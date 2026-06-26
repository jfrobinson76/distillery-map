"""
Phase 2B — Step 4: Signal monitoring.

Two signal sources:
  1. RSS feeds (15 curated spirits industry feeds) — scan for entity name matches,
     write to signals table with type 'rss_mention'.
  2. New entrant detection — compare TTB permit issue_dates and HMRC entries
     against DB; flag anything from 2023+ as is_new_entrant = 1.

Outputs:
  - signals table rows (DB)
  - data/enriched/signals.json   — all new signals this run
  - data/enriched/new_entrants.csv — hot list: new DSPs with contacts

Rate limit: 1 req/sec per feed fetch.
Skips entries already in signals table (by url).
"""

import csv
import json
import logging
import sqlite3
import time
import defusedxml.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests
from rapidfuzz import fuzz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"
ENRICHED_DIR = REPO_ROOT / "data" / "enriched"
ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

SIGNALS_JSON = ENRICHED_DIR / "signals.json"
NEW_ENTRANTS_CSV = ENRICHED_DIR / "new_entrants.csv"

HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}
TIMEOUT = 15
NAME_MATCH_THRESHOLD = 75  # lower than regulatory matching — news doesn't use official names

# New entrant cutoff — distilleries that opened from this year onwards
NEW_ENTRANT_YEAR = 2023

RSS_FEEDS = [
    # Trade / industry
    {"id": "shanken_news", "url": "https://www.shankennewsdaily.com/index.php/feed/"},
    {"id": "spirits_business", "url": "https://www.thespiritsbusiness.com/feed/"},
    {"id": "drinks_business", "url": "https://www.thedrinksbusiness.com/feed/"},
    {"id": "craft_spirits", "url": "https://craftspiritsmag.com/feed/"},
    {"id": "whiskey_wash", "url": "https://thewhiskeywash.com/feed/"},
    # Culture / consumer
    {"id": "vinepair", "url": "https://vinepair.com/feed/"},
    {"id": "punch_drink", "url": "https://punchdrink.com/feed/"},
    {"id": "imbibe", "url": "https://imbibemagazine.com/feed/"},
    {"id": "decanter", "url": "https://www.decanter.com/feed/"},
    # Regional / specific
    {"id": "irish_whiskey_mag", "url": "https://irishwhiskeymagazine.com/feed/"},
    {"id": "distillery_trail", "url": "https://www.distillerytrail.com/feed/"},
]

# Signal type keywords — headline patterns suggesting a business event
SIGNAL_KEYWORDS = {
    "new_entrant": ["opens", "opening", "new distillery", "launches", "founded", "first batch",
                    "new license", "new permit", "granted", "approved"],
    "expansion": ["expands", "expansion", "new still", "capacity", "second distillery",
                  "new facility", "extension", "grows"],
    "exec_hire": ["appoints", "appointed", "names", "hires", "joins as", "new ceo", "new director",
                  "new distiller", "head distiller"],
    "acquisition": ["acquired", "acquisition", "buys", "sold to", "merger", "merges",
                    "investment", "stake"],
}


def fetch_feed(feed: dict) -> list[dict]:
    """Fetch and parse an RSS feed. Returns list of {title, url, published_date}."""
    try:
        resp = requests.get(feed["url"], headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        time.sleep(1.0)
        root = ET.fromstring(resp.content)
    except Exception as exc:
        log.warning("Feed %s failed: %s", feed["id"], exc)
        return []

    entries = []
    # RSS 2.0
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub = item.findtext("pubDate", "").strip()
        if title and link:
            entries.append({"title": title, "url": link, "published_date": pub})

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link", ns)
        pub_el = entry.find("atom:published", ns) or entry.find("atom:updated", ns)
        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.get("href", "").strip() if link_el is not None else ""
        pub = pub_el.text.strip() if pub_el is not None and pub_el.text else ""
        if title and link:
            entries.append({"title": title, "url": link, "published_date": pub})

    return entries


def classify_signal(headline: str) -> str:
    """Return the most specific signal type for a headline, or 'rss_mention'."""
    lower = headline.lower()
    for signal_type, keywords in SIGNAL_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return signal_type
    return "rss_mention"


def match_entity(headline: str, entities: list[tuple]) -> tuple[str | None, str | None, int]:
    """Fuzzy-match headline against entity names. Returns (source_id, matched_name, score)."""
    best_sid, best_name, best_score = None, None, 0
    for sid, name in entities:
        score = fuzz.partial_ratio(name.lower(), headline.lower())
        if score > best_score:
            best_score, best_sid, best_name = score, sid, name
    if best_score >= NAME_MATCH_THRESHOLD:
        return best_sid, best_name, best_score
    return None, None, 0


def run_rss_signals(con: sqlite3.Connection, entities: list[tuple]) -> list[dict]:
    """Fetch all feeds, match against entities, write to signals table."""
    existing_urls = {
        r[0] for r in con.execute("SELECT url FROM signals WHERE url IS NOT NULL")
    }

    new_signals = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for feed in RSS_FEEDS:
        log.info("Fetching %s…", feed["id"])
        entries = fetch_feed(feed)
        log.info("  %d entries", len(entries))

        for entry in entries:
            if entry["url"] in existing_urls:
                continue

            sid, matched_name, score = match_entity(entry["title"], entities)
            if not sid:
                continue

            signal_type = classify_signal(entry["title"])
            con.execute(
                """INSERT INTO signals
                   (entity_source_id, signal_type, source, headline, url,
                    published_date, matched_name, detected_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))""",
                (sid, signal_type, feed["id"], entry["title"],
                 entry["url"], entry["published_date"], matched_name),
            )
            new_signals.append({
                "entity_source_id": sid,
                "signal_type": signal_type,
                "source": feed["id"],
                "headline": entry["title"],
                "url": entry["url"],
                "published_date": entry["published_date"],
                "matched_name": matched_name,
                "match_score": score,
                "detected_date": today,
            })
            existing_urls.add(entry["url"])

    con.commit()
    log.info("RSS signals: %d new matches written", len(new_signals))
    return new_signals


def flag_new_entrants(con: sqlite3.Connection) -> int:
    """Flag entities that have an RSS new_entrant signal."""
    result = con.execute(
        """UPDATE regulatory SET is_new_entrant = 1
           WHERE entity_source_id IN (
               SELECT DISTINCT entity_source_id FROM signals
               WHERE signal_type = 'new_entrant'
           )
           AND is_new_entrant = 0"""
    )
    flagged = result.rowcount
    con.commit()
    log.info("New entrants flagged via RSS signals: %d", flagged)
    return flagged


def export_new_entrants(con: sqlite3.Connection) -> int:
    """Write new_entrants.csv — entities with a new_entrant signal + any contact data."""
    rows = con.execute(
        """SELECT DISTINCT e.name, e.website, e.website_status,
                  l.city, l.state,
                  r.ttb_permit_number, r.state_license_number,
                  s.headline, s.source, s.published_date,
                  c.contact_email, c.contact_name, c.contact_role
           FROM entities e
           JOIN regulatory r ON r.entity_source_id = e.source_id
           JOIN signals s ON s.entity_source_id = e.source_id AND s.signal_type = 'new_entrant'
           LEFT JOIN locations l ON l.entity_source_id = e.source_id
           LEFT JOIN contacts c ON c.entity_source_id = e.source_id
           ORDER BY s.published_date DESC"""
    ).fetchall()

    with open(NEW_ENTRANTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "website", "website_status", "city", "state",
            "ttb_permit", "assoc_member",
            "signal_headline", "signal_source", "signal_date",
            "contact_email", "contact_name", "contact_role",
        ])
        writer.writerows(rows)

    log.info("new_entrants.csv written: %d rows → %s", len(rows), NEW_ENTRANTS_CSV)
    return len(rows)


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run Phase 2 + Phase 2B Steps 1-3 first")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    # Load all entity names for matching
    entities = con.execute("SELECT source_id, name FROM entities WHERE name IS NOT NULL").fetchall()
    log.info("%d entities loaded for RSS matching", len(entities))

    # RSS signals
    new_signals = run_rss_signals(con, entities)

    # New entrant detection
    flagged = flag_new_entrants(con)

    # Export hot list
    ne_rows = export_new_entrants(con)

    # Save signals JSON
    with open(SIGNALS_JSON, "w", encoding="utf-8") as f:
        json.dump(new_signals, f, indent=2, ensure_ascii=False)
    log.info("signals.json written: %d entries → %s", len(new_signals), SIGNALS_JSON)

    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("phase2b_signal_monitor", len(new_signals),
         f"rss_signals={len(new_signals)}, new_entrants_flagged={flagged}, hot_list_rows={ne_rows}"),
    )
    con.commit()
    con.close()

    log.info("Signal monitor complete:")
    log.info("  New RSS signals:   %d", len(new_signals))
    log.info("  New entrants:      %d (via RSS signals)", flagged)
    log.info("  Hot list rows:     %d → %s", ne_rows, NEW_ENTRANTS_CSV)


if __name__ == "__main__":
    main()
