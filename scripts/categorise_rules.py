#!/usr/bin/env python3
"""Pass 1 of spirit categorisation: decide what a rule can decide, and hand the
rest to a model.

Two outputs, neither of which touches the public dataset:
  data/categories/rules.json      slug -> verdict, for everything a rule caught
  data/categories/batch_NNN.json  the remainder, batched for Haiku subagents

Nothing here writes public/data/distilleries.geojson. That only happens in
categorise_merge.py, behind a confidence gate, so a bad run is always throwaway.

Why rules only get us so far: a name match finds "Tequilera Trujillo" and misses
Ardbeg, Talisker and Lagavulin, because a famous distillery's name says nothing
about what comes off its stills. Rules handle the literal cases cheaply; world
knowledge is what the model is actually for.

Run: .venv/bin/python scripts/categorise_rules.py
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
OUTDIR = ROOT / "data" / "categories"

# How many records ride in one subagent batch. 50 keeps a batch prompt small
# enough to stay reliable while cutting ~4,500 records to ~90 calls — the
# difference between an hour and a week.
BATCH_SIZE = 50

# Controlled vocabulary. Deliberately granular where the law is granular:
# tequila and mezcal are separate denominations, cognac and armagnac separate
# AOCs, and whiskey people care about exactly those distinctions. `beer` and
# `wine` are here so breweries and wineries can be filtered OUT of a spirits
# map, not because they belong on one.
VOCAB = [
    "whisky", "gin", "vodka", "rum", "brandy", "cognac", "armagnac", "grappa",
    "calvados", "pisco", "tequila", "mezcal", "aquavit", "absinthe", "liqueur",
    "bitters", "shochu", "soju", "baijiu", "eau_de_vie", "beer", "wine", "other",
]

# Ordered: first match wins as the primary signal, but every match is kept —
# a distillery making whisky and gin is the norm, not an edge case.
RULES = [
    ("tequila",    r"tequila|tequiler"),
    ("mezcal",     r"mezcal|mescal|mezcaler"),
    ("agave_misc", r"\braicilla\b|\bsotol\b|\bbacanora\b"),
    ("cognac",     r"\bcognac\b"),
    ("armagnac",   r"\barmagnac\b"),
    ("grappa",     r"\bgrappa\b|grapper"),
    ("calvados",   r"\bcalvados\b"),
    ("pisco",      r"\bpisco\b"),
    ("aquavit",    r"aquavit|akvavit|akevitt"),
    ("absinthe",   r"absinth"),
    ("shochu",     r"shochu|焼酎"),
    ("soju",       r"\bsoju\b"),
    ("baijiu",     r"baijiu|白酒"),
    ("whisky",     r"whisk[ey]|bourbon|\bscotch\b|single malt|\brye distill"),
    ("gin",        r"\bgin\b|\bgins\b|ginebra|\bgenever\b|jenever"),
    ("vodka",      r"vodka|wodka|w[oó]dka"),
    ("rum",        r"\brum\b|\brhum\b|\bron\b|cacha[cç]a|\bcane spirit"),
    ("brandy",     r"brandy|weinbrand|obstbrand|eau[- ]de[- ]vie|\bschnaps|schnapps"),
    ("liqueur",    r"liqueur|lik[oö]r|limoncello|\bamaro\b"),
    ("bitters",    r"\bbitters\b"),
    ("beer",       r"brewery|brauerei|brewing|cervec|birrific"),
    ("wine",       r"winery|weingut|vineyard|bodega\b|cantina\b|vi[nñ]edo"),
]

# Generic words that mean "distillery" in some language and nothing about the
# spirit. Matching these would label half of Germany as brandy on no evidence.
GENERIC = re.compile(r"brennerei|destiler|distiller|distiller[ií]a|spirits?\b", re.I)

# agave_misc collapses into a real vocab term at write time.
COLLAPSE = {"agave_misc": "other"}


def signals(props: dict) -> list[str]:
    """Every vocabulary term the record's own text supports."""
    blob = " ".join(
        str(props.get(k) or "") for k in ("name", "description", "website")
    ).lower()
    found = []
    for label, pattern in RULES:
        if re.search(pattern, blob):
            found.append(COLLAPSE.get(label, label))
    # dedupe, preserve order
    return list(dict.fromkeys(found))


def main() -> None:
    data = json.loads(DISTILLERIES.read_text())
    features = data["features"]
    OUTDIR.mkdir(parents=True, exist_ok=True)

    resolved: dict[str, dict] = {}
    unresolved: list[dict] = []
    counts: Counter = Counter()

    for f in features:
        p = f["properties"]
        slug = p.get("slug")
        if not slug:
            continue
        hits = signals(p)
        if hits and hits != ["other"]:
            resolved[slug] = {
                "spirits": hits,
                "confidence": "high",
                "source": "rules",
            }
            for h in hits:
                counts[h] += 1
        else:
            # Send the model the minimum it needs to recognise a distillery:
            # name, country, and the domain (which often IS the answer).
            site = (p.get("website") or "").strip()
            domain = re.sub(r"^https?://(www\.)?", "", site).split("/")[0] if site else ""
            unresolved.append({
                "slug": slug,
                "name": p.get("name") or "",
                "country": (p.get("country") or "").strip(),
                "domain": domain,
                "generic_name": bool(GENERIC.search(p.get("name") or "")),
            })

    (OUTDIR / "rules.json").write_text(json.dumps(resolved, indent=2, ensure_ascii=False))

    batches = [unresolved[i:i + BATCH_SIZE] for i in range(0, len(unresolved), BATCH_SIZE)]
    for old in OUTDIR.glob("batch_*.json"):
        old.unlink()
    for i, b in enumerate(batches):
        (OUTDIR / f"batch_{i:03d}.json").write_text(
            json.dumps(b, indent=2, ensure_ascii=False)
        )

    total = len(features)
    print(f"records:           {total}")
    print(f"resolved by rules: {len(resolved)} ({len(resolved) * 100 // total}%)")
    print(f"to the model:      {len(unresolved)} in {len(batches)} batches of {BATCH_SIZE}")
    print(f"  of those, {sum(1 for u in unresolved if not u['domain'])} have no website to fall back on")
    print()
    for k, v in counts.most_common():
        print(f"  {k:11}{v}")
    print(f"\nwrote {OUTDIR.relative_to(ROOT)}/rules.json and {len(batches)} batch files")


if __name__ == "__main__":
    main()
