"""
Phase 1 — Step 1: Parse distilleries.geojson and extract US entities.

Output: data/enriched/us_distilleries_seed.csv
"""

import json
import re
import csv
from pathlib import Path

GEOJSON_PATH = Path(__file__).parent.parent / "public" / "data" / "distilleries.geojson"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "enriched" / "us_distilleries_seed.csv"

STATE_RE = re.compile(r',\s*([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?(?:\s*,\s*USA?)?$')
CITY_RE = re.compile(r',\s*([^,]+?)\s*,\s*[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?(?:\s*,\s*USA?)?$')

SLUG_RE = re.compile(r'[^a-z0-9]+')


def slugify(text: str) -> str:
    return SLUG_RE.sub('_', text.lower()).strip('_')


def parse_state(address: str) -> str:
    if not address:
        return ''
    m = STATE_RE.search(address)
    return m.group(1) if m else ''


def parse_city(address: str) -> str:
    if not address:
        return ''
    m = CITY_RE.search(address)
    return m.group(1).strip() if m else ''


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(GEOJSON_PATH, encoding='utf-8') as f:
        geojson = json.load(f)

    features = geojson.get('features', [])
    total = len(features)

    rows = []
    state_parsed = 0
    has_address = 0

    for feat in features:
        props = feat.get('properties', {})
        if props.get('region') != 'usa':
            continue

        coords = feat.get('geometry', {}).get('coordinates', [None, None])
        lng = coords[0]
        lat = coords[1]

        name = props.get('name', '')
        address = props.get('address', '') or ''
        website = props.get('website', '') or ''
        geojson_source = props.get('source', '')

        city = parse_city(address)
        state = parse_state(address)

        if address:
            has_address += 1
        if state:
            state_parsed += 1

        source_id = slugify(name) + '_' + (state if state else 'unknown')

        rows.append({
            'source_id': source_id,
            'name': name,
            'lat': lat,
            'lng': lng,
            'website': website,
            'address': address,
            'city': city,
            'state': state,
            'geojson_source': geojson_source,
        })

    fieldnames = ['source_id', 'name', 'lat', 'lng', 'website', 'address', 'city', 'state', 'geojson_source']
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    us_count = len(rows)
    print(f"Total GeoJSON features:    {total}")
    print(f"US entities extracted:     {us_count}")
    print(f"  With address:            {has_address} ({has_address/us_count*100:.1f}%)")
    print(f"  State parsed:            {state_parsed} ({state_parsed/us_count*100:.1f}%)")
    print(f"  State not parsed:        {us_count - state_parsed}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
