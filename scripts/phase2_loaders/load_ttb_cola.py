"""
Phase 2 — Loader: TTB COLA registry → products table.

TTB publishes COLA (Certificate of Label Approval) data as bulk downloads.
Bulk file URL: https://www.ttb.gov/images/pdfs/foia/cola-approvals-by-year/
We fetch the most recent year(s) of distilled spirits COLAs and link them
to entities in the DB via ttb_permit_number.

Falls back gracefully if TTB changes URLs — logs and moves on.
Rate limit: 1 req/sec. User-Agent set.
"""

import csv
import io
import logging
import sqlite3
import time
import zipfile
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"

TTB_COLA_INDEX = "https://www.ttb.gov/foia/cola-approvals-by-year"
HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}

# Only fetch recent years — craft spirits boom post-2015
CUTOFF_YEAR = 2015
# Only load distilled spirits product classes
DS_CLASS_KEYWORDS = {"distilled", "spirit", "whiskey", "whisky", "bourbon", "vodka",
                     "gin", "rum", "brandy", "tequila", "mezcal", "aquavit", "absinthe"}


def is_distilled_spirit(class_type: str) -> bool:
    ct = class_type.lower()
    return any(kw in ct for kw in DS_CLASS_KEYWORDS)


def fetch_cola_links() -> list[tuple[int, str]]:
    """Return list of (year, url) for COLA CSV/ZIP downloads >= CUTOFF_YEAR."""
    try:
        resp = requests.get(TTB_COLA_INDEX, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        log.warning("Could not reach TTB COLA index: %s", exc)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not any(ext in href.lower() for ext in (".csv", ".zip", ".xls", ".xlsx")):
            continue
        for year in range(CUTOFF_YEAR, 2030):
            if str(year) in href:
                full = href if href.startswith("http") else "https://www.ttb.gov" + href
                links.append((year, full))
                break

    links.sort(key=lambda x: x[0], reverse=True)
    log.info("Found %d COLA download links >= %d", len(links), CUTOFF_YEAR)
    return links


def load_csv_rows(content: bytes, filename: str) -> list[dict]:
    """Parse CSV bytes into list of dicts, normalising column names."""
    try:
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        # Normalise headers
        rows = []
        for row in reader:
            normalised = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items()}
            rows.append(normalised)
        return rows
    except Exception as exc:
        log.warning("Failed to parse %s: %s", filename, exc)
        return []


def extract_zip(content: bytes) -> list[tuple[str, bytes]]:
    """Return list of (filename, bytes) for CSVs inside a zip."""
    results = []
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    results.append((name, zf.read(name)))
    except Exception as exc:
        log.warning("Failed to extract zip: %s", exc)
    return results


def infer_cola_fields(row: dict) -> dict | None:
    """Map TTB COLA CSV columns to our schema. Returns None if not distilled spirits."""
    class_type = (
        row.get("class_type_description")
        or row.get("class/type_description")
        or row.get("class")
        or row.get("product_type")
        or ""
    )
    if not is_distilled_spirit(class_type):
        return None

    return {
        "ttb_permit_number": (
            row.get("permit_number")
            or row.get("basic_permit_number")
            or row.get("dsp_number")
            or ""
        ).strip(),
        "cola_id": (row.get("cola_id") or row.get("id") or row.get("ttb_id") or "").strip(),
        "brand_name": (row.get("brand_name") or row.get("brand") or "").strip(),
        "product_name": (row.get("product_name") or row.get("name") or "").strip(),
        "class_type": class_type.strip(),
        "approval_date": (
            row.get("approved_date")
            or row.get("approval_date")
            or row.get("date_approved")
            or ""
        ).strip(),
        "fanciful_name": (row.get("fanciful_name") or "").strip() or None,
    }


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found at %s — run load_phase1_matched.py first", DB_PATH)
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    # Build set of known TTB permit numbers in DB for fast linking
    known_permits = {
        r[0]
        for r in con.execute("SELECT ttb_permit_number FROM regulatory WHERE ttb_permit_number IS NOT NULL")
    }
    log.info("%d TTB permit numbers in DB for linking", len(known_permits))

    links = fetch_cola_links()
    if not links:
        log.warning("No COLA links found — products table will remain empty")
        con.close()
        return

    total_inserted = 0

    for year, url in links:
        log.info("Fetching COLA data for year %d from %s …", year, url)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            resp.raise_for_status()
            content = resp.content
            time.sleep(1)
        except Exception as exc:
            log.warning("Failed to download %s: %s", url, exc)
            continue

        # Handle zip or direct CSV
        file_batches: list[tuple[str, bytes]] = []
        if url.lower().endswith(".zip") or b"PK\x03\x04" in content[:4]:
            file_batches = extract_zip(content)
        else:
            file_batches = [(url.split("/")[-1], content)]

        for filename, file_bytes in file_batches:
            rows = load_csv_rows(file_bytes, filename)
            log.info("  %s: %d raw rows", filename, len(rows))

            batch_inserted = 0
            for raw in rows:
                mapped = infer_cola_fields(raw)
                if not mapped or not mapped["cola_id"]:
                    continue

                entity_source_id = None
                if mapped["ttb_permit_number"] and mapped["ttb_permit_number"] in known_permits:
                    result = con.execute(
                        "SELECT entity_source_id FROM regulatory WHERE ttb_permit_number = ?",
                        (mapped["ttb_permit_number"],),
                    ).fetchone()
                    if result:
                        entity_source_id = result[0]

                try:
                    con.execute(
                        """INSERT OR IGNORE INTO products
                           (entity_source_id, ttb_permit_number, cola_id, brand_name,
                            product_name, class_type, approval_date, fanciful_name)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            entity_source_id,
                            mapped["ttb_permit_number"] or None,
                            mapped["cola_id"],
                            mapped["brand_name"] or None,
                            mapped["product_name"] or None,
                            mapped["class_type"] or None,
                            mapped["approval_date"] or None,
                            mapped["fanciful_name"],
                        ),
                    )
                    batch_inserted += 1
                except sqlite3.IntegrityError:
                    pass

            con.commit()
            total_inserted += batch_inserted
            log.info("  Inserted %d distilled spirits products from %s", batch_inserted, filename)

    con.execute(
        "INSERT INTO enrichment_log (source, rows_added) VALUES (?, ?)",
        ("ttb_cola", total_inserted),
    )
    con.commit()
    log.info("COLA load complete. Total products inserted: %d", total_inserted)
    con.close()


if __name__ == "__main__":
    main()
