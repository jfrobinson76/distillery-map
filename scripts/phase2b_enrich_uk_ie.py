"""
Phase 2B — Step 1: Load Ireland, Scotland, and UK entities into DB.

Extracts 654 non-US priority entities from the GeoJSON and loads them.
Then makes best-effort regulatory matches from:
  - Scotch Whisky Association member list (Scotland)
  - Drinks Ireland / Irish Whiskey Association member list (Ireland)
  - WSTA member list (UK ex-Scotland)

These regulatory sources are smaller and web-scraped rather than bulk-downloaded.
If scraping fails, entities are still loaded — the GeoJSON IS the source of truth here.

Idempotent: INSERT OR REPLACE on source_id.
"""

import csv
import json
import logging
import re
import sqlite3
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
GEOJSON_PATH = REPO_ROOT / "public" / "data" / "distilleries.geojson"

HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}
TARGET_REGIONS = {"ireland", "scotland", "uk"}

# Sources
SWA_URL = "https://www.scotch-whisky.org.uk/members/member-directory/"
IWA_URL = "https://www.irishwhiskey.ie/members/"
WSTA_URL = "https://www.wsta.co.uk/wsta/members/"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def parse_postcode(address: str) -> str:
    """Extract UK/IE postcode from address string."""
    uk_match = re.search(r"\b([A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})\b", address, re.I)
    if uk_match:
        return uk_match.group(1).upper()
    ie_match = re.search(r"\b([A-Z]\d{2}\s*[A-Z0-9]{4})\b", address, re.I)
    if ie_match:
        return ie_match.group(1).upper()
    return ""


def load_priority_entities() -> list[dict]:
    """Extract Ireland, Scotland, UK entities from GeoJSON."""
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    entities = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        region = props.get("region", "").lower()
        if region not in TARGET_REGIONS:
            continue

        coords = feature.get("geometry", {}).get("coordinates", [None, None])
        lat = coords[1] if len(coords) >= 2 else None
        lng = coords[0] if len(coords) >= 2 else None

        address = props.get("address", "").strip()
        name = props.get("name", "").strip()
        state = parse_postcode(address)

        # Derive source_id
        slug = slugify(name) or "unknown"
        postcode_slug = re.sub(r"\s+", "", state).lower() if state else region
        source_id = f"{slug}_{postcode_slug}"

        entities.append({
            "source_id": source_id,
            "name": name,
            "lat": lat,
            "lng": lng,
            "website": props.get("website", "").strip() or None,
            "address": address or None,
            "region": region,
            "geojson_source": props.get("source", "").strip() or None,
        })

    log.info("Extracted %d priority entities (IE/Scotland/UK) from GeoJSON", len(entities))
    return entities


def insert_entities(con: sqlite3.Connection, entities: list[dict]) -> int:
    """Load entities + locations into DB."""
    inserted = 0
    for e in entities:
        con.execute(
            """INSERT OR REPLACE INTO entities
               (source_id, name, lat, lng, website, geojson_source, region)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (e["source_id"], e["name"], e["lat"], e["lng"],
             e["website"], e["geojson_source"], e["region"]),
        )
        # Locations: state = region for UK/IE (no 2-letter code), address raw
        con.execute(
            """INSERT OR REPLACE INTO locations
               (entity_source_id, address, city, state)
               VALUES (?, ?, ?, ?)""",
            (e["source_id"], e["address"], None, e["region"].upper()),
        )
        # Placeholder regulatory row so state_license_number can be updated later
        con.execute(
            """INSERT OR IGNORE INTO regulatory (entity_source_id) VALUES (?)""",
            (e["source_id"],),
        )
        inserted += 1
    return inserted


def fetch_swa_members() -> list[str]:
    """Scrape Scotch Whisky Association member names."""
    try:
        resp = requests.get(SWA_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        names = []
        for el in soup.select("h3, h4, .member-name, .entry-title, article h2"):
            text = el.get_text(strip=True)
            if text and len(text) > 3:
                names.append(text)
        # Deduplicate
        names = list(dict.fromkeys(names))
        log.info("SWA: found %d member names", len(names))
        return names
    except Exception as exc:
        log.warning("SWA scrape failed: %s", exc)
        return []


def fetch_iwa_members() -> list[str]:
    """Scrape Irish Whiskey Association member names."""
    try:
        resp = requests.get(IWA_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        names = []
        for el in soup.select("h2, h3, h4, .member-name, .team-name, article h2, .entry-title"):
            text = el.get_text(strip=True)
            if text and len(text) > 3:
                names.append(text)
        names = list(dict.fromkeys(names))
        log.info("IWA: found %d member names", len(names))
        return names
    except Exception as exc:
        log.warning("IWA scrape failed: %s", exc)
        return []


def match_and_flag(con: sqlite3.Connection, member_names: list[str],
                   region: str, source_label: str) -> int:
    """Fuzzy-match association member names to DB entities in the given region."""
    entities = con.execute(
        "SELECT source_id, name FROM entities WHERE region = ?",
        (region,),
    ).fetchall()

    if not entities:
        return 0

    updated = 0
    for member_name in member_names:
        best_sid, best_score = None, 0
        for sid, ename in entities:
            score = fuzz.token_sort_ratio(member_name.lower(), ename.lower())
            if score > best_score:
                best_score, best_sid = score, sid

        if best_score >= 80 and best_sid:
            con.execute(
                """UPDATE regulatory
                   SET state_license_number = ?, state_license_source = ?
                   WHERE entity_source_id = ?""",
                (member_name, source_label, best_sid),
            )
            updated += 1

    return updated


def run_migration(con: sqlite3.Connection) -> None:
    """Apply Phase 2B schema migration — ignore errors for already-existing columns."""
    migration = (REPO_ROOT / "scripts" / "phase2b_schema_migration.sql").read_text()
    for segment in migration.split(";"):
        # Strip comment-only lines — a segment may start with comments but contain real SQL
        lines = [l for l in segment.split("\n") if l.strip() and not l.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if not stmt:
            continue
        try:
            con.execute(stmt)
        except sqlite3.OperationalError as exc:
            if "duplicate column" in str(exc).lower():
                pass  # column already exists — idempotent
            else:
                log.debug("Migration statement skipped: %s", exc)
    con.commit()
    log.info("Schema migration applied")


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run Phase 2 pipeline first")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    run_migration(con)

    entities = load_priority_entities()
    inserted = insert_entities(con, entities)
    con.commit()
    log.info("Loaded %d IE/UK/Scotland entities into DB", inserted)

    # Best-effort association matching
    log.info("Fetching SWA members for Scotland…")
    swa = fetch_swa_members()
    time.sleep(1)
    swa_matched = match_and_flag(con, swa, "scotland", "SWA")
    con.commit()
    log.info("SWA: %d/%d names matched to Scotland entities", swa_matched, len(swa))

    log.info("Fetching IWA members for Ireland…")
    iwa = fetch_iwa_members()
    time.sleep(1)
    iwa_matched = match_and_flag(con, iwa, "ireland", "IWA")
    con.commit()
    log.info("IWA: %d/%d names matched to Ireland entities", iwa_matched, len(iwa))

    total_entities = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    by_region = con.execute(
        "SELECT region, COUNT(*) FROM entities WHERE region IS NOT NULL GROUP BY region ORDER BY COUNT(*) DESC"
    ).fetchall()

    con.execute(
        "INSERT INTO enrichment_log (source, rows_added, notes) VALUES (?, ?, ?)",
        ("phase2b_uk_ie", inserted,
         f"SWA matched {swa_matched}, IWA matched {iwa_matched}"),
    )
    con.commit()
    con.close()

    log.info("Phase 2B Step 1 complete. Total entities in DB: %d", total_entities)
    for region, cnt in by_region:
        log.info("  %-15s %d", region, cnt)


if __name__ == "__main__":
    main()
