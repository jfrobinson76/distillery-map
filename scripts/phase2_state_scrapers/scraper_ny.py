"""
NY — New York SLA license data.

NY State Liquor Authority publishes license data on NY Open Data:
https://data.ny.gov/Economic-Development/Liquor-Authority-Quarterly-List-of-Active-Licenses/

Distillery license types in NY:
- "FARM DISTILLERY" — craft distillery license
- "DISTILLERY" — full distillery license

Uses Socrata Open Data API (no key required for public datasets).
"""

import logging
import sqlite3
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}

# NY Open Data — SLA active licenses (Socrata)
# Dataset: "Liquor Authority Quarterly List of Active Licenses"
NY_OPENDATA_URL = "https://data.ny.gov/resource/wg8y-fzsb.json"

DS_TYPES = {"FARM DISTILLERY", "DISTILLERY", "MICRO DISTILLERY"}


def fetch_ny_licenses() -> list[dict]:
    results = []
    offset = 0
    limit = 1000

    while True:
        try:
            resp = requests.get(
                NY_OPENDATA_URL,
                params={
                    "$limit": limit,
                    "$offset": offset,
                    "$where": "license_type_name in ('FARM DISTILLERY', 'DISTILLERY', 'MICRO DISTILLERY')",
                },
                headers=HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break

            for row in batch:
                results.append({
                    "license_number": row.get("serial_number", row.get("license_serial", "")),
                    "business_name": row.get("doing_business_as", row.get("license_class_code", "")),
                    "city": row.get("premise_city", ""),
                    "zip": row.get("premise_zip", ""),
                    "status": row.get("license_type_name", ""),
                })

            if len(batch) < limit:
                break
            offset += limit
            time.sleep(1)

        except Exception as exc:
            log.warning("NY Open Data request failed at offset %d: %s", offset, exc)
            break

    log.info("Fetched %d NY distillery licenses from Open Data", len(results))
    return results


def match_to_db(con: sqlite3.Connection, licenses: list[dict]) -> int:
    from rapidfuzz import fuzz

    ny_entities = con.execute(
        """SELECT e.source_id, e.name FROM entities e
           JOIN locations l ON l.entity_source_id = e.source_id
           WHERE l.state = 'NY'"""
    ).fetchall()

    if not ny_entities:
        log.info("No NY entities in DB")
        return 0

    updated = 0
    for lic in licenses:
        lic_name = lic.get("business_name", "").strip()
        if not lic_name:
            continue

        best_sid, best_score = None, 0
        for sid, ename in ny_entities:
            score = fuzz.token_sort_ratio(lic_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory SET state_license_number = ?, state_license_source = 'NY_SLA'
                   WHERE entity_source_id = ?""",
                (lic["license_number"], best_sid),
            )
            updated += 1

    return updated


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run load_phase1_matched.py first")
        return

    licenses = fetch_ny_licenses()
    if not licenses:
        log.info("No NY license data retrieved — skipping")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    updated = match_to_db(con, licenses)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("NY_SLA", updated, f"{len(licenses)} licenses fetched, {updated} matched"),
    )
    con.commit()
    con.close()
    log.info("NY complete: %d/%d matched", updated, len(licenses))


if __name__ == "__main__":
    main()
