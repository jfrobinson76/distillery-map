#!/usr/bin/env python3
"""Pass 3: read what the distillery says about itself.

The model pass topped out around 20% because a bare domain carries no
information — world knowledge covers famous producers, and this dataset is
overwhelmingly small craft ones. Their own homepage settles it immediately:
distinctdistillers.co.uk says "rum" fifty-nine times. Fetch the page, run the
same deterministic vocabulary over the text, no model involved.

Costs nothing in tokens. It is still a crawl over someone else's servers, so:
  - one request per domain, ever (results cached to disk, re-runs are free)
  - robots.txt honoured per host
  - a delay between requests to the same host
  - a hard --limit so a run can never sprawl
  - identifies itself honestly in the User-Agent

Expect roughly a fifth to be dead, parked or JavaScript-rendered with no text
in the HTML. Those are recorded as misses rather than retried — a lapsed domain
serving a content farm is a data-quality finding, not a fetch to repeat.

Run: .venv/bin/python scripts/categorise_fetch.py --limit 200      # sample
     .venv/bin/python scripts/categorise_fetch.py --limit 5000     # the rest
"""

import argparse
import collections
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
CATDIR = ROOT / "data" / "categories"
CACHE = CATDIR / "fetch_cache.json"
VERDICTS = CATDIR / "out_fetch.json"

UA = "distillerymap.org research bot (+https://distillerymap.org; hello@distillerymap.org)"
TIMEOUT = 12
PER_HOST_DELAY = 1.0
MAX_BYTES = 400_000

# Same vocabulary as the rules pass, matched against page text rather than the
# record's own name. Thresholds matter here: a distillery's shop page mentions
# every spirit it stocks, so a single passing mention is not evidence.
TERMS = [
    ("whisky",    r"whisk[ey]y?\b|bourbon\b|single malt\b|\brye whisk"),
    ("gin",       r"\bgin\b|\bgins\b"),
    ("vodka",     r"\bvodka\b"),
    ("rum",       r"\brum\b|\brhum\b|cacha[cç]a"),
    ("tequila",   r"\btequila\b"),
    ("mezcal",    r"\bmezcal\b|\bmescal\b"),
    ("brandy",    r"\bbrandy\b|eau[- ]de[- ]vie|obstbrand|weinbrand"),
    ("cognac",    r"\bcognac\b"),
    ("armagnac",  r"\barmagnac\b"),
    ("grappa",    r"\bgrappa\b"),
    ("calvados",  r"\bcalvados\b"),
    ("pisco",     r"\bpisco\b"),
    ("aquavit",   r"\baquavit\b|\bakvavit\b"),
    ("absinthe",  r"\babsinthe\b"),
    ("liqueur",   r"\bliqueurs?\b|\bamaro\b|limoncello"),
    ("bitters",   r"\bbitters\b"),
    ("shochu",    r"\bshochu\b"),
    ("soju",      r"\bsoju\b"),
    ("baijiu",    r"\bbaijiu\b"),
    ("beer",      r"\bbrewery\b|\bbrewing\b|\bbeers?\b|\bales?\b"),
    ("wine",      r"\bwinery\b|\bvineyard\b|\bwines?\b"),
]
COMPILED = [(label, re.compile(rx, re.I)) for label, rx in TERMS]

# A term has to carry weight before it counts, and has to be a real share of the
# page's spirit vocabulary. Otherwise every distillery with a well-stocked bar
# comes back making all twenty-one categories.
MIN_HITS = 3
MIN_SHARE = 0.15


def page_text(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read(MAX_BYTES)
        charset = r.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, "ignore")
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def classify(text: str) -> tuple[list[str], str]:
    counts = {lab: len(rx.findall(text)) for lab, rx in COMPILED}
    counts = {k: v for k, v in counts.items() if v >= MIN_HITS}
    if not counts:
        return [], "low"
    total = sum(counts.values())
    keep = [k for k, v in sorted(counts.items(), key=lambda kv: -kv[1])
            if v / total >= MIN_SHARE]
    if not keep:
        return [], "low"
    # A page shouting one spirit is high; a page spreading across several is
    # still useful but less certain about which is the primary product.
    top = max(counts.values())
    confidence = "high" if top >= 8 and len(keep) <= 3 else "medium"
    return keep, confidence


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200, help="max domains this run")
    ap.add_argument("--delay", type=float, default=PER_HOST_DELAY)
    args = ap.parse_args()

    data = json.loads(DISTILLERIES.read_text())
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    verdicts = json.loads(VERDICTS.read_text()) if VERDICTS.exists() else {}

    # Only records nothing else has settled, and only ones with a website.
    settled = set(verdicts)
    for name in ("rules.json",):
        p = CATDIR / name
        if p.exists():
            settled |= set(json.loads(p.read_text()))
    for out in CATDIR.glob("out_p*.json"):
        for slug, v in json.loads(out.read_text()).items():
            if v.get("confidence") in ("high", "medium"):
                settled.add(slug)

    todo = []
    for f in data["features"]:
        p = f["properties"]
        slug, site = p.get("slug"), (p.get("website") or "").strip()
        if not slug or slug in settled or not site:
            continue
        if not site.startswith("http"):
            site = "https://" + site
        todo.append((slug, site))

    print(f"candidates without a verdict and with a website: {len(todo)}")
    print(f"cached from previous runs: {sum(1 for s, _ in todo if s in cache)}")
    todo = [t for t in todo if t[0] not in cache][:args.limit]
    print(f"fetching this run: {len(todo)} (limit {args.limit})\n")

    robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
    last_hit: dict[str, float] = {}
    stats = collections.Counter()

    for i, (slug, url) in enumerate(todo, 1):
        host = urllib.parse.urlparse(url).netloc
        rp = robots.get(host, "unset")
        if rp == "unset":
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"https://{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                rp = None
            robots[host] = rp
        if rp is not None and not rp.can_fetch(UA, url):
            cache[slug] = {"status": "robots_denied"}
            stats["robots_denied"] += 1
            continue

        wait = args.delay - (time.monotonic() - last_hit.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            text = page_text(url)
            last_hit[host] = time.monotonic()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
            cache[slug] = {"status": "unreachable", "error": type(e).__name__}
            stats["unreachable"] += 1
            continue

        spirits, conf = classify(text or "")
        cache[slug] = {"status": "ok", "chars": len(text or "")}
        if spirits:
            verdicts[slug] = {"spirits": spirits, "confidence": conf, "source": "website"}
            stats[f"resolved_{conf}"] += 1
        else:
            stats["no_signal"] += 1

        if i % 25 == 0:
            print(f"  {i}/{len(todo)} ...")
            CACHE.write_text(json.dumps(cache, indent=2))
            VERDICTS.write_text(json.dumps(verdicts, indent=2, ensure_ascii=False))

    CATDIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2))
    VERDICTS.write_text(json.dumps(verdicts, indent=2, ensure_ascii=False))

    attempted = len(todo)
    resolved = stats["resolved_high"] + stats["resolved_medium"]
    print(f"\nattempted: {attempted}")
    for k, v in stats.most_common():
        print(f"  {k:18}{v}")
    if attempted:
        print(f"\nresolve rate: {resolved * 100 // attempted}%")
    print(f"verdicts on file: {len(verdicts)} -> {VERDICTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
