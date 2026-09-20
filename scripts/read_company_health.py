#!/usr/bin/env python3
"""
Read the health layer: five register facts per company behind a pin, dated.

  status          live | dissolved | liquidation | administration | receivership | dormant | unknown
  last_accounts   date the newest accounts were made up to, and their type
  overdue         accounts or confirmation statement past due (a register fact in the UK,
                  arithmetic on the next-return-due date in Ireland, blank elsewhere)
  charges         registered charges: total, outstanding, date of the newest
  read_on         the day each value was read; a value without a date is not a value

Registers read, and what each can give:
  Companies House (UK, NI)  all five. REST API, free key, profile + charges endpoints.
  CRO (Ireland)             status, last accounts date, next return due. Open-data zip,
                            offline. No charges in the free file.
  TTB (United States)       status only: on the weekly permittee list or not, plus the
                            new-permit flag. Offline against data/enriched/ttb_spirits_permits.csv.
  Everything else           nothing yet; rows are written with status "unknown" and the
                            reason, so the gap is visible, not silent.

Output: data/health/company-health.csv, one row per (registry, company_number) in the
crosswalk at high/verified, plus a dated copy under data/health/snapshots/ so two reads can
be diffed (that diff is the quarterly note). data/health/README.md defines every field.

Run:
  COMPANIES_HOUSE_API_KEY=... python3 scripts/read_company_health.py --fetch-ch --cache DIR
  python3 scripts/read_company_health.py --cache DIR                         # offline, cached
  python3 scripts/read_company_health.py --cache DIR --cro ~/Documents/"Stillbound Knowledge"/.claude/cache/cro-companies.csv.zip

Companies House: ~2 requests per company, 0.6 s apart, cap 700 per run (limit is 600 per
five minutes). Nothing is fetched without --fetch-ch.
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crosswalklib import fetch, rows as xrows  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
XW = ROOT / "data" / "company-crosswalk" / "company-crosswalk.csv"
TTB = ROOT / "data" / "enriched" / "ttb_spirits_permits.csv"
OUT = ROOT / "data" / "health" / "company-health.csv"
SNAP = ROOT / "data" / "health" / "snapshots"
CH_API = "https://api.company-information.service.gov.uk"
CH_PAGE = "https://find-and-update.company-information.service.gov.uk/company/{}"
CRO_PAGE = "https://core.cro.ie/company/{}"
TTB_PAGE = "https://www.ttb.gov/public-information/foia/list-of-permittees"

FIELDS = ["registry", "company_number", "company_name", "country", "read_on", "status", "status_detail",
          "incorporated", "last_accounts_date", "last_accounts_type", "next_due", "accounts_overdue",
          "confirmation_overdue", "charges_total", "charges_outstanding", "charges_latest", "sic",
          "source", "note"]

# Companies House status vocabulary -> ours
CH_STATUS = {"active": "live", "dissolved": "dissolved", "liquidation": "liquidation",
             "receivership": "receivership", "administration": "administration",
             "voluntary-arrangement": "voluntary-arrangement", "converted-closed": "dissolved",
             "insolvency-proceedings": "insolvency", "open": "live", "closed": "dissolved",
             "registered": "live", "removed": "dissolved"}
CRO_STATUS = {"Normal": "live", "Dissolved": "dissolved", "Liquidation": "liquidation",
              "Receivership": "receivership", "Strike Off Listed": "strike-off-listed",
              "Examinership": "examinership"}


def companies(xw: Path) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for r in csv.DictReader(xw.open(encoding="utf-8")):
        if r["confidence"] not in ("high", "verified") or not r["company_number"]:
            continue
        k = (r["registry"], r["company_number"].strip().upper())
        c = out.setdefault(k, {"registry": k[0], "company_number": k[1], "company_name": r["company_name"],
                               "country": r["country"], "slugs": []})
        c["slugs"].append(r["slug"])
    return out


# ------------------------------------------------------------ Companies House ----
def ch_read(f: fetch.Fetcher, key: str, num: str, today: str) -> dict:
    auth = {"Authorization": "Basic " + base64.b64encode(f"{key}:".encode()).decode()}
    prof = f.json(f"{CH_API}/company/{num}", headers=auth)
    row = {"read_on": today, "source": CH_PAGE.format(num)}
    if not prof:
        row.update(status="unknown", note="profile not fetched: " + f.summary().split(";")[0])
        return row
    acc = prof.get("accounts") or {}
    last = acc.get("last_accounts") or {}
    conf = prof.get("confirmation_statement") or {}
    st = prof.get("company_status", "")
    row.update(
        status=CH_STATUS.get(st, st or "unknown"),
        status_detail=prof.get("company_status_detail", ""),
        incorporated=prof.get("date_of_creation", ""),
        last_accounts_date=last.get("made_up_to", ""),
        last_accounts_type=last.get("type", ""),
        next_due=(acc.get("next_due") or ""),
        accounts_overdue=str(bool(acc.get("overdue"))).lower(),
        confirmation_overdue=str(bool(conf.get("overdue"))).lower(),
        sic=" ".join(prof.get("sic_codes") or []),
        company_name=prof.get("company_name", ""),
    )
    if row["status"] == "live" and row["last_accounts_type"] == "dormant":
        row["status"] = "dormant"
    ch = f.json(f"{CH_API}/company/{num}/charges", headers=auth)
    if ch is not None:
        items = ch.get("items") or []
        row.update(charges_total=str(ch.get("total_count", len(items))),
                   charges_outstanding=str(ch.get("unfiltered_count", ch.get("total_count", 0)) - ch.get("satisfied_count", 0)
                                           if "satisfied_count" in ch else sum(1 for i in items if i.get("status") == "outstanding")),
                   charges_latest=max((i.get("created_on") or i.get("delivered_on") or "" for i in items), default=""))
    else:
        row["note"] = "charges not fetched"
    return row


# --------------------------------------------------------------------- CRO ----
def cro_index(zip_path: Path) -> dict[str, dict]:
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(name) as fh:
            rd = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
            return {r[rd.fieldnames[0]].strip(): r for r in rd}


def cro_read(idx: dict[str, dict], num: str, today: str, zip_date: str) -> dict:
    r = idx.get(num.lstrip("0")) or idx.get(num)
    row = {"read_on": zip_date, "source": CRO_PAGE.format(num)}
    if not r:
        row.update(status="unknown", note="not in the CRO open-data file")
        return row
    g = lambda *ks: next((r[k] for k in ks if k in r and r[k]), "")  # noqa: E731
    st = g("company_status").strip()
    last_acc = g("last_accounts_date")
    nard = g("nard")
    overdue = "true" if (nard and nard < today) else ("false" if nard else "")
    row.update(status=CRO_STATUS.get(st, st.lower() or "unknown"),
               status_detail=(g("company_status_date") + (" dissolved " + g("comp_dissolved_date") if g("comp_dissolved_date") else "")).strip(),
               incorporated=g("company_reg_date"), last_accounts_date=last_acc,
               last_accounts_type="", next_due=nard, accounts_overdue=overdue,
               sic=g("nace_v2_code").replace(".0", "") if g("nace_v2_code") else "",
               company_name=g("company_name"),
               note="CRO open data; charges are a paid document; overdue = next annual return date has passed")
    return row


# --------------------------------------------------------------------- TTB ----
def ttb_index() -> tuple[dict[str, dict], str]:
    if not TTB.exists():
        return {}, ""
    meta = TTB.with_suffix(".txt")
    fetched = ""
    if meta.exists():
        for line in meta.read_text().splitlines():
            if line.startswith("fetched:"):
                fetched = line.split(":", 1)[1].strip()
    with TTB.open(encoding="utf-8-sig", newline="") as fh:
        return {r["Permit_Number"]: r for r in csv.DictReader(fh)}, fetched


def ttb_read(idx: dict[str, dict], num: str, fetched: str) -> dict:
    r = idx.get(num)
    row = {"read_on": fetched, "source": TTB_PAGE}
    if not idx:
        row.update(status="unknown", note="TTB list not on disk; run match_ttb_permits.py --fetch")
    elif r:
        row.update(status="live", status_detail="new permit this week" if r.get("New_Permit_Flag") == "1" else "",
                   company_name=r["Owner_Name"], note="on the weekly TTB permittee list; a permit is permission, not a working still")
    else:
        row.update(status="dissolved", status_detail="permit no longer listed",
                   note="absent from the weekly TTB permittee list of " + fetched)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--fetch-ch", action="store_true", help="allow Companies House API requests")
    ap.add_argument("--cro", type=Path, help="CRO companies.csv.zip (open data)")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    today = time.strftime("%Y-%m-%d")
    key = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
    if a.fetch_ch and not key:
        print("COMPANIES_HOUSE_API_KEY not set", file=sys.stderr)
        return 2
    f = fetch.Fetcher(a.cache / "ch", allow=a.fetch_ch, cap=700, delay=0.6, log=a.cache / "requests.log")
    cro = cro_index(a.cro) if a.cro and a.cro.exists() else {}
    cro_date = time.strftime("%Y-%m-%d", time.localtime(a.cro.stat().st_mtime)) if cro else ""
    ttb, ttb_date = ttb_index()

    out = []
    comps = companies(XW)
    n = 0
    for (reg, num), c in sorted(comps.items()):
        base = {k: c.get(k, "") for k in ("registry", "company_number", "company_name", "country")}
        if reg == "companies-house":
            if a.limit and n >= a.limit:
                continue
            n += 1
            r = ch_read(f, key, num, today)
        elif reg == "cro":
            r = cro_read(cro, num, today, cro_date) if cro else {"status": "unknown", "read_on": today, "note": "pass --cro"}
        elif reg == "ttb-basic-permit":
            r = ttb_read(ttb, num, ttb_date)
        else:
            r = {"status": "unknown", "read_on": today, "note": f"no health reader for {reg} yet"}
        row = {k: "" for k in FIELDS}
        row.update(base)
        row.update({k: v for k, v in r.items() if k in FIELDS})
        out.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    SNAP.mkdir(exist_ok=True)
    (SNAP / f"{today}.csv").write_text(OUT.read_text())
    by = {}
    for r in out:
        by[(r["registry"], r["status"])] = by.get((r["registry"], r["status"]), 0) + 1
    print(f"{len(out)} companies -> {OUT.relative_to(ROOT)}; {f.summary()}")
    for k, v in sorted(by.items()):
        print(f"  {k[0]:20} {k[1]:22} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
