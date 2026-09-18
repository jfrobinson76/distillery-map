#!/usr/bin/env python3
"""
Match the map's Irish distilleries against the CRO open-data register (no login, no key).

The register is https://opendata.cro.ie/ -> companies.csv.zip; the Stillbound vault caches
it at .claude/cache/cro-companies.csv.zip and reads it with cro_register.py. This script
takes that zip and writes candidates for human review, up to three per distillery, ranked:
name overlap first, then status Normal, then NACE 1101 (distilling) or DISTILL in the name.

Run:
  python3 scripts/match_cro_register.py --register "~/Documents/Stillbound Knowledge/.claude/cache/cro-companies.csv.zip"

Output: data/company-crosswalk/cro-candidates.csv. Nothing here enters the crosswalk until
a row is copied into company-crosswalk-operators.csv or -manual.csv with a confidence.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = {"distillery", "distillers", "distilling", "distilleries", "the", "ltd", "limited", "dac",
        "company", "co", "irish", "whiskey", "whisky", "spirits", "and", "of", "house", "unlimited",
        "teoranta", "teo", "cuideachta"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str) -> set[str]:
    return {t for t in norm(s).split() if t not in STOP and len(t) > 1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", required=True)
    args = ap.parse_args()
    feats = json.loads((ROOT / "public" / "data" / "distilleries.geojson").read_text())["features"]
    irish = [f["properties"] for f in feats if f["properties"].get("country") == "Ireland"]
    targets = [(d["slug"], d["name"], toks(d["name"])) for d in irish]
    targets = [t for t in targets if t[2]]
    cands: dict[str, list] = {slug: [] for slug, _, _ in targets}
    zpath = Path(args.register).expanduser()
    with zipfile.ZipFile(zpath) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(name) as fh:
            reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
            for row in reader:
                cname = row.get("company_name", "")
                ct = toks(cname)
                if not ct:
                    continue
                for slug, dname, dt in targets:
                    shared = dt & ct
                    if not shared:
                        continue
                    j = len(shared) / len(dt | ct)
                    # the distillery's distinctive token must be in the company name
                    if j < 0.34 and not (len(dt) == 1 and dt <= ct):
                        continue
                    status = (row.get("company_status") or "").strip()
                    nace = (row.get("nace_v2_code") or "").strip()
                    score = j + (0.3 if status == "Normal" else 0) + (0.3 if nace.startswith("1101") else 0) \
                        + (0.2 if "DISTILL" in cname.upper() else 0)
                    cands[slug].append((score, row["company_num"], cname, status, row.get("company_type", ""),
                                        row.get("company_reg_date", ""), nace, row.get("last_accounts_date", ""),
                                        (row.get("company_address_4") or row.get("company_address_2") or "").strip()))
    out = ROOT / "data" / "company-crosswalk" / "cro-candidates.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slug", "distillery_name", "rank", "score", "company_num", "company_name", "status", "type",
                    "reg_date", "nace", "last_accounts", "address"])
        matched = 0
        for slug, dname, _ in targets:
            rows = sorted(cands[slug], reverse=True)[:3]
            if rows:
                matched += 1
            for i, r in enumerate(rows, 1):
                w.writerow([slug, dname, i, f"{r[0]:.2f}", *r[1:]])
    print(f"{matched}/{len(targets)} Irish distilleries have at least one candidate -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
