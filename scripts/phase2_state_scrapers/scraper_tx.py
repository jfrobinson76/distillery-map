"""
TX — Texas TABC license data.

TABC publishes licensed premises as downloadable data.
Distillery license type: "DS" (Distillery Permit), "DB" (Distillers and Rectifiers Permit)
Public data: https://www.tabc.texas.gov/licensing-permitting/

Uses TABC's bulk/open data download where available.
"""

import csv
import io
import logging
import sqlite3
import time
import zipfile
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}

# TABC open data — licensed premises
# They also publish via Texas Open Data Portal: https://data.texas.gov/
TABC_OPENDATA_URL = "https://data.texas.gov/resource/6s3c-3axi.json"  # TABC licensed premises
TABC_OPENDATA_FALLBACK = "https://www.tabc.texas.gov/wp-content/uploads/licensed_locations.csv"

# Distillery permit types
DS_TYPES = {"DS", "DB", "MB", "MBRP"}  # Distillery, Distillers & Rectifiers, Micro-Brewery (for craft crossovers)


def fetch_tabc_opendata() -> list[dict]:
    results = []
    offset = 0
    limit = 1000

    while True:
        try:
            resp = requests.get(
                TABC_OPENDATA_URL,
                params={"$limit": limit, "$offset": offset},
                headers=HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break

            for row in batch:
                lic_type = row.get("license_type", row.get("permit_type", "")).upper()
                if lic_type in DS_TYPES:
                    results.append({
                        "license_number": row.get("license_number", row.get("license_num", "")),
                        "business_name": row.get("business_name", row.get("dba_name", row.get("name", ""))),
                        "city": row.get("city", ""),
                        "zip": row.get("zip_code", row.get("zip", "")),
                        "status": row.get("license_status", row.get("status", "")),
                    })

            if len(batch) < limit:
                break
            offset += limit
            time.sleep(1)

        except Exception as exc:
            log.warning("TABC Open Data request failed at offset %d: %s", offset, exc)
            break

    log.info("Fetched %d TX distillery licenses from Open Data", len(results))
    return results


def fetch_tabc_fallback() -> list[dict]:
    try:
        resp = requests.get(TABC_OPENDATA_FALLBACK, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        text = resp.content.decode("utf-8", errors="replace")
        results = []
        for row in csv.DictReader(io.StringIO(text)):
            norm = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items()}
            lic_type = norm.get("license_type", norm.get("permit_type", "")).upper()
            if lic_type in DS_TYPES:
                results.append({
                    "license_number": norm.get("license_number", norm.get("license_num", "")),
                    "business_name": norm.get("business_name", norm.get("dba_name", "")),
                    "city": norm.get("city", ""),
                    "zip": norm.get("zip_code", ""),
                    "status": norm.get("status", ""),
                })
        log.info("Fetched %d TX licenses from fallback CSV", len(results))
        return results
    except Exception as exc:
        log.warning("TABC fallback failed: %s", exc)
        return []


def match_to_db(con: sqlite3.Connection, licenses: list[dict]) -> int:
    from rapidfuzz import fuzz

    tx_entities = con.execute(
        """SELECT e.source_id, e.name FROM entities e
           JOIN locations l ON l.entity_source_id = e.source_id
           WHERE l.state = 'TX'"""
    ).fetchall()

    if not tx_entities:
        log.info("No TX entities in DB")
        return 0

    updated = 0
    for lic in licenses:
        lic_name = lic.get("business_name", "").strip()
        if not lic_name:
            continue

        best_sid, best_score = None, 0
        for sid, ename in tx_entities:
            score = fuzz.token_sort_ratio(lic_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory SET state_license_number = ?, state_license_source = 'TX_TABC'
                   WHERE entity_source_id = ?""",
                (lic["license_number"], best_sid),
            )
            updated += 1

    return updated


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run load_phase1_matched.py first")
        return

    licenses = fetch_tabc_opendata()
    if not licenses:
        log.info("Open Data returned nothing — trying fallback")
        licenses = fetch_tabc_fallback()

    if not licenses:
        log.info("No TX license data retrieved — skipping")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    updated = match_to_db(con, licenses)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("TX_TABC", updated, f"{len(licenses)} licenses fetched, {updated} matched"),
    )
    con.commit()
    con.close()
    log.info("TX complete: %d/%d matched", updated, len(licenses))


if __name__ == "__main__":
    main()
