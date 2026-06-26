"""
Phase 2 — Final report: summarise DB state after overnight run.

Output: data/enriched/enrichment_report_phase2.txt
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
REPORT_PATH = REPO_ROOT / "data" / "enriched" / "enrichment_report_phase2.txt"


def main() -> None:
    if not DB_PATH.exists():
        print("DB not found — pipeline may have failed")
        return

    con = sqlite3.connect(DB_PATH)

    total_entities = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    reviewed = con.execute("SELECT COUNT(*) FROM entities WHERE review_needed = 1").fetchone()[0]
    with_ttb = con.execute(
        "SELECT COUNT(*) FROM regulatory WHERE ttb_permit_number IS NOT NULL"
    ).fetchone()[0]
    with_state_lic = con.execute(
        "SELECT COUNT(*) FROM regulatory WHERE state_license_number IS NOT NULL"
    ).fetchone()[0]
    products_total = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    linked_products = con.execute(
        "SELECT COUNT(*) FROM products WHERE entity_source_id IS NOT NULL"
    ).fetchone()[0]

    by_state = con.execute(
        """SELECT l.state, COUNT(*) AS cnt
           FROM locations l
           WHERE l.state IS NOT NULL AND l.state != ''
           GROUP BY l.state ORDER BY cnt DESC"""
    ).fetchall()

    state_licensed = con.execute(
        """SELECT r.state_license_source, COUNT(*) AS cnt
           FROM regulatory r
           WHERE r.state_license_number IS NOT NULL
           GROUP BY r.state_license_source ORDER BY cnt DESC"""
    ).fetchall()

    log_entries = con.execute(
        "SELECT source, run_date, rows_added, rows_updated, notes FROM enrichment_log ORDER BY id"
    ).fetchall()

    con.close()

    lines = [
        "STILLBOUND INTELLIGENCE LAYER — Phase 2 Report",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "DATABASE SUMMARY",
        f"  Total entities:                {total_entities}",
        f"  High-confidence matched:       {total_entities - reviewed}",
        f"  Review-flagged (70-84 score):  {reviewed}",
        f"  With TTB permit number:        {with_ttb}",
        f"  With state license number:     {with_state_lic}",
        f"  Products in DB:                {products_total}",
        f"  Products linked to entity:     {linked_products}",
        "",
        "ENTITIES BY STATE (top 20)",
    ]

    for state, cnt in by_state[:20]:
        lines.append(f"  {state or '??':<6} {cnt}")

    lines += [
        "",
        "STATE LICENSE ENRICHMENT",
    ]
    if state_licensed:
        for source, cnt in state_licensed:
            lines.append(f"  {source:<15} {cnt} matched")
    else:
        lines.append("  (none — state scrapers may have found no bulk data)")

    lines += [
        "",
        "PIPELINE LOG",
    ]
    for source, run_date, rows_added, rows_updated, notes in log_entries:
        added = f"+{rows_added}" if rows_added else ""
        updated = f"~{rows_updated}" if rows_updated else ""
        marker = " ".join(filter(None, [added, updated]))
        lines.append(f"  {source:<45} {marker}")
        if notes:
            lines.append(f"    → {notes}")

    lines += [
        "",
        "NEXT STEP (Phase 3)",
        "  1. Review data/enriched/matched_review.csv (borderline matches)",
        "  2. Migrate SQLite → Supabase eu-west-1 for remote access",
        "  3. Wire distillerymap.org claim form → contacts table",
        "  4. Connect to CaskIQ as TAM source for outreach module",
        "",
        f"DB file: {DB_PATH}",
        f"API:     cd {REPO_ROOT} && uvicorn api.main:app --reload",
    ]

    report = "\n".join(lines)
    REPORT_PATH.write_text(report)
    print(report)
    print(f"\nReport written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
