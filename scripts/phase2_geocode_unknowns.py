"""
Phase 2 — Pre-flight: Reverse-geocode entities with no state parsed.

305 rows in us_distilleries_seed.csv have state="" (source_id ends _unknown).
They have valid lat/lng. This script calls Nominatim (free, no key, 1 req/sec)
to assign state, then overwrites us_distilleries_seed.csv with corrections.

Idempotent — safe to re-run. Already-geocoded rows are skipped.
"""

import csv
import json
import logging
import re
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SEED_PATH = Path(__file__).parent.parent / "data" / "enriched" / "us_distilleries_seed.csv"
GEOCODE_CACHE = Path(__file__).parent.parent / "data" / "enriched" / "geocode_cache.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)"}
RATE_LIMIT = 1.1  # seconds between requests

US_STATE_ABBREVS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}


def load_cache() -> dict:
    if GEOCODE_CACHE.exists():
        return json.loads(GEOCODE_CACHE.read_text())
    return {}


def save_cache(cache: dict) -> None:
    GEOCODE_CACHE.write_text(json.dumps(cache, indent=2))


def reverse_geocode(lat: float, lng: float, cache: dict) -> str:
    key = f"{lat:.4f},{lng:.4f}"
    if key in cache:
        return cache[key]

    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        addr = data.get("address", {})

        state_name = addr.get("state", "").lower()
        state_code = US_STATE_ABBREVS.get(state_name, "")
        country = addr.get("country_code", "").upper()

        if country != "US":
            state_code = ""

        cache[key] = state_code
        save_cache(cache)
        time.sleep(RATE_LIMIT)
        return state_code

    except Exception as exc:
        log.warning("Nominatim failed for %s,%s: %s", lat, lng, exc)
        cache[key] = ""
        save_cache(cache)
        time.sleep(RATE_LIMIT)
        return ""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def main() -> None:
    rows = []
    with open(SEED_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    unknown_rows = [r for r in rows if not r.get("state") and r.get("lat") and r.get("lng")]
    log.info("%d rows need geocoding", len(unknown_rows))

    if not unknown_rows:
        log.info("Nothing to geocode — all rows have state. Exiting.")
        return

    cache = load_cache()
    fixed = 0

    for row in unknown_rows:
        try:
            lat = float(row["lat"])
            lng = float(row["lng"])
        except (ValueError, TypeError):
            continue

        state = reverse_geocode(lat, lng, cache)
        if state:
            row["state"] = state
            old_id = row["source_id"]
            if old_id.endswith("_unknown"):
                row["source_id"] = old_id[:-8] + "_" + state
            fixed += 1
            log.info("  %s → %s", row["name"], state)
        else:
            log.info("  %s — no state resolved", row["name"])

    with open(SEED_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    log.info("Geocoding complete: %d/%d rows fixed. Seed file updated.", fixed, len(unknown_rows))


if __name__ == "__main__":
    main()
