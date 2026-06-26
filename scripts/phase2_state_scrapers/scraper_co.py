"""
CO — Colorado liquor licensing data.

Colorado Liquor Enforcement Division (LED) publishes license data.
Open Data: https://data.colorado.gov/dataset/Active-License-Data/

Distillery license types in CO:
- "Distillery Pub"
- "Manufacturer's License" (spirits)

Uses Colorado Open Data Portal (Socrata API).
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

# Colorado Open Data — LED Active Licenses
CO_OPENDATA_URL = "https://data.colorado.gov/resource/active-license-data.json"
CO_OPENDATA_ALT = "https://data.colorado.gov/resource/qb9p-5dqp.json"  # known dataset ID

DS_TYPE_KEYWORDS = {"distill", "spirits", "manufacturer"}


def is_distillery_license(license_type: str) -> bool:
    lt = license_type.lower()
    return any(kw in lt for kw in DS_TYPE_KEYWORDS)


def fetch_co_licenses() -> list[dict]:
    results = []
    urls_to_try = [CO_OPENDATA_URL, CO_OPENDATA_ALT]

    for base_url in urls_to_try:
        offset = 0
        limit = 1000
        url_results = []

        while True:
            try:
                resp = requests.get(
                    base_url,
                    params={"$limit": limit, "$offset": offset},
                    headers=HEADERS,
                    timeout=30,
                )
                resp.raise_for_status()
                batch = resp.json()
                if not batch:
                    break

                for row in batch:
                    lic_type = row.get("license_type", row.get("licensetype", row.get("type", "")))
                    if is_distillery_license(str(lic_type)):
                        url_results.append({
                            "license_number": row.get("license_number", row.get("license_no", row.get("licensenum", ""))),
                            "business_name": row.get("doing_business_as", row.get("business_name", row.get("dba", ""))),
                            "city": row.get("city", row.get("premise_city", "")),
                            "zip": row.get("zip", row.get("zip_code", "")),
                            "status": str(lic_type),
                        })

                if len(batch) < limit:
                    break
                offset += limit
                time.sleep(1)

            except Exception as exc:
                log.warning("CO Open Data request at %s offset %d failed: %s", base_url, offset, exc)
                break

        if url_results:
            log.info("Fetched %d CO distillery licenses from %s", len(url_results), base_url)
            results = url_results
            break

    if not results:
        log.info("CO Open Data returned no results — CO license enrichment skipped")

    return results


def match_to_db(con: sqlite3.Connection, licenses: list[dict]) -> int:
    from rapidfuzz import fuzz

    co_entities = con.execute(
        """SELECT e.source_id, e.name FROM entities e
           JOIN locations l ON l.entity_source_id = e.source_id
           WHERE l.state = 'CO'"""
    ).fetchall()

    if not co_entities:
        log.info("No CO entities in DB")
        return 0

    updated = 0
    for lic in licenses:
        lic_name = lic.get("business_name", "").strip()
        if not lic_name:
            continue

        best_sid, best_score = None, 0
        for sid, ename in co_entities:
            score = fuzz.token_sort_ratio(lic_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory SET state_license_number = ?, state_license_source = 'CO_LED'
                   WHERE entity_source_id = ?""",
                (lic["license_number"], best_sid),
            )
            updated += 1

    return updated


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run load_phase1_matched.py first")
        return

    licenses = fetch_co_licenses()
    if not licenses:
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    updated = match_to_db(con, licenses)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("CO_LED", updated, f"{len(licenses)} licenses fetched, {updated} matched"),
    )
    con.commit()
    con.close()
    log.info("CO complete: %d/%d matched", updated, len(licenses))


if __name__ == "__main__":
    main()
