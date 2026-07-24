#!/usr/bin/env python3
"""Flag candidate entries in a country for the data-quality audit.

Detects three patterns found repeatedly during the July 2026 audit:
  - bare stubs (no website and no address)
  - historic/former-sounding names ("old", "ehemalige", "dawny", ...)
  - point-of-interest names that aren't distilleries (shop, hotel, museum...)
  - near-duplicate pairs (same country, <15km apart, similar/overlapping name)

This only FLAGS candidates — it never edits or removes data. Verify each
flagged entry (web search, or fan out research agents for large batches)
before touching public/data/distilleries.geojson. See data/audit/verdicts/
for the source-cited verdict format used in past sweeps.

Usage:
  .venv/bin/python scripts/audit_flag_candidates.py "United States"
  .venv/bin/python scripts/audit_flag_candidates.py "France" "Belgium"

Writes data/audit/<country-slug>_worklist.json and _pairs.json per country.
"""

import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
AUDIT_DIR = ROOT / "data" / "audit"

HIST = re.compile(
    r"\b(old|former|historic|heritage|museum|ruins?|site of|closed|"
    r"dawny|dawna|byłe|ehemalige|ehemaliger|alte|alter|bývalý|byval|"
    r"kyu|ato)\b",
    re.I,
)
POI = re.compile(
    r"\b(shop|store|sklep|geschäft|hotel|apartment|cottage|museum|shed|"
    r"kiosk|bar\b|pub\b|restaurant|cafe)\b",
    re.I,
)
NOISE_WORDS = re.compile(
    r"\b(the|distillery|distilling|distillers|brennerei|gorzelnia|"
    r"destylarnia|of|co|company)\b"
)


def slugify(name):
    n = unicodedata.normalize("NFKD", name)
    n = re.sub(r"[̀-ͯ]", "", n).lower()
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", n))


def norm_for_compare(name):
    n = NOISE_WORDS.sub("", name.lower())
    return re.sub(r"[^a-z0-9 ]", "", n).strip()


def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[1], a[0], b[1], b[0]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(
        (lo2 - lo1) / 2
    ) ** 2
    return 12742 * math.asin(math.sqrt(h))


def find_dupe_pairs(features, max_km=15, min_sim=0.75):
    grid = defaultdict(list)
    for f in features:
        x, y = f["geometry"]["coordinates"][:2]
        grid[(round(x * 5), round(y * 5))].append(f)

    seen = set()
    pairs = []
    dupe_slugs = set()
    for key, cell in grid.items():
        neighbours = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbours += grid.get((key[0] + dx, key[1] + dy), [])
        for f1 in cell:
            for f2 in neighbours:
                if f1 is f2:
                    continue
                s1, s2 = f1["properties"]["slug"], f2["properties"]["slug"]
                pair_key = tuple(sorted([s1, s2]))
                if pair_key in seen:
                    continue
                seen.add(pair_key)
                dist = haversine_km(f1["geometry"]["coordinates"], f2["geometry"]["coordinates"])
                if dist > max_km:
                    continue
                n1 = norm_for_compare(f1["properties"]["name"])
                n2 = norm_for_compare(f2["properties"]["name"])
                if not n1 or not n2:
                    continue
                sim = SequenceMatcher(None, n1, n2).ratio()
                t1, t2 = set(n1.split()), set(n2.split())
                overlap = bool(t1 and t2 and (t1 <= t2 or t2 <= t1))
                if sim >= min_sim or overlap:
                    pairs.append(
                        (f1["properties"]["name"], f2["properties"]["name"], round(dist, 1), round(sim, 2))
                    )
                    dupe_slugs.add(s1)
                    dupe_slugs.add(s2)
    return pairs, dupe_slugs


def flag_country(features, country):
    fs = [f for f in features if f["properties"].get("country") == country]
    flags = defaultdict(set)

    for f in fs:
        p = f["properties"]
        slug = p["slug"]
        name = p.get("name") or ""
        if not p.get("website") and not p.get("address"):
            flags[slug].add("stub")
        if HIST.search(name):
            flags[slug].add("historic")
        if POI.search(name):
            flags[slug].add("poi-name")
        if re.match(r"^Q\d+$", name):
            flags[slug].add("raw-qid")

    pairs, dupe_slugs = find_dupe_pairs(fs)
    for slug in dupe_slugs:
        flags[slug].add("dupe")

    by_slug = {f["properties"]["slug"]: f for f in fs}
    worklist = []
    for slug, reasons in flags.items():
        f = by_slug[slug]
        p = f["properties"]
        worklist.append(
            {
                "slug": slug,
                "name": p.get("name"),
                "region": p.get("region", ""),
                "website": p.get("website", ""),
                "address": p.get("address", ""),
                "description": (p.get("description") or "")[:100],
                "source": p.get("source", ""),
                "coords": f["geometry"]["coordinates"],
                "reasons": sorted(reasons),
            }
        )
    return fs, worklist, pairs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data = json.loads(DISTILLERIES.read_text())
    features = data["features"]
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    for country in sys.argv[1:]:
        fs, worklist, pairs = flag_country(features, country)
        slug = slugify(country)
        (AUDIT_DIR / f"{slug}_worklist.json").write_text(
            json.dumps(worklist, indent=1, ensure_ascii=False)
        )
        (AUDIT_DIR / f"{slug}_pairs.json").write_text(
            json.dumps(pairs, indent=1, ensure_ascii=False)
        )
        reason_counts = Counter(r for e in worklist for r in e["reasons"])
        print(
            f"{country}: {len(fs)} total, {len(worklist)} flagged, "
            f"{len(pairs)} dupe pairs -> {dict(reason_counts)}"
        )


if __name__ == "__main__":
    main()
