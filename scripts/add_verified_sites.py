#!/usr/bin/env python3
"""Append verified sites to public/data/distilleries.geojson.

Input: a JSON list of objects with name, country, lat, lng, source, and optionally
region, website, description, address, entity_role, operator, brands.
Every row must have been verified against docs/data-quality/inclusion-rules.md
first (real address, trading today). This script does not check that; a human does.

Usage: python3 scripts/add_verified_sites.py path/to/new-sites.json
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict

GEOJSON = "public/data/distilleries.geojson"


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "distillery"


def main(path: str) -> None:
    rows = json.load(open(path))
    data = json.load(open(GEOJSON))
    feats = data["features"]

    slugs = {f["properties"].get("slug") for f in feats}
    names = {(f["properties"]["name"].lower(), f["properties"].get("country")) for f in feats}
    region_by_country = defaultdict(Counter)
    for f in feats:
        p = f["properties"]
        region_by_country[p.get("country")][p.get("region")] += 1

    added = 0
    for r in rows:
        key = (r["name"].lower(), r["country"])
        if key in names:
            print(f"skip (already on map): {r['name']} / {r['country']}")
            continue
        region = r.get("region")
        if not region:
            counts = region_by_country.get(r["country"])
            region = counts.most_common(1)[0][0] if counts else "rest"
        slug = base = slugify(r["name"])
        n = 2
        while slug in slugs:
            slug = f"{base}-{n}"
            n += 1
        slugs.add(slug)
        props = {
            "name": r["name"],
            "source": r.get("source", "curated"),
            "region": region,
            "country": r["country"],
            "website": r.get("website", ""),
            "description": r.get("description", ""),
            "address": r.get("address", ""),
            "slug": slug,
        }
        for k in ("entity_role", "operator", "brands"):
            if r.get(k):
                props[k] = r[k]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(r["lng"]), float(r["lat"])]},
            "properties": props,
        })
        added += 1
        print(f"add: {r['name']} / {r['country']} -> region={region} slug={slug}")

    json.dump(data, open(GEOJSON, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"\n{added} added, {len(feats)} total")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
