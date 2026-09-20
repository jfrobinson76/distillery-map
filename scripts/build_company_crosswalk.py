#!/usr/bin/env python3
"""
Build data/company-crosswalk/company-crosswalk.csv: map distillery slug -> registered company.

This is the spine for the filings x map join (vault: "Own the Index - Public Data Joins
Plan"; build ideas 46, 50, 53). The map has 6,139 distilleries and no company field.
Companies House, the CRO and the filings watcher speak in company numbers. Nothing joins
them until this file does.

Sources, in order of trust:
  1. data/company-crosswalk/company-crosswalk-manual.csv  hand-verified rows (numbers confirmed
     against the register by the vault's filings watcher)
  1b. data/company-crosswalk/company-crosswalk-operators.csv  site -> operating company for
     group-run distilleries (Diageo Scotland, Dewar's, Inver House, Beam Suntory UK...) and
     independents whose company name differs from the site name. Company checked on the
     register (status, SIC, accounts type); the site-to-company relation is industry
     knowledge, which is why the row is `high`, not `verified`. Takes precedence over
     Wikidata and the name search.
  2. data/company-crosswalk/wd-direct.csv + wd-via-owner.csv  Wikidata (CC0), matched on name
     and country. Thin: 26 Companies House ids worldwide at 18 Sep 2026.
  2b. data/company-crosswalk/*-candidates.csv (ttb- for the US, canada-, australia-, japan-,
     france-... each written by its own scripts/match_*_registers.py): register matches. Only `high` and `medium` rows with a register number enter the
     crosswalk; `low` and number-less rows stay in the candidates file as leads. A slug may
     carry a `self` and an `operator` row. A manual or operator-map row for the slug
     replaces them. canada-licences.csv (provincial liquor licences) is a second identifier
     layer and is not folded.
  3. Companies House search API, UK only, when COMPANIES_HOUSE_API_KEY is set.
     Free key: https://developer.company-information.service.gov.uk/  (register, create
     an application, copy the REST key). Rate limit 600 requests / 5 minutes; this
     script sleeps 0.6s between calls, so 521 UK distilleries take ~5 minutes.

Run:
  python3 scripts/build_company_crosswalk.py                # manual + wikidata
  COMPANIES_HOUSE_API_KEY=... python3 scripts/build_company_crosswalk.py --companies-house
  python3 scripts/build_company_crosswalk.py --companies-house --limit 20   # try 20 first

Companies House search rows already in the output CSV are carried forward when
--companies-house is not given, so a rebuild without the key does not lose them. A manual
or operator row for a slug replaces the search row. The operators file may hold more than
one row per slug (operator plus group) when both exist.

Never writes anything but the crosswalk. Never fetches without --companies-house.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
ENR = ROOT / "data" / "company-crosswalk"
OUT = ENR / "company-crosswalk.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

# Wikidata sometimes hangs a subsidiary's registry id on the parent item (William Grant &
# Sons carries a French OpenCorporates id). A registry outside the distillery's own country
# is a lead, not a match.
JURIS = {"United Kingdom": "gb", "Ireland": "ie", "Belgium": "be", "Japan": "jp", "France": "fr",
         "Norway": "no", "Denmark": "dk", "New Zealand": "nz", "Netherlands": "nl", "Germany": "de",
         "Australia": "au", "Canada": "ca", "United States": "us", "Sweden": "se", "Finland": "fi",
         "Switzerland": "ch", "Austria": "at", "Italy": "it", "Spain": "es"}

STOP = {"distillery", "distillers", "distilling", "distilleries", "the", "ltd", "limited", "llc",
        "inc", "co", "company", "plc", "gmbh", "sa", "bv", "nv", "and", "of", "de", "la", "le"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return " ".join(t for t in s.split() if t not in STOP)


def tokens(s: str) -> set[str]:
    return set(norm(s).split())


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a or b else 0.0


def load_map() -> list[dict]:
    feats = json.loads(GEO.read_text())["features"]
    return [{"slug": f["properties"]["slug"], "name": f["properties"]["name"],
             "country": f["properties"].get("country", ""), "region": f["properties"].get("region", "")}
            for f in feats]


def load_manual() -> list[dict]:
    p = ENR / "company-crosswalk-manual.csv"
    return list(csv.DictReader(p.open())) if p.exists() else []


def load_prior_search() -> list[dict]:
    if not OUT.exists():
        return []
    return [r for r in csv.DictReader(OUT.open()) if r["match_method"] == "companies-house-search"]


def load_candidates() -> list[dict]:
    rows = []
    for p in sorted(ENR.glob("*-candidates.csv")):
        if p.name == "cro-candidates.csv":  # review file, different shape
            continue
        rows += [r for r in csv.DictReader(p.open())
                 if r.get("confidence") in ("high", "medium") and r.get("company_number")]
    return rows


def load_wikidata() -> list[dict]:
    rows = []
    for name in ("wd-direct.csv", "wd-via-owner.csv"):
        p = ENR / name
        if p.exists():
            rows += list(csv.DictReader(p.open()))
    return rows


def wikidata_registry(row: dict) -> tuple[str, str]:
    if row.get("ch"):
        return "companies-house", row["ch"]
    oc = row.get("oc", "")
    juris, _, num = oc.partition("/")
    return f"opencorporates:{juris}", num


def match_wikidata(dists: list[dict], wd: list[dict], today: str) -> list[dict]:
    by_country: dict[str, list[dict]] = {}
    for d in dists:
        by_country.setdefault(d["country"], []).append(d)
    out = []
    for row in wd:
        cands = by_country.get(row.get("countryLabel", ""), [])
        best, score = None, 0.0
        wt = tokens(row["itemLabel"])
        if not wt:
            continue
        for d in cands:
            s = jaccard(wt, tokens(d["name"]))
            if s > score:
                best, score = d, s
        if best is None or score < 0.5:
            continue
        reg, num = wikidata_registry(row)
        conf = "high" if score >= 0.8 else "medium"
        note = f"name jaccard {score:.2f}"
        juris = reg.split(":")[-1] if reg.startswith("opencorporates:") else "gb"
        if JURIS.get(best["country"]) and juris != JURIS[best["country"]]:
            conf, note = "low", note + f"; registry {juris} is not {JURIS[best['country']]}, likely a subsidiary id on the parent item"
        out.append({"slug": best["slug"], "distillery_name": best["name"], "country": best["country"],
                    "registry": reg, "company_number": num, "company_name": row.get("orgLabel", ""),
                    "relation": "self" if row["item"] == row["org"] else "owner-or-operator",
                    "match_method": "wikidata-name", "confidence": conf,
                    "verified": "", "source": row["item"], "note": note})
    return out


def ch_search(name: str, key: str) -> list[dict]:
    q = urllib.parse.quote(name)
    req = urllib.request.Request(
        f"https://api.company-information.service.gov.uk/search/companies?q={q}&items_per_page=5",
        headers={"Authorization": "Basic " + base64.b64encode(f"{key}:".encode()).decode(),
                 "User-Agent": "StillboundDistilleryMap/0.1 (stillbound.ai)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get("items", [])


def match_companies_house(dists: list[dict], have: set[str], key: str, limit: int | None,
                          today: str) -> list[dict]:
    uk = [d for d in dists if d["country"] == "United Kingdom" and d["slug"] not in have]
    if limit:
        uk = uk[:limit]
    out = []
    for i, d in enumerate(uk, 1):
        try:
            items = ch_search(d["name"], key)
        except Exception as e:  # noqa: BLE001
            print(f"  {d['slug']}: {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(2)
            continue
        dt = tokens(d["name"])
        best, score = None, 0.0
        for it in items:
            s = jaccard(dt, tokens(it.get("title", "")))
            if it.get("company_status") == "active":
                s += 0.05
            if s > score:
                best, score = it, s
        if best and score >= 0.6:
            # An exact name on a dissolved or newly registered company is usually a shell
            # (BOWMORE LTD dissolved, ABERFELDY LIMITED registered 2025); the operator is a
            # group company. Cap those at medium so the review pass sees them.
            status = best.get("company_status")
            created = str(best.get("date_of_creation") or "")
            conf = "high" if score >= 0.9 else "medium"
            if status != "active" or created >= "2023":
                conf = "medium" if conf == "high" else "low"
            out.append({"slug": d["slug"], "distillery_name": d["name"], "country": d["country"],
                        "registry": "companies-house", "company_number": best["company_number"],
                        "company_name": best["title"], "relation": "name-match",
                        "match_method": "companies-house-search",
                        "confidence": conf, "verified": "",
                        "source": "https://find-and-update.company-information.service.gov.uk/company/"
                                  + best["company_number"],
                        "note": f"status {status}; created {created[:4]}; jaccard {score:.2f}"})
        if i % 25 == 0:
            print(f"  {i}/{len(uk)} searched, {len(out)} matched")
        time.sleep(0.6)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--companies-house", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    today = time.strftime("%Y-%m-%d")

    dists = load_map()
    by_slug = {d["slug"]: d for d in dists}
    rows: list[dict] = []
    for m in load_manual():
        d = by_slug.get(m["slug"])
        if not d:
            print(f"manual row has unknown slug {m['slug']}", file=sys.stderr)
            continue
        rows.append({"slug": m["slug"], "distillery_name": d["name"], "country": d["country"],
                     "registry": m["registry"], "company_number": m["company_number"],
                     "company_name": m["company_name"], "relation": m["relation"],
                     "match_method": "manual", "confidence": "verified", "verified": today,
                     "source": m.get("source") or "vault .claude/ingest/filings-watchlist.json",
                     "note": m.get("note", "")})
    have = {r["slug"] for r in rows}
    manual_slugs = set(have)
    seen = {(r["slug"], r["company_number"]) for r in rows}
    ops = ENR / "company-crosswalk-operators.csv"
    for m in (list(csv.DictReader(ops.open())) if ops.exists() else []):
        d = by_slug.get(m["slug"])
        if not d or m["slug"] in manual_slugs or (m["slug"], m["company_number"]) in seen:
            continue
        seen.add((m["slug"], m["company_number"]))
        rows.append({"slug": m["slug"], "distillery_name": d["name"], "country": d["country"],
                     "registry": m["registry"], "company_number": m["company_number"],
                     "company_name": m["company_name"], "relation": m["relation"],
                     "match_method": "operator-map", "confidence": m.get("confidence") or "high",
                     "verified": "", "source": "company-crosswalk-operators.csv", "note": m.get("note", "")})
        have.add(m["slug"])
    for r in match_wikidata(dists, load_wikidata(), today):
        if r["slug"] not in have:
            rows.append(r)
            have.add(r["slug"])
    prior = set(have)
    for r in load_candidates():
        if r["slug"] in by_slug and r["slug"] not in prior and (r["slug"], r["company_number"]) not in seen:
            rows.append({k: r.get(k, "") for k in FIELDS})
            seen.add((r["slug"], r["company_number"]))
            have.add(r["slug"])
    if args.companies_house:
        key = os.environ.get("COMPANIES_HOUSE_API_KEY")
        if not key:
            print("COMPANIES_HOUSE_API_KEY not set. Register a free key at "
                  "https://developer.company-information.service.gov.uk/ and export it.", file=sys.stderr)
            return 2
        rows += match_companies_house(dists, have, key, args.limit, today)
    else:
        rows += [r for r in load_prior_search() if r["slug"] not in have]

    rows.sort(key=lambda r: (r["country"], r["slug"]))
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    uk_total = sum(1 for d in dists if d["country"] == "United Kingdom")
    uk_done = sum(1 for r in rows if r["country"] == "United Kingdom")
    by_method: dict[str, int] = {}
    for r in rows:
        by_method[r["match_method"]] = by_method.get(r["match_method"], 0) + 1
    print(f"crosswalk: {len(rows)} rows across {len(dists)} distilleries; "
          f"UK {uk_done}/{uk_total}; by method {by_method}; -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
