"""
Stillbound Intelligence Layer — Phase 2 master runner.

Runs all Phase 2 steps sequentially. Safe to leave running overnight.
Progress logged to: data/phase2_run.log (also printed to stdout).

Usage:
    cd /Users/frankrobinson1/Projects/distillery-map
    source .venv/bin/activate
    python scripts/run_phase2.py

Each step is idempotent — safe to re-run if interrupted.
"""

import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_PATH = REPO_ROOT / "data" / "phase2_run.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Configure logging to both file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


STEPS = [
    # ── Phase 2: US enrichment ──────────────────────────────────────────────
    ("Geocode unknowns",        "scripts/phase2_geocode_unknowns.py"),
    ("Re-run Phase 1 match",    "__phase1_rematch__"),  # special case — see below
    ("Load matched data",       "scripts/phase2_loaders/load_phase1_matched.py"),
    ("Load COLA products",      "scripts/phase2_loaders/load_ttb_cola.py"),
    ("Scrape CA licenses",      "scripts/phase2_state_scrapers/scraper_ca.py"),
    ("Scrape TX licenses",      "scripts/phase2_state_scrapers/scraper_tx.py"),
    ("Scrape NY licenses",      "scripts/phase2_state_scrapers/scraper_ny.py"),
    ("Scrape KY licenses",      "scripts/phase2_state_scrapers/scraper_ky.py"),
    ("Scrape CO licenses",      "scripts/phase2_state_scrapers/scraper_co.py"),
    ("Generate Phase 2 report", "scripts/phase2_report.py"),
    # ── Phase 2B: Global enrichment ─────────────────────────────────────────
    ("Load IE/UK/Scotland",     "scripts/phase2b_enrich_uk_ie.py"),
    ("Verify websites",         "scripts/phase2b_verify_websites.py"),
    ("Scrape contacts",         "scripts/phase2b_scrape_contacts.py"),
    ("Signal monitor",          "scripts/phase2b_signal_monitor.py"),
]


def run_script(script_path: str) -> bool:
    full_path = REPO_ROOT / script_path
    if not full_path.exists():
        log.error("Script not found: %s", full_path)
        return False

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=REPO_ROOT,
        capture_output=False,  # let subprocess log stream to stdout/file handler above
    )
    return result.returncode == 0


def run_phase1_rematch() -> bool:
    """
    Re-run phase1_match.py on the newly geocoded rows only.
    We do this by running the full match again — it's idempotent and
    overwrites the CSVs, capturing any newly state-assigned entities.
    """
    scripts = [
        REPO_ROOT / "scripts" / "phase1_match.py",
        REPO_ROOT / "scripts" / "phase1_report.py",
    ]
    for script in scripts:
        if not script.exists():
            log.warning("Phase 1 script not found: %s — skipping rematch", script)
            return True
        result = subprocess.run([sys.executable, str(script)], cwd=REPO_ROOT)
        if result.returncode != 0:
            log.error("Phase 1 rematch failed at %s", script)
            return False
    return True


def main() -> None:
    start = datetime.now(timezone.utc)
    log.info("=" * 60)
    log.info("STILLBOUND PHASE 2 PIPELINE STARTING")
    log.info("Started at %s UTC", start.strftime("%Y-%m-%d %H:%M"))
    log.info("Log file: %s", LOG_PATH)
    log.info("=" * 60)

    passed = 0
    failed = 0

    for name, script in STEPS:
        log.info("")
        log.info("── STEP: %s ──", name.upper())
        step_start = time.time()

        try:
            if script == "__phase1_rematch__":
                ok = run_phase1_rematch()
            else:
                ok = run_script(script)
        except Exception as exc:
            log.error("Unexpected error in step '%s': %s", name, exc)
            ok = False

        elapsed = time.time() - step_start
        if ok:
            log.info("✓ %s completed in %.1fs", name, elapsed)
            passed += 1
        else:
            log.warning("✗ %s FAILED (%.1fs) — continuing", name, elapsed)
            failed += 1

    end = datetime.now(timezone.utc)
    total_mins = (end - start).total_seconds() / 60

    log.info("")
    log.info("=" * 60)
    log.info("PHASE 2 PIPELINE COMPLETE")
    log.info("Steps passed: %d  |  Failed: %d", passed, failed)
    log.info("Total runtime: %.1f minutes", total_mins)
    log.info("Finished at %s UTC", end.strftime("%Y-%m-%d %H:%M"))
    log.info("=" * 60)
    log.info("")
    log.info("Results:      data/enriched/enrichment_report_phase2.txt")
    log.info("Hot list:     data/enriched/new_entrants.csv")
    log.info("RSS signals:  data/enriched/signals.json")
    log.info("Database:     data/stillbound_intelligence.db")
    log.info("Start API:    uvicorn api.main:app --reload")

    if failed:
        log.warning("%d step(s) failed — check log for details: %s", failed, LOG_PATH)
        sys.exit(1)


if __name__ == "__main__":
    main()
