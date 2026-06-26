"""
Phase 2 — Loader: matched_high_confidence.csv + matched_review.csv → SQLite DB.

Inserts entities, locations, and regulatory records.
Idempotent via INSERT OR REPLACE / INSERT OR IGNORE.
"""

import csv
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
HIGH_CONF_PATH = REPO_ROOT / "data" / "enriched" / "matched_high_confidence.csv"
REVIEW_PATH = REPO_ROOT / "data" / "enriched" / "matched_review.csv"


def load_file(con: sqlite3.Connection, path: Path, review_needed: int) -> int:
    if not path.exists():
        log.warning("File not found: %s — skipping", path)
        return 0

    rows = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            source_id = row.get("source_id", "").strip()
            if not source_id:
                continue

            con.execute(
                """INSERT OR REPLACE INTO entities
                   (source_id, name, lat, lng, website, geojson_source, review_needed)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    source_id,
                    row.get("name", "").strip(),
                    _float(row.get("lat")),
                    _float(row.get("lng")),
                    row.get("website", "").strip() or None,
                    row.get("geojson_source", "").strip() or None,
                    review_needed,
                ),
            )

            con.execute(
                """INSERT OR REPLACE INTO locations
                   (entity_source_id, address, city, state, zip)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    source_id,
                    row.get("address", "").strip() or None,
                    row.get("city", "").strip() or None,
                    row.get("state", "").strip() or None,
                    None,
                ),
            )

            con.execute(
                """INSERT OR REPLACE INTO regulatory
                   (entity_source_id, ttb_permit_number, ttb_business_name, ttb_dba_name,
                    ttb_status, ttb_issue_date, ttb_permit_type, match_score, match_method)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source_id,
                    row.get("ttb_permit_number", "").strip() or None,
                    row.get("ttb_business_name", "").strip() or None,
                    row.get("ttb_dba_name", "").strip() or None,
                    row.get("ttb_status", "").strip() or None,
                    row.get("ttb_issue_date", "").strip() or None,
                    row.get("ttb_permit_type", "").strip() or None,
                    _float(row.get("match_score")),
                    row.get("match_method", "").strip() or None,
                ),
            )
            rows += 1

    return rows


def _float(val) -> float | None:
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    schema = (REPO_ROOT / "scripts" / "phase2_schema.sql").read_text()
    con.executescript(schema)
    con.commit()

    log.info("Loading matched_high_confidence.csv …")
    added_hc = load_file(con, HIGH_CONF_PATH, review_needed=0)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_added) VALUES (?, ?)",
        ("phase1_matched_high_confidence", added_hc),
    )
    con.commit()
    log.info("  %d rows inserted (high confidence)", added_hc)

    log.info("Loading matched_review.csv …")
    added_rv = load_file(con, REVIEW_PATH, review_needed=1)
    con.execute(
        "INSERT INTO enrichment_log (source, rows_added) VALUES (?, ?)",
        ("phase1_matched_review", added_rv),
    )
    con.commit()
    log.info("  %d rows inserted (review)", added_rv)

    total = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    log.info("Entities in DB: %d", total)
    con.close()


if __name__ == "__main__":
    main()
