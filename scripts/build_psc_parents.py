#!/usr/bin/env python3
"""
Roll single-site companies up to the group that controls them, from the register.

Loch Lomond Distillery Company Ltd (08617161) and Glen Scotia Distillery Company Ltd
(08617165) each run one distillery and are both owned by Loch Lomond Group. A count of
"companies with one site" calls both independent. Companies House publishes each company's
persons with significant control (PSC); when the PSC is a company, that is the parent. This
script follows that chain upward for every high/verified UK company in the crosswalk and
writes the ultimate UK parent, so "independent" can mean "the controlling entity runs one
site" rather than "this registration runs one site".

Stops when: the PSC is an individual (family-owned; the company is its own top), there is
no PSC on record, the parent is outside Companies House (a foreign parent: Pernod Ricard
SA, Beam Suntory Inc), or after four levels.

Needs COMPANIES_HOUSE_API_KEY. ~1 request per company per level, 0.6 s apart.

Run:
  COMPANIES_HOUSE_API_KEY=... python3 scripts/build_psc_parents.py
Output:
  data/ownership/psc-parents.csv     one row per company: its chain and ultimate parent
  data/ownership/psc-cache.json      raw PSC responses, so reruns are cheap
"""
from __future__ import annotations

import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XW = ROOT / "data" / "company-crosswalk" / "company-crosswalk.csv"
OUT = ROOT / "data" / "ownership" / "psc-parents.csv"
CACHE = ROOT / "data" / "ownership" / "psc-cache.json"
API = "https://api.company-information.service.gov.uk"
MAX_LEVELS = 7


def get(path: str, key: str) -> tuple[int, dict]:
    req = urllib.request.Request(API + path, headers={
        "Authorization": "Basic " + base64.b64encode(f"{key}:".encode()).decode(),
        "User-Agent": "StillboundDistilleryMap/0.1 (stillbound.ai)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}


def norm_num(n: str) -> str:
    n = (n or "").strip().upper()
    return n.zfill(8) if n.isdigit() else n


def psc_of(num: str, key: str, cache: dict) -> dict:
    """Return {'kind': individual|corporate|none|error, 'parent_number', 'parent_name'}."""
    if num in cache:
        return cache[num]
    status, d = get(f"/company/{num}/persons-with-significant-control", key)
    time.sleep(0.6)
    res = {"kind": "none", "parent_number": "", "parent_name": "", "status": status}
    if status == 200:
        active = [i for i in d.get("items", []) if not i.get("ceased_on")]
        corp = [i for i in active if i.get("kind", "").startswith("corporate-entity")]
        if corp:
            i = corp[0]
            ident = i.get("identification") or {}
            reg = norm_num(ident.get("registration_number", ""))
            place = (ident.get("place_registered") or "") + " " + (ident.get("country_registered") or "")
            uk = ("england" in place.lower() or "scotland" in place.lower() or "wales" in place.lower()
                  or "northern ireland" in place.lower() or "united kingdom" in place.lower()
                  or "companies house" in place.lower())
            res = {"kind": "corporate" if (reg and uk) else "corporate-foreign",
                   "parent_number": reg if uk else "", "parent_name": i.get("name", ""),
                   "parent_place": place.strip(), "status": status}
        elif active:
            res = {"kind": "individual", "parent_number": "", "parent_name": "", "status": status}
    elif status == 404:
        res["kind"] = "none"
    else:
        res["kind"] = "error"
    cache[num] = res
    return res


def main() -> int:
    key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    if not key:
        print("COMPANIES_HOUSE_API_KEY not set", file=sys.stderr)
        return 2
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    companies: dict[str, str] = {}
    for r in csv.DictReader(XW.open(encoding="utf-8")):
        if r["registry"] == "companies-house" and r["confidence"] in ("high", "verified") and r["country"] == "United Kingdom":
            companies.setdefault(norm_num(r["company_number"]), r["company_name"])
    print(f"{len(companies)} companies to resolve")
    rows = []
    for i, (num, name) in enumerate(sorted(companies.items()), 1):
        chain = []
        cur, cur_name, stop = num, name, ""
        for level in range(MAX_LEVELS):
            p = psc_of(cur, key, cache)
            if p["kind"] == "corporate":
                chain.append(f"{cur}:{cur_name} -> {p['parent_number']}:{p['parent_name']}")
                cur, cur_name = p["parent_number"], p["parent_name"]
                continue
            stop = p["kind"]
            if p["kind"] == "corporate-foreign":
                stop = f"foreign parent: {p['parent_name']} ({p.get('parent_place','')})"
                cur_name = p["parent_name"]
                cur = ""
            break
        else:
            stop = "max levels"
        rows.append({"company_number": num, "company_name": name, "ultimate_number": cur,
                     "ultimate_name": cur_name, "levels": len(chain), "stopped_because": stop,
                     "chain": " | ".join(chain),
                     "source": f"https://find-and-update.company-information.service.gov.uk/company/{num}/persons-with-significant-control"})
        if i % 25 == 0:
            print(f"  {i}/{len(companies)}")
            CACHE.write_text(json.dumps(cache, indent=1))
    CACHE.write_text(json.dumps(cache, indent=1))
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    import collections
    tops = collections.Counter(r["ultimate_name"].upper() for r in rows)
    multi = [(k, v) for k, v in tops.most_common() if v > 1]
    print(f"wrote {OUT.relative_to(ROOT)}; {len(rows)} companies -> {len(tops)} ultimate parents; "
          f"{len(multi)} parents control >1 company:")
    for k, v in multi[:25]:
        print(f"  {v:3}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
