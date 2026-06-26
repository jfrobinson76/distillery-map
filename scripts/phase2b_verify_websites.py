"""
Phase 2B — Step 2: Verify all 6,497 distillery websites are live.

Sends a HEAD request to each entity's website URL and records:
  LIVE        — 200/301/302 resolving to a live page
  REDIRECT    — permanent redirect to a different domain
  DEAD        — 4xx/5xx or connection error
  NO_WEBSITE  — no website in DB

Uses ThreadPoolExecutor for parallel requests (10 workers, per-domain rate limit).
Total runtime: ~20–40 minutes for 6,500 URLs.

Updates entities.website_status and entities.website_checked_date.
"""

import logging
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"

HEADERS = {
    "User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}
TIMEOUT = 10
MAX_WORKERS = 10
DOMAIN_RATE_LIMIT: dict[str, float] = {}  # domain → last request time


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return url


def check_website(source_id: str, url: str) -> tuple[str, str, str]:
    """Returns (source_id, url, status)."""
    if not url or not url.startswith(("http://", "https://")):
        return source_id, url, "NO_WEBSITE"

    domain = get_domain(url)

    # Per-domain rate limiting (1 req/sec per domain)
    last = DOMAIN_RATE_LIMIT.get(domain, 0)
    wait = 1.0 - (time.time() - last)
    if wait > 0:
        time.sleep(wait)
    DOMAIN_RATE_LIMIT[domain] = time.time()

    try:
        resp = requests.head(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
        )

        if resp.status_code < 400:
            # Check if final URL domain differs significantly from original
            final_domain = get_domain(resp.url)
            if final_domain != domain and "parked" not in resp.text.lower():
                return source_id, url, "REDIRECT"
            return source_id, url, "LIVE"
        else:
            # HEAD may be blocked — try GET on 405
            if resp.status_code == 405:
                resp2 = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
                return source_id, url, "LIVE" if resp2.status_code < 400 else "DEAD"
            return source_id, url, "DEAD"

    except requests.exceptions.SSLError:
        return source_id, url, "DEAD"
    except Exception:
        return source_id, url, "DEAD"


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run Phase 2 + Phase 2B Step 1 first")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    # Fetch all entities with a website that haven't been checked yet
    rows = con.execute(
        """SELECT source_id, website FROM entities
           WHERE website IS NOT NULL AND website != ''
           AND (website_status IS NULL OR website_status = '')
           ORDER BY source_id"""
    ).fetchall()

    no_website = con.execute(
        "SELECT COUNT(*) FROM entities WHERE website IS NULL OR website = ''"
    ).fetchone()[0]

    log.info("%d entities to check, %d with no website", len(rows), no_website)

    # Mark no-website entities
    con.execute(
        """UPDATE entities SET website_status = 'NO_WEBSITE',
           website_checked_date = datetime('now')
           WHERE website IS NULL OR website = ''"""
    )
    con.commit()

    checked = 0
    live = dead = redirect = 0
    checked_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(check_website, source_id, website): source_id
            for source_id, website in rows
        }

        batch = []
        for future in as_completed(futures):
            source_id, url, status = future.result()
            batch.append((status, checked_date, source_id))

            if status == "LIVE":
                live += 1
            elif status == "DEAD":
                dead += 1
            elif status == "REDIRECT":
                redirect += 1

            checked += 1

            if len(batch) >= 100:
                con.executemany(
                    "UPDATE entities SET website_status = ?, website_checked_date = ? WHERE source_id = ?",
                    batch,
                )
                con.commit()
                batch = []
                log.info("  Checked %d/%d — LIVE %d, DEAD %d, REDIRECT %d",
                         checked, len(rows), live, dead, redirect)

    if batch:
        con.executemany(
            "UPDATE entities SET website_status = ?, website_checked_date = ? WHERE source_id = ?",
            batch,
        )
        con.commit()

    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("phase2b_verify_websites", checked,
         f"LIVE={live}, DEAD={dead}, REDIRECT={redirect}, NO_WEBSITE={no_website}"),
    )
    con.commit()
    con.close()

    log.info("Website verification complete:")
    log.info("  LIVE:       %d", live)
    log.info("  DEAD:       %d", dead)
    log.info("  REDIRECT:   %d", redirect)
    log.info("  NO_WEBSITE: %d", no_website)


if __name__ == "__main__":
    main()
