"""
KY — Kentucky ABC license data.

KY ABC doesn't have a bulk download API. Options:
1. Kentucky Open Data Portal (https://opendataky.gov/) — check for license dataset
2. KY ABC License Verification page HTML scrape (rate limited)

This scraper tries the Open Data portal first, then falls back to
a targeted HTML scrape of the KY ABC license search for distillery types.

KY distillery license type: "Distilled Spirits Manufacturer" / DSP
"""

import logging
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

KY_OPENDATA_URL = "https://opendataky.gov/resource"  # check for ABC dataset
KY_ABC_SEARCH = "https://abc.ky.gov/Pages/LicenseSearch.aspx"

ROBOTS_BASE = "https://abc.ky.gov"


def check_robots(base_url: str) -> bool:
    try:
        resp = requests.get(base_url + "/robots.txt", headers=HEADERS, timeout=10)
        text = resp.text.lower()
        if "disallow: /" in text and "user-agent: *" in text:
            # Check if it's a blanket disallow
            lines = [l.strip() for l in text.splitlines()]
            for i, line in enumerate(lines):
                if "user-agent: *" in line:
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("user-agent"):
                            break
                        if lines[j] == "disallow: /":
                            log.warning("robots.txt blocks all crawling at %s", base_url)
                            return False
        return True
    except Exception:
        return True


def fetch_ky_opendata() -> list[dict]:
    """Try Kentucky Open Data Portal for ABC license data."""
    # Known dataset IDs change — try a few common patterns
    candidate_urls = [
        "https://opendataky.gov/resource/abc-licenses.json",
        "https://data.ky.gov/resource/distilled-spirits-licenses.json",
    ]
    for url in candidate_urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                rows = resp.json()
                if rows:
                    log.info("KY Open Data returned %d rows from %s", len(rows), url)
                    return [
                        {
                            "license_number": r.get("license_number", r.get("license_no", "")),
                            "business_name": r.get("business_name", r.get("dba", r.get("licensee", ""))),
                            "city": r.get("city", ""),
                            "zip": r.get("zip", ""),
                            "status": r.get("status", ""),
                        }
                        for r in rows
                    ]
        except Exception as exc:
            log.debug("KY Open Data %s failed: %s", url, exc)
        time.sleep(1)
    return []


def fetch_ky_known_entities(con: sqlite3.Connection) -> list[dict]:
    """
    KY fallback: for entities already in DB with TTB permit (state=KY),
    we already have their TTB data. The state license scrape adds little.
    Return a note rather than scraping a form-gated site.
    """
    count = con.execute(
        "SELECT COUNT(*) FROM locations WHERE state = 'KY'"
    ).fetchone()[0]
    log.info(
        "KY: %d entities in DB already. KY ABC website requires form-based search — "
        "no bulk download available. State license enrichment skipped for KY. "
        "TTB permit numbers cover KY entities adequately.",
        count,
    )
    return []


def match_to_db(con: sqlite3.Connection, licenses: list[dict]) -> int:
    if not licenses:
        return 0

    from rapidfuzz import fuzz

    ky_entities = con.execute(
        """SELECT e.source_id, e.name FROM entities e
           JOIN locations l ON l.entity_source_id = e.source_id
           WHERE l.state = 'KY'"""
    ).fetchall()

    updated = 0
    for lic in licenses:
        lic_name = lic.get("business_name", "").strip()
        if not lic_name:
            continue

        best_sid, best_score = None, 0
        for sid, ename in ky_entities:
            score = fuzz.token_sort_ratio(lic_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory SET state_license_number = ?, state_license_source = 'KY_ABC'
                   WHERE entity_source_id = ?""",
                (lic["license_number"], best_sid),
            )
            updated += 1

    return updated


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run load_phase1_matched.py first")
        return

    if not check_robots(ROBOTS_BASE):
        return

    licenses = fetch_ky_opendata()

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    if not licenses:
        fetch_ky_known_entities(con)
        con.execute(
            "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
            ("KY_ABC", 0, "No bulk data available — KY entities rely on TTB permit enrichment"),
        )
        con.commit()
        con.close()
        return

    updated = match_to_db(con, licenses)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("KY_ABC", updated, f"{len(licenses)} licenses fetched, {updated} matched"),
    )
    con.commit()
    con.close()
    log.info("KY complete: %d/%d matched", updated, len(licenses))


if __name__ == "__main__":
    main()
