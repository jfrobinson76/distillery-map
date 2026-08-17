#!/usr/bin/env python3
"""Remove records that carry the word "distillery" but are not distilleries.

Google Places matched on the name, so the dataset picked up a hiking trailhead,
an office park, an art gallery, a startup incubator, a running shop and a
holiday let. They inflate the count the homepage renders, which is the one
number the site's credibility rests on.

Removal is by EXPLICIT SLUG, never by pattern. A pattern pass over names looked
tempting and would have deleted Wilderness Trail Distillery, Wiggly Bridge
Distillery, Junction 56, Burnt Church, Trailhead Spirits and Spirit Lab
Distilling — all real producers whose names happen to contain "trail",
"bridge", "junction" or "lab". Names are not evidence. This list is hand-checked,
one entry at a time, with the reason recorded.

Museums and visitor centres attached to working distilleries are NOT removed
(Van Kleef, Cardrona, Old Hokonui, Yilan). A distillery can have a museum; it
cannot be a conservation area.

Every removal is written to data/audit/pruned_non_distilleries.json so the
decision is reversible and defensible later.

Run: .venv/bin/python scripts/prune_non_distilleries.py          # dry run
     .venv/bin/python scripts/prune_non_distilleries.py --apply
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
AUDIT = ROOT / "data" / "audit" / "pruned_non_distilleries.json"

# slug -> why it is not a distillery
REMOVE = {
    "distillery-apartments": "residential apartments, Germany",
    "distillery-bend-trailhead": "hiking trailhead",
    "distillery-commons": "office park, Louisville",
    "distillery-gallery": "art gallery",
    "distillery-labs": "startup incubator",
    "distillery-road-conservation-area": "conservation area",
    "mercidistillery-magasin-de-running-trail-outdoor-provisions-a-grenoble":
        "running and outdoor shop, Grenoble",
    "the-distillery-lavender-farm-studio-apartment-family-room-with-garden-view":
        "holiday rental",
    "the-distillers-library": "whisky bar, not a producer",
    "the-distillers-library-bangkok": "whisky bar, not a producer",
    "the-whisky-distillery-marina-bay-sands": "whisky retail and bar, not a producer",
    "madan-singh-anand-sons-storage-tanks-liquor-bottling-plant-distillation-plant-rectified-spirit-plant-pot-still-plant":
        "equipment supplier and bottling plant, not a producer",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = json.loads(DISTILLERIES.read_text())
    before = len(data["features"])

    removed, kept = [], []
    for f in data["features"]:
        slug = f["properties"].get("slug")
        if slug in REMOVE:
            removed.append({
                "slug": slug,
                "name": f["properties"].get("name"),
                "country": f["properties"].get("country"),
                "source": f["properties"].get("source"),
                "reason": REMOVE[slug],
            })
        else:
            kept.append(f)

    found = {r["slug"] for r in removed}
    missing = sorted(set(REMOVE) - found)

    print(f"before: {before}")
    print(f"removing: {len(removed)}")
    for r in removed:
        print(f"  {r['name'][:52]:54}{r['reason']}")
    if missing:
        print(f"\nlisted but not found ({len(missing)}) — already gone or slug changed:")
        for m in missing:
            print(f"  {m}")
    print(f"\nafter: {before - len(removed)}")

    if args.apply:
        data["features"] = kept
        DISTILLERIES.write_text(json.dumps(data, ensure_ascii=False))
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        AUDIT.write_text(json.dumps(removed, indent=2, ensure_ascii=False))
        print(f"\nwrote {DISTILLERIES.relative_to(ROOT)} and {AUDIT.relative_to(ROOT)}")
    else:
        print("\ndry run — nothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
