#!/usr/bin/env python3
"""Pass 2 of spirit categorisation: validate model output, gate it on
confidence, and only then touch the public dataset.

Reads:
  data/categories/rules.json    pass 1, deterministic, always trusted
  data/categories/out_*.json    subagent verdicts, trusted only above threshold

Writes (with --apply):
  public/data/distilleries.geojson   adds `spirits` to features that earned one

Default is a dry run. Nothing reaches the public file until you ask for it,
because the whole point of a confidence gate is that some of this is wrong.

Gate: `low` is never published, and neither is anything off-vocabulary. A blank
category is invisible to a visitor; a wrong one is a credibility problem on the
dataset the site's reputation rests on.

Run: .venv/bin/python scripts/categorise_merge.py            # dry run, report
     .venv/bin/python scripts/categorise_merge.py --apply    # write geojson
     .venv/bin/python scripts/categorise_merge.py --min medium --apply
"""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
CATDIR = ROOT / "data" / "categories"

VOCAB = {
    "whisky", "gin", "vodka", "rum", "brandy", "cognac", "armagnac", "grappa",
    "calvados", "pisco", "tequila", "mezcal", "aquavit", "absinthe", "liqueur",
    "bitters", "shochu", "soju", "baijiu", "eau_de_vie", "beer", "wine", "other",
}

RANK = {"low": 0, "medium": 1, "high": 2}


def load_verdicts() -> tuple[dict, Counter, list[str]]:
    """Merge rules + every out_*.json, keeping the most confident verdict per
    slug. Returns (verdicts, confidence counts, complaints)."""
    verdicts: dict[str, dict] = {}
    conf: Counter = Counter()
    problems: list[str] = []

    rules_file = CATDIR / "rules.json"
    if rules_file.exists():
        for slug, v in json.loads(rules_file.read_text()).items():
            verdicts[slug] = v
            conf["rules"] += 1

    for out in sorted(CATDIR.glob("out_*.json")):
        try:
            payload = json.loads(out.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{out.name}: unreadable JSON ({e})")
            continue
        if not isinstance(payload, dict):
            problems.append(f"{out.name}: expected an object keyed by slug")
            continue
        for slug, v in payload.items():
            if not isinstance(v, dict):
                problems.append(f"{out.name}: {slug} is not an object")
                continue
            spirits = v.get("spirits") or []
            confidence = v.get("confidence", "low")
            if confidence not in RANK:
                problems.append(f"{out.name}: {slug} has confidence {confidence!r}")
                continue
            bad = [s for s in spirits if s not in VOCAB]
            if bad:
                problems.append(f"{out.name}: {slug} used off-vocabulary {bad}")
                spirits = [s for s in spirits if s in VOCAB]
            # A high-confidence verdict with nothing in it is a contradiction.
            if confidence != "low" and not spirits:
                confidence = "low"
            entry = {"spirits": spirits, "confidence": confidence, "source": "model"}
            prior = verdicts.get(slug)
            if prior and RANK[prior["confidence"]] >= RANK[confidence]:
                continue
            verdicts[slug] = entry
            conf[confidence] += 1

    return verdicts, conf, problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the geojson")
    ap.add_argument("--min", default="medium", choices=["medium", "high"],
                    help="lowest confidence allowed into the public file")
    args = ap.parse_args()

    verdicts, conf, problems = load_verdicts()
    floor = RANK[args.min]

    data = json.loads(DISTILLERIES.read_text())
    features = data["features"]

    applied = 0
    spirit_counts: Counter = Counter()
    covered_slugs = set()

    for f in features:
        p = f["properties"]
        slug = p.get("slug")
        v = verdicts.get(slug)
        if not v:
            continue
        covered_slugs.add(slug)
        if RANK[v["confidence"]] < floor or not v["spirits"]:
            continue
        applied += 1
        for s in v["spirits"]:
            spirit_counts[s] += 1
        if args.apply:
            p["spirits"] = v["spirits"]

    total = len(features)
    print(f"records:            {total}")
    print(f"verdicts on hand:   {len(verdicts)}  (rules {conf['rules']}, "
          f"model high {conf['high']}, medium {conf['medium']}, low {conf['low']})")
    print(f"pass the --min {args.min} gate: {applied} ({applied * 100 // total}% of the dataset)")
    print(f"left uncategorised:  {total - applied}")
    print()
    for k, v in spirit_counts.most_common():
        print(f"  {k:11}{v}")

    if problems:
        print(f"\n{len(problems)} problem(s) in model output:")
        for x in problems[:20]:
            print(f"  - {x}")
        if len(problems) > 20:
            print(f"  ... and {len(problems) - 20} more")

    if args.apply:
        DISTILLERIES.write_text(json.dumps(data, ensure_ascii=False))
        print(f"\nwrote {DISTILLERIES.relative_to(ROOT)}")
    else:
        print("\ndry run — nothing written. Re-run with --apply to commit to the geojson.")


if __name__ == "__main__":
    main()
