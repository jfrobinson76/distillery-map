#!/usr/bin/env python3
"""Backfill blank `country` fields and generate stable slugs for every feature
in public/data/distilleries.geojson.

Offline point-in-polygon against Natural Earth 10m admin-0 boundaries — zero
API calls. Boundaries file (gitignored):
  data/boundaries/ne_10m_admin_0_countries.geojson
Download once:
  curl -sL -o data/boundaries/ne_10m_admin_0_countries.geojson \
    https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson

Run: .venv/bin/python scripts/backfill_country.py
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
BOUNDARIES = ROOT / "data" / "boundaries" / "ne_10m_admin_0_countries.geojson"

# Natural Earth ADMIN names -> the taxonomy already used in the dataset
NAME_FIXES = {
    "United States of America": "United States",
    "Czechia": "Czech Republic",
    "Hong Kong S.A.R.": "Hong Kong",
    "Macao S.A.R": "Macau",
    "Republic of Serbia": "Serbia",
    "United Republic of Tanzania": "Tanzania",
    "Federated States of Micronesia": "Micronesia",
    "The Bahamas": "Bahamas",
    "Ivory Coast": "Côte d'Ivoire",
    "eSwatini": "Eswatini",
    "Democratic Republic of the Congo": "DR Congo",
    "Republic of the Congo": "Congo",
    "East Timor": "Timor-Leste",
    "Cabo Verde": "Cape Verde",
}

# Max distance (degrees, ~55km at equator) for snapping offshore/coastal points
NEAREST_TOLERANCE_DEG = 0.5


def slugify(name: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    return slug


def main() -> int:
    if not BOUNDARIES.exists():
        print(f"Missing boundaries file: {BOUNDARIES}\nSee header for download command.")
        return 1

    print("Loading boundaries…")
    ne = json.loads(BOUNDARIES.read_text())
    geoms, admins = [], []
    for f in ne["features"]:
        name = f["properties"].get("ADMIN") or f["properties"].get("NAME")
        geoms.append(shape(f["geometry"]))
        admins.append(NAME_FIXES.get(name, name))
    tree = STRtree(geoms)

    print("Loading distilleries…")
    data = json.loads(DISTILLERIES.read_text())
    features = data["features"]

    filled = Counter()
    unresolved = []
    already = 0

    for f in features:
        props = f["properties"]
        if (props.get("country") or "").strip():
            already += 1
            continue
        pt = Point(f["geometry"]["coordinates"])
        hits = tree.query(pt, predicate="within")
        if len(hits) > 0:
            country = admins[hits[0]]
        else:
            # coastal/offshore points: snap to nearest country within tolerance
            nearest = tree.nearest(pt)
            if geoms[nearest].distance(pt) <= NEAREST_TOLERANCE_DEG:
                country = admins[nearest]
            else:
                unresolved.append(props.get("name"))
                continue
        props["country"] = country
        filled[country] += 1

    # Stable slugs for every feature: name, then name-country, then -2/-3…
    seen: dict[str, int] = {}
    base_counts = Counter()
    for f in features:
        base_counts[slugify(f["properties"].get("name") or "distillery")] += 1
    for f in features:
        props = f["properties"]
        base = slugify(props.get("name") or "distillery") or "distillery"
        slug = base
        if base_counts[base] > 1:
            country_slug = slugify(props.get("country") or "")
            if country_slug:
                slug = f"{base}-{country_slug}"
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        if n:
            slug = f"{slug}-{n + 1}"
            seen[slug] = 1
        props["slug"] = slug

    DISTILLERIES.write_text(
        json.dumps(data, separators=(", ", ": "), ensure_ascii=False)
    )

    blank = sum(1 for f in features if not (f["properties"].get("country") or "").strip())
    slugs = [f["properties"]["slug"] for f in features]
    print(f"\nFeatures: {len(features)}")
    print(f"Country already set: {already}")
    print(f"Country filled: {sum(filled.values())}")
    print(f"Still blank: {blank}")
    print(f"Unique slugs: {len(set(slugs))}/{len(slugs)}")
    if unresolved:
        print(f"Unresolved ({len(unresolved)}): {unresolved[:20]}")
    print("\nTop countries after backfill:")
    total = Counter(
        (f["properties"].get("country") or "").strip() for f in features
    )
    for country, n in total.most_common(25):
        print(f"  {n:5}  {country or '(blank)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
