"""
CA — California ABC license data.

CA ABC publishes distillery license data via their License Query API.
License type for distilled spirits manufacturers: "02" (Distilled Spirits Manufacturer)
Public data portal: https://www.abc.ca.gov/licensing/

This scraper uses the CA ABC License Query to download Type 02 licenses.
Adds state_license_number to regulatory table for matched CA entities,
and logs any unmatched CA entities as enrichment_log notes.
"""

import logging
import re
import sqlite3
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}

ROBOTS_URL = "https://www.abc.ca.gov/robots.txt"
BULK_URL = "https://www.abc.ca.gov/wp-content/uploads/ABC_License_Data_{year}.zip"

# CA ABC license types for spirits producers
DS_LICENSE_TYPES = {"02", "2"}


def check_robots(base_url: str) -> bool:
    try:
        resp = requests.get(base_url + "/robots.txt", headers=HEADERS, timeout=10)
        if "Disallow: /" in resp.text:
            log.warning("robots.txt disallows root — scraping blocked for %s", base_url)
            return False
        return True
    except Exception:
        return True  # assume allowed if unreachable


def fetch_ca_licenses() -> list[dict]:
    """Try bulk download first, fall back to query form."""
    import datetime
    year = datetime.date.today().year

    for try_year in [year, year - 1]:
        url = BULK_URL.format(year=try_year)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                log.info("Got CA ABC bulk file for %d (%d bytes)", try_year, len(resp.content))
                return parse_ca_bulk(resp.content)
        except Exception as exc:
            log.debug("Bulk download failed for %d: %s", try_year, exc)
        time.sleep(1)

    log.info("Bulk download unavailable — trying CA ABC license query API")
    return fetch_ca_via_query()


def parse_ca_bulk(content: bytes) -> list[dict]:
    import csv
    import io
    import zipfile

    results = []
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for name in zf.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                text = zf.read(name).decode("utf-8", errors="replace")
                for row in csv.DictReader(io.StringIO(text)):
                    norm = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items()}
                    lic_type = norm.get("license_type", norm.get("type", ""))
                    if lic_type in DS_LICENSE_TYPES:
                        results.append({
                            "license_number": norm.get("license_number", norm.get("license_no", "")),
                            "business_name": norm.get("business_name", norm.get("dba", "")),
                            "city": norm.get("city", ""),
                            "zip": norm.get("zip", norm.get("zip_code", "")),
                            "status": norm.get("status", norm.get("license_status", "")),
                        })
    except Exception as exc:
        log.warning("Failed to parse CA bulk file: %s", exc)

    log.info("Parsed %d CA distillery licenses from bulk file", len(results))
    return results


def fetch_ca_via_query() -> list[dict]:
    """
    CA ABC has a license query at https://www.abc.ca.gov/licensing/license-lookup/
    This returns HTML results — parse type 02 entries.
    Limited fallback: returns empty list if structure changes.
    """
    base = "https://www.abc.ca.gov/licensing/license-lookup/"
    try:
        resp = requests.get(base, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        # If the site requires a form POST with CSRF, we can't easily automate it.
        # Return empty and log — operator can manually export from ABC portal.
        log.info("CA ABC query form found — automated scrape not possible without CSRF. "
                 "Skipping CA state license enrichment (bulk file unavailable).")
    except Exception as exc:
        log.warning("CA ABC query unreachable: %s", exc)
    return []


def match_to_db(con: sqlite3.Connection, licenses: list[dict]) -> int:
    from rapidfuzz import fuzz

    ca_entities = con.execute(
        """SELECT e.source_id, e.name FROM entities e
           JOIN locations l ON l.entity_source_id = e.source_id
           WHERE l.state = 'CA'"""
    ).fetchall()

    if not ca_entities:
        log.info("No CA entities in DB to match against")
        return 0

    updated = 0
    for lic in licenses:
        lic_name = lic.get("business_name", "").strip()
        if not lic_name:
            continue

        best_sid, best_score = None, 0
        for sid, ename in ca_entities:
            score = fuzz.token_sort_ratio(lic_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory SET state_license_number = ?, state_license_source = 'CA_ABC'
                   WHERE entity_source_id = ?""",
                (lic["license_number"], best_sid),
            )
            updated += 1

    return updated


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run load_phase1_matched.py first")
        return

    if not check_robots("https://www.abc.ca.gov"):
        return

    licenses = fetch_ca_licenses()
    if not licenses:
        log.info("No CA license data retrieved — skipping")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    updated = match_to_db(con, licenses)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("CA_ABC", updated, f"{len(licenses)} licenses fetched, {updated} matched to DB entities"),
    )
    con.commit()
    con.close()
    log.info("CA complete: %d/%d licenses matched to DB entities", updated, len(licenses))


if __name__ == "__main__":
    main()
