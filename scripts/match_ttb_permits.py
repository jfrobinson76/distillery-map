#!/usr/bin/env python3
"""
Match the map's US distilleries against the TTB list of spirits permittees (public record).

The United States has no national company register. What it has is the TTB's weekly FOIA
list of FAA Act basic permits for distilled spirits plants: permit number, the permittee's
legal name (Owner_Name), its trading name (Operating_Name) and the premises address.
https://www.ttb.gov/public-information/foia/list-of-permittees ->
FRL_Spirits_Producers_and_Bottlers_List.csv (~5,500 rows, 750 KB). A permit proves
permission, not a working still (docs/data-quality/ttb-permit-type-research-2026-08-29.md),
which is why this script only ever runs map -> permit, never permit -> map.

For the crosswalk the permittee IS the registered business behind the pin: it is the entity
that files with TTB and holds the bond. State Secretary-of-State numbers are a second layer,
per state, and are not attempted here.

Run:
  python3 scripts/match_ttb_permits.py --fetch          # download today's list to data/enriched/
  python3 scripts/match_ttb_permits.py                  # match against the cached list

Output: data/company-crosswalk/ttb-candidates.csv in the crosswalk schema, one row per US
slug that matched. build_company_crosswalk.py folds it in. Nothing here is `verified`.

Matching, pass 1 (name): premises state from the pin's address (161 pins have no address;
those match nationwide and cap at `medium`), token Jaccard of the pin name against both
permittee names, city agreement as a tie-break and a lift. Thresholds: `high` >= 0.8 with
state agreeing (or an exact name), `medium` 0.6-0.8, `low` 0.5-0.6.
Pass 2 (premises), for pins pass 1 left below 0.5: same ZIP, same street number, street
tokens overlap. Catches permits held under a name the pin does not carry (holding company,
brewery that also distils). Always `medium`, `relation: operator` unless the names overlap.
Below both bars no row is written.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
TTB = ROOT / "data" / "enriched" / "ttb_spirits_permits.csv"
OUT = ROOT / "data" / "company-crosswalk" / "ttb-candidates.csv"
TTB_URL = "https://www.ttb.gov/system/files/2025-04/FRL_Spirits_Producers_and_Bottlers_List.csv"
TTB_PAGE = "https://www.ttb.gov/public-information/foia/list-of-permittees"
UA = "Stillbound-Research/1.0 (data@stillbound.ai)"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

STOP = {"distillery", "distillers", "distilling", "distilleries", "distillery's", "the", "ltd",
        "limited", "llc", "l", "c", "inc", "incorporated", "corp", "corporation", "co", "company",
        "and", "of", "spirits", "craft", "artisan", "dba", "lp", "llp", "group", "holdings"}
STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
          "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
          "VA", "WA", "WV", "WI", "WY", "DC", "PR", "VI"}
ADDR_RE = re.compile(r",\s*([^,]+?)\s*,\s*([A-Z]{2})\s*(\d{5})?(?:-\d{4})?\s*,\s*USA?\s*$")
STREET_ABBR = {"street": "st", "avenue": "ave", "road": "rd", "drive": "dr", "boulevard": "blvd",
               "lane": "ln", "highway": "hwy", "north": "n", "south": "s", "east": "e", "west": "w",
               "suite": "ste", "unit": "ste", "#": "ste"}


def street_tokens(s: str) -> tuple[str, set[str]]:
    """(street number, normalised street tokens) from a street line."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 #]+", " ", s)
    toks = [STREET_ABBR.get(t, t) for t in s.split()]
    num = toks[0] if toks and re.match(r"^\d+[a-z]?$", toks[0]) else ""
    return num, {t for t in toks[1:] if t not in ("ste",) and not t.isdigit()}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return " ".join(t for t in s.split() if t not in STOP)


def tokens(s: str) -> set[str]:
    return set(norm(s).split())


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a or b else 0.0


def fetch() -> None:
    TTB.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(TTB_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    TTB.write_bytes(data)
    n = sum(1 for _ in csv.DictReader(data.decode("utf-8-sig").splitlines())) if data else 0
    print(f"fetched {len(data)} bytes, {n} permits -> {TTB.relative_to(ROOT)}")
    (TTB.with_suffix(".txt")).write_text(
        f"source: {TTB_URL}\nindex: {TTB_PAGE}\nfetched: {time.strftime('%Y-%m-%d')}\nrows: {n}\n"
        "licence: US federal public record (FOIA frequently requested list)\n")


def load_ttb() -> list[dict]:
    rows = []
    with TTB.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            r["_owner"] = tokens(r["Owner_Name"])
            r["_oper"] = tokens(r["Operating_Name"])
            r["_city"] = norm(r["City"])
            r["_zip"] = r["Prem_Zip"][:5].zfill(5)
            r["_num"], r["_street"] = street_tokens(r["Street"])
            rows.append(r)
    return rows


def load_us() -> list[dict]:
    feats = json.loads(GEO.read_text())["features"]
    out = []
    for f in feats:
        p = f["properties"]
        if p.get("country") != "United States":
            continue
        m = ADDR_RE.search(p.get("address") or "")
        state = m.group(2) if m and m.group(2) in STATES else ""
        city = norm(m.group(1)) if m else ""
        zip5 = m.group(3) if m and m.group(3) else ""
        num, street = street_tokens((p.get("address") or "").split(",")[0]) if m else ("", set())
        out.append({"slug": p["slug"], "name": p["name"], "state": state, "city": city,
                    "toks": tokens(p["name"]), "zip": zip5, "num": num, "street": street})
    return out


def best_match(d: dict, ttb: list[dict], by_state: dict[str, list[dict]]) -> tuple[dict, float, str] | None:
    pool = by_state.get(d["state"]) if d["state"] else ttb
    if not pool:
        return None
    best, best_score, best_via = None, 0.0, ""
    for r in pool:
        for via, tk in (("operating", r["_oper"]), ("owner", r["_owner"])):
            if not tk:
                continue
            s = jaccard(d["toks"], tk)
            if s == 0:
                continue
            if d["city"] and r["_city"] and d["city"] == r["_city"]:
                s = min(1.0, s + 0.1)
            if s > best_score or (s == best_score and best is not None and via == "operating" and best_via == "owner"):
                best, best_score, best_via = r, s, via
    if best is None:
        return None
    return best, best_score, best_via


def premises_match(d: dict, by_zip: dict[str, list[dict]]) -> tuple[dict, float] | None:
    if not d["zip"] or not d["num"]:
        return None
    best, best_score = None, 0.0
    for r in by_zip.get(d["zip"], []):
        if r["_num"] != d["num"]:
            continue
        s = jaccard(d["street"], r["_street"])
        if s > best_score:
            best, best_score = r, s
    return (best, best_score) if best is not None and best_score >= 0.3 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download today's TTB list first")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    if not TTB.exists():
        print(f"{TTB.relative_to(ROOT)} missing; run with --fetch", file=sys.stderr)
        return 2

    ttb = load_ttb()
    by_state: dict[str, list[dict]] = {}
    for r in ttb:
        by_state.setdefault(r["State"], []).append(r)
    by_zip: dict[str, list[dict]] = {}
    for r in ttb:
        by_zip.setdefault(r["_zip"], []).append(r)
    us = load_us()
    fetched = ""
    meta = TTB.with_suffix(".txt")
    if meta.exists():
        for line in meta.read_text().splitlines():
            if line.startswith("fetched:"):
                fetched = line.split(":", 1)[1].strip()

    rows, dist = [], {"high": 0, "medium": 0, "low": 0, "premises": 0, "none": 0}
    for d in us:
        m = best_match(d, ttb, by_state)
        if not m or m[1] < 0.5:
            pm = premises_match(d, by_zip)
            if not pm:
                dist["none"] += 1
                continue
            r, s = pm
            dist["premises"] += 1
            name_overlap = max(jaccard(d["toks"], r["_owner"]), jaccard(d["toks"], r["_oper"]))
            rows.append({"slug": d["slug"], "distillery_name": d["name"], "country": "United States",
                         "registry": "ttb-basic-permit", "company_number": r["Permit_Number"],
                         "company_name": r["Owner_Name"],
                         "relation": "self" if name_overlap >= 0.3 else "operator",
                         "match_method": "ttb-premises", "confidence": "medium", "verified": "",
                         "source": TTB_PAGE,
                         "note": (f"same premises: {r['Street'].title()}, {r['City'].title()} {r['_zip']}, "
                                  f"street overlap {s:.2f}, name overlap {name_overlap:.2f}"
                                  + (f"; dba {r['Operating_Name']}" if r["Operating_Name"] else "")
                                  + (f"; list of {fetched}" if fetched else ""))})
            continue
        r, score, via = m
        exact = norm(d["name"]) in (norm(r["Operating_Name"]), norm(r["Owner_Name"]))
        if (score >= 0.8 or exact) and d["state"]:
            conf = "high"
        elif score >= 0.6 or exact:
            conf = "medium"
        else:
            conf = "low"
        dist[conf] += 1
        owner_is_person = not any(t in r["Owner_Name"].upper() for t in ("LLC", "INC", "CORP", "CO", "LTD", "LP", "COMPANY", "PARTNERS", "TRUST", "L.L.C", "GROUP"))
        relation = "self"
        if via == "operating" and r["_owner"] and jaccard(d["toks"], r["_owner"]) < 0.3 and not owner_is_person:
            relation = "operator"
        note = (f"jaccard {score:.2f} via {via}; premises {r['City'].title()}, {r['State']}"
                + (f"; dba {r['Operating_Name']}" if r["Operating_Name"] else "")
                + ("; owner is an individual" if owner_is_person else "")
                + ("; pin has no address, matched nationwide" if not d["state"] else "")
                + (f"; list of {fetched}" if fetched else ""))
        rows.append({"slug": d["slug"], "distillery_name": d["name"], "country": "United States",
                     "registry": "ttb-basic-permit", "company_number": r["Permit_Number"],
                     "company_name": r["Owner_Name"], "relation": relation,
                     "match_method": "ttb-name-state", "confidence": conf, "verified": "",
                     "source": TTB_PAGE, "note": note})
    rows.sort(key=lambda r: r["slug"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"US pins {len(us)}; permits {len(ttb)}; matched {len(rows)}; {dist}; "
          f"no-state pins {sum(1 for d in us if not d['state'])}; -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
