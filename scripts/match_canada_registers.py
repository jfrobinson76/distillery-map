#!/usr/bin/env python3
"""
Match the map's Canadian distilleries against free, permitted company registers and
liquor-licence lists, and write candidate rows for human review.

Registers and lists (research: docs/data-quality/canada-registers-2026-09-19.md):
  corporations-canada  Corporations Canada bulk CSVs (Open Government Licence - Canada),
                       matched locally: active CBCA, active non-CBCA, inactive CBCA.
  qc-req               NEQ taken from the RACJ alcohol-manufacturer permit register
                       (CC-BY 4.0). The REQ bulk zip itself is CC-BY-NC-SA and its
                       download endpoint returned 403 on 19 Sep 2026, so it is not used.
  bc-orgbook           OrgBook BC API v4 (OGL-BC + BC API terms). Only fetched with
                       --fetch-orgbook; responses are cached so reruns are offline.
  on-obr               Ontario Business Registry has no bulk file and no API. Rows are
                       derived from the AGCO manufacturer-licence list (legal entity
                       name); the OBR number is filled only when the legal name is a
                       numbered company ("1234567 Ontario Inc.").
  Licence layer        AGCO (ON), LCRB (BC), RACJ (QC) rows go to canada-licences.csv,
                       same schema, registries on-agco / bc-lcrb / qc-racj.
  Canada's Business Registries is NOT queried: its terms forbid automated tools.
  AB, SK, NS, NB, NL, MB have no free bulk file; those pins get federal rows only,
  plus hand cases below.

Run (offline, from cached files):
  python3 scripts/match_canada_registers.py --cache /path/to/cache
Fetch OrgBook (<= 1 request/second, hard cap 400, cached in <cache>/orgbook-cache.json):
  python3 scripts/match_canada_registers.py --cache /path/to/cache --fetch-orgbook

Cache dir must hold: corporations-active-cbca-en.csv, corporations-active-non-cbca-en.csv,
corporations-inactive-or-dissolved-cbca-en.csv, racj-alcool-fabricant.csv,
agco-manufacturers.csv, bc_liquor.xlsx. Missing files are skipped with a warning.
Idempotent: same inputs -> same outputs. Never fetches without --fetch-orgbook.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "canada-candidates.csv"
OUT_LICENCES = OUT_DIR / "canada-licences.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

SRC_FED = "https://open.canada.ca/data/en/dataset/0032ce54-c5dd-4b66-99a0-320a7b5e99f2"
SRC_RACJ = "https://www.donneesquebec.ca/recherche/dataset/racj-alcool-fabricant"
SRC_AGCO = "https://www.agco.ca/sites/default/files/opendata/OpenDataManufacturersLicences_En.csv"
SRC_LCRB = "https://catalogue.data.gov.bc.ca/dataset/licensed-establishments-in-b-c"
SRC_ORGBOOK = "https://orgbook.gov.bc.ca/api/v4/search/topic"
ORGBOOK_ENTITY = "https://orgbook.gov.bc.ca/entity/{}"

PROV_RE = re.compile(r",\s*(AB|BC|MB|NB|NL|NS|NT|NU|ON|PE|QC|SK|YT)\b")
SUFFIX = {"ltd", "limited", "inc", "incorporated", "incorporee", "corp", "corporation", "co",
          "company", "ltee", "limitee", "llc", "lp", "ulc", "sencrl", "senc", "enr", "the", "les",
          "le", "la", "de", "des", "du", "and", "of", "et", "a", "an"}
GENERIC = {"distillery", "distillerie", "distillers", "distilling", "distilleries", "distillateur",
           "distillateurs", "spirits", "spirit", "spiritueux", "craft", "artisanal", "artisanale",
           "micro", "microdistillerie", "microdistillery", "brewing", "brewery", "brewers",
           "winery", "cidery", "cidrerie", "vineyard", "vignoble", "estate", "farm", "farms"}
STOP = SUFFIX | GENERIC
COMMON_TOKEN_CAP = 4000  # skip index tokens with more postings than this (canada, group...)
SIGNAL = (GENERIC - {"estate", "farm", "farms", "vineyard", "vignoble", "craft", "micro"}) | {"whisky", "whiskey", "liquor", "liqueur", "liqueurs", "alcool", "alcools", "vodka", "gin",
                    "rum", "rhum", "moonshine", "beverage", "beverages", "boissons", "brasserie", "vin",
                    "vins", "wines", "cider", "cidre", "meadery", "hydromel", "still", "cask", "barrel"}

# Hand cases: relation known from industry knowledge, company checked on the register.
# number "" = not obtainable from a free register (paid provincial lookup needed).
HAND = {
    "hiram-walker-distillery": [
        ("on-obr", "", "Hiram Walker & Sons Limited", "self", "high",
         "Ontario corporation; Pernod Ricard subsidiary; OBR number needs a paid/portal lookup",
         "https://www.ontario.ca/page/ontario-business-registry"),
        ("corporations-canada", "3254381", "PERNOD RICARD CANADA LTÉE", "group", "high",
         "federal CBCA, Active, registered office Windsor ON; owner of Hiram Walker & Sons", SRC_FED),
    ],
    "lot-no-40-corby-distillery": [
        ("corporations-canada", "107611", "CORBY SPIRIT AND WINE LIMITED", "operator", "high",
         "federal CBCA, Active, Toronto ON; Lot No. 40 is a Corby brand distilled at Hiram Walker, Windsor", SRC_FED),
        ("on-obr", "", "Hiram Walker & Sons Limited", "operator", "high",
         "site operator (Windsor ON plant); Ontario corporation, number needs paid/portal lookup",
         "https://www.ontario.ca/page/ontario-business-registry"),
        ("corporations-canada", "3254381", "PERNOD RICARD CANADA LTÉE", "group", "high",
         "federal CBCA, Active, Windsor ON; majority owner of Corby", SRC_FED),
    ],
    "crown-royal-distillery": [
        ("corporations-canada", "10866512", "Diageo Canada Inc.", "operator", "high",
         "federal CBCA, Active, Toronto ON. Crown Royal is distilled at Gimli MB; the map pin is at "
         "The Forks, Winnipeg (visitor site), not the distillery", SRC_FED),
    ],
    "forty-creek": [
        ("corporations-canada", "9130403", "FORTY CREEK DISTILLERY LTD.", "self", "high",
         "federal CBCA, Active, Grimsby ON; Campari Group subsidiary since 2014", SRC_FED),
    ],
    "the-glenora-inn-distillery": [
        ("ns-rjsc", "", "Glenora Distillers International Limited", "self", "medium",
         "industry knowledge (Mabou NS); RJSC free search would give the registry ID but rjsc.novascotia.ca is Cloudflare-gated to scripts",
         "https://rjsc.novascotia.ca/"),
    ],
    "lucky-bastards-destillers": [
        ("sk-isc", "", "LB Distillers Inc.", "self", "medium",
         "industry knowledge (Saskatoon SK, trades as Lucky Bastard Distillers); ISC Corporate Registry lookup is paid",
         "https://www.saskregistries.ca/corporateregistry"),
    ],
    "alberta-distillers-limited": [
        ("ab-registry", "", "Alberta Distillers Limited", "self", "high",
         "Alberta corporation (Calgary); Suntory Global Spirits subsidiary; Alberta register is paid via registry agents",
         "https://www.alberta.ca/find-corporation-details"),
    ],
}
# Slugs that need a different search string than the pin name
ALIASES = {
    "crown-royal-distillery": ["Diageo Canada"],
    "lot-no-40-corby-distillery": ["Corby Spirit and Wine"],
    "hiram-walker-distillery": ["Hiram Walker & Sons"],
    "forty-creek": ["Forty Creek Distillery"],
    "alberta-distillers-limited": ["Alberta Distillers"],
    "still-waters-distillery": ["Still Waters Distillery"],
    "dillon-s-small-batch-distillers": ["Dillon's Small Batch Distillers", "Dillons Distillers"],
    "spirit-of-york-distillery-co": ["Spirit of York Distillery"],
    "lucky-bastards-destillers": ["Lucky Bastard Distillers", "LB Distillers"],
    "the-glenora-inn-distillery": ["Glenora Distillers International"],
    "okanagan-spirits-craft-distillery": ["Okanagan Spirits"],
    "sheringham-distillery": ["Sheringham Distillery"],
    "last-straw-distillery": ["Last Straw Distillery"],
    "shelter-point-distillery": ["Shelter Point Distillery"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str, keep_generic: bool = False) -> frozenset:
    stop = SUFFIX if keep_generic else STOP
    return frozenset(t for t in norm(s).split() if t not in stop)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def pin_city(addr: str) -> str:
    m = re.search(r",\s*([^,]+?),\s*(?:AB|BC|MB|NB|NL|NS|NT|NU|ON|PE|QC|SK|YT)\b", addr or "")
    return norm(m.group(1)).strip() if m else ""


def city_eq(a: str, b: str) -> bool:
    a, b = norm(a).strip(), norm(b).strip()
    return bool(a and b and (a == b or a in b or b in a))


def grade(j: float, exact: bool, city_ok: bool, prov_ok: bool, active: bool, distinctive: bool) -> str | None:
    if exact or j >= 0.8:
        if not active:
            return "medium"
        return "high" if (city_ok or distinctive) else "medium"
    if j >= 0.6:
        return "medium" if (city_ok or prov_ok) else "low"
    if j >= 0.4 and (city_ok or (prov_ok and distinctive)):
        return "low"
    return None


def exact_key(name: str) -> str:
    return " ".join(sorted(toks(name, keep_generic=True)))


def relation_for(pin_toks: frozenset, legal_name: str) -> str:
    """self when the legal name shares a distinctive token with the pin, else operator."""
    return "self" if pin_toks & toks(legal_name) else "operator"


def has_signal(name: str) -> bool:
    return bool(toks(name, keep_generic=True) & SIGNAL)


def adjust(g: str | None, pin_toks: frozenset, company_name: str, pin_city: str, company_city: str,
           j: float = 1.0) -> str | None:
    """Tighten a grade: single-token or partial-name matches need a drinks word in the company
    name; a known city conflict drops one level."""
    if not g:
        return None
    signal = has_signal(company_name)
    if (len(pin_toks) <= 1 or j < 0.8) and not signal:
        return None
    if pin_city and company_city and not city_eq(pin_city, company_city):
        g = {"high": "medium", "medium": "low", "low": None}[g]
    return g


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        if p.get("country") != "Canada":
            continue
        addr = p.get("address") or ""
        m = PROV_RE.search(addr)
        pins.append({"slug": p["slug"], "name": p["name"], "prov": m.group(1) if m else "",
                     "city": pin_city(addr), "toks": toks(p["name"]),
                     "full": toks(p["name"], keep_generic=True),
                     "aliases": ALIASES.get(p["slug"], [])})
    return pins


# ---------------------------------------------------------------- federal ----
def load_federal(cache: Path):
    rows, index, exact = [], defaultdict(list), defaultdict(list)
    files = [("corporations-active-cbca-en.csv", True), ("corporations-active-non-cbca-en.csv", True),
             ("corporations-inactive-or-dissolved-cbca-en.csv", False)]
    for fname, _ in files:
        path = cache / fname
        if not path.exists():
            print(f"warn: missing {path}", file=sys.stderr)
            continue
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                name = r.get("Corporate name - form 1") or ""
                name2 = r.get("Corporate name - form 2") or ""
                t = toks(name) | toks(name2)
                if not t:
                    continue
                i = len(rows)
                rows.append((r["Corporation number"], r.get("Business number (BN)", ""), name, name2,
                             r.get("Governing legislation", ""), r.get("Status", ""), r.get("Status Detail", ""),
                             r.get("City/town", ""), r.get("Province/territory", ""), r.get("Year of last annual filing", "")))
                for tok in t:
                    index[tok].append(i)
                exact[exact_key(name)].append(i)
                if name2:
                    exact[exact_key(name2)].append(i)
    print(f"federal: {len(rows)} corporations indexed", file=sys.stderr)
    return rows, index, exact


def federal_exact(fed, legal_name: str):
    """Rows whose corporate name equals legal_name once suffixes are stripped."""
    rows, _, exact = fed
    return [rows[i] for i in exact.get(exact_key(legal_name), [])] if legal_name else []


def federal_row(p, r, method, evidence, relation):
    note = (f"{evidence}; federal status {r[5]}{(' - ' + r[6]) if r[6] else ''}; "
            f"{r[4].replace('Canada Business Corporations Act', 'CBCA')}; registered office {r[7]}, {r[8]}; "
            f"BN {r[1] or 'n/a'}; last annual filing {r[9] or 'n/a'}")
    return [p["slug"], p["name"], "Canada", "corporations-canada", r[0], r[2], relation, method,
            "high" if r[5] == "Active" else "medium", "", SRC_FED, note]


def match_federal(pins, fed):
    rows, index, _ = fed
    out = []
    for p in pins:
        queries = [p["name"]] + p["aliases"]
        seen = {}
        for q in queries:
            qt = toks(q)
            if not qt:
                continue
            cand = set()
            for tok in qt:
                post = index.get(tok, [])
                if 0 < len(post) <= COMMON_TOKEN_CAP:
                    cand.update(post)
            for i in cand:
                r = rows[i]
                ct = toks(r[2]) | toks(r[3])
                j = jaccard(qt, ct)
                exact = norm(q) == norm(r[2]) or (toks(q, True) == toks(r[2], True))
                prov_ok = bool(p["prov"]) and r[8] == p["prov"]
                city_ok = city_eq(p["city"], r[7])
                active = r[5] == "Active"
                distinctive = len(qt) >= 2 and qt <= ct
                g = adjust(grade(j, exact, city_ok, prov_ok, active, distinctive), qt, r[2] + " " + r[3], p["city"], r[7], j)
                if not g:
                    continue
                if p["prov"] and r[8] and r[8] != p["prov"] and not exact:
                    continue  # federal rows carry the registered-office province; mismatch = other business
                score = j + (0.3 if active else 0) + (0.2 if city_ok else 0) + (0.1 if prov_ok else 0)
                note = (f"name jaccard {j:.2f}; status {r[5]}{(' - ' + r[6]) if r[6] else ''}; "
                        f"{r[4].replace('Canada Business Corporations Act', 'CBCA')}; "
                        f"registered office {r[7]}, {r[8]}{' (city agrees)' if city_ok else ''}; "
                        f"BN {r[1] or 'n/a'}; last annual filing {r[9] or 'n/a'}")
                key = r[0]
                if key not in seen or seen[key][0] < score:
                    seen[key] = (score, g, r, note)
        ranked = sorted(seen.values(), key=lambda x: -x[0])[:3]
        if any(x[1] == "high" for x in ranked):
            ranked = [x for x in ranked if x[1] != "low"]
        for score, g, r, note in ranked:
            out.append([p["slug"], p["name"], "Canada", "corporations-canada", r[0], r[2], "self",
                        "federal-bulk-name", g, "", SRC_FED, note])
    return out


# ------------------------------------------------------------------- RACJ ----
def load_racj(cache: Path):
    path = cache / "racj-alcool-fabricant.csv"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def match_racj(pins, racj, fed):
    cands, lic = [], []
    for p in pins:
        if p["prov"] not in ("QC", ""):
            continue
        best = {}
        for r in racj:
            for field in ("RaisonSociale", "Titulaire"):
                nm = r.get(field) or ""
                ct = toks(nm)
                j = jaccard(p["toks"], ct)
                exact = toks(p["name"], True) == toks(nm, True)
                city_ok = city_eq(p["city"], r.get("Ville", ""))
                distiller = r["TypePermis"] in ("Distillateur", "Production artisanale d’alcools et spiritueux",
                                                "Production artisanale d'alcools et spiritueux")
                g = grade(j, exact, city_ok, p["prov"] == "QC", True, len(p["toks"]) >= 2 and p["toks"] <= ct)
                if not g:
                    continue
                if not distiller and g != "high":
                    continue
                score = j + (0.3 if distiller else 0) + (0.2 if city_ok else 0)
                key = r["Neq"]
                if key not in best or best[key][0] < score:
                    best[key] = (score, g, r, j, city_ok)
        for score, g, r, j, city_ok in sorted(best.values(), key=lambda x: -x[0])[:2]:
            note = (f"name jaccard {j:.2f}; RACJ permit {r['NoPermis']} ({r['TypePermis']}) in force, "
                    f"{r['Ville']}{' (city agrees)' if city_ok else ''}; NEQ is the REQ register number; "
                    f"REQ status/incorporation date not checked (REQ bulk not used)")
            rel = relation_for(p["toks"], r["RaisonSociale"])
            cands.append([p["slug"], p["name"], "Canada", "qc-req", r["Neq"], r["RaisonSociale"], rel,
                          "racj-permit-name", g, "", SRC_RACJ, note])
            for fr in federal_exact(fed, r["RaisonSociale"])[:1]:
                cands.append(federal_row(p, fr, "racj-permit-name+federal-bulk",
                                         f"legal name from RACJ permit {r['NoPermis']} ({r['Ville']}), name jaccard {j:.2f}", rel))
            lic.append([p["slug"], p["name"], "Canada", "qc-racj", r["NoPermis"], r["Titulaire"], "self",
                        "racj-permit-name", g, "", SRC_RACJ,
                        f"{r['TypePermis']}; establishment {r['AdresseEtabl']}, {r['Ville']}; NEQ {r['Neq']}"])
    return cands, lic


# ------------------------------------------------------------------- AGCO ----
ON_NUMBERED = re.compile(r"^\s*(\d{6,8})\s+ontario\s+(inc|ltd|limited|corp|corporation)\b", re.I)


def load_agco(cache: Path):
    path = cache / "agco-manufacturers.csv"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [r for r in csv.DictReader(fh) if "Distillery" in r.get("Licence Type", "")]


def match_agco(pins, agco, fed):
    cands, lic = [], []
    for p in pins:
        if p["prov"] not in ("ON", ""):
            continue
        best = {}
        for r in agco:
            for field in ("Premises Name", "Legal Entity Name"):
                nm = r.get(field) or ""
                ct = toks(nm)
                j = jaccard(p["toks"], ct)
                exact = toks(p["name"], True) == toks(nm, True)
                city_ok = city_eq(p["city"], r.get("City", ""))
                active = r.get("Licence Status") in ("Active", "Deemed to Continue")
                g = grade(j, exact, city_ok, p["prov"] == "ON", active, len(p["toks"]) >= 2 and p["toks"] <= ct)
                if not g:
                    continue
                primary = r["Licence Type"].startswith("Manufacturer's Licence")
                score = j + (0.3 if active else 0) + (0.2 if city_ok else 0) + (0.1 if primary else 0)
                key = norm(r["Legal Entity Name"]).strip()
                if key not in best or best[key][0] < score:
                    best[key] = (score, g, r, j, city_ok, active)
        for score, g, r, j, city_ok, active in sorted(best.values(), key=lambda x: -x[0])[:2]:
            legal = r["Legal Entity Name"]
            m = ON_NUMBERED.match(legal)
            number = m.group(1) if m else ""
            note = (f"legal entity from AGCO licence {r['Licence Number']} ({r['Licence Type']}, {r['Licence Status']}, "
                    f"premises '{r['Premises Name'].strip()}', {r['City']}{' (city agrees)' if city_ok else ''}); "
                    f"name jaccard {j:.2f}; "
                    + ("OBR number = Ontario numbered-company name" if number else
                       "OBR number not obtainable without a portal lookup (no bulk, no API)"))
            rel = relation_for(p["toks"], legal)
            gg = g if active else ("medium" if g == "high" else g)
            fed_hits = federal_exact(fed, legal)
            if fed_hits:
                cands.append(federal_row(p, fed_hits[0], "agco-licence-name+federal-bulk",
                                         f"legal name from AGCO licence {r['Licence Number']} ({r['Licence Status']}, "
                                         f"premises '{r['Premises Name'].strip()}', {r['City']}), name jaccard {j:.2f}", rel))
            else:
                cands.append([p["slug"], p["name"], "Canada", "on-obr", number, legal, rel, "agco-licence-name",
                              gg, "", "https://www.ontario.ca/page/ontario-business-registry", note])
            lic.append([p["slug"], p["name"], "Canada", "on-agco", r["Licence Number"], legal, "self",
                        "agco-licence-name", g, "", SRC_AGCO,
                        f"{r['Licence Type']}; status {r['Licence Status']}; premises '{r['Premises Name'].strip()}', "
                        f"{r['Street Address']}, {r['City']}; issued {r['Issue Date']}, expires {r['Expiry Date']}"])
    return cands, lic


# ------------------------------------------------------------------- LCRB ----
def load_lcrb(cache: Path):
    path = cache / "bc_liquor.xlsx"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    z = zipfile.ZipFile(path)
    ss = re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8", "replace"), flags=re.S)
    strs = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", s, flags=re.S)) for s in ss]
    x = z.read("xl/worksheets/sheet1.xml").decode("utf-8", "replace")
    out, header = [], None
    for row in re.findall(r"<row[^>]*>(.*?)</row>", x, flags=re.S):
        cells = {}
        for m in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', row, flags=re.S):
            col, attrs, inner = m.groups()
            v = re.search(r"<v>(.*?)</v>", inner)
            v = v.group(1) if v else ""
            if 't="s"' in attrs:
                v = strs[int(v)]
            cells[col] = v.replace("&amp;", "&")
        if header is None:
            header = cells
            continue
        rec = {header[k]: v for k, v in cells.items() if k in header}
        if rec.get("Licence Type") == "Manufacturer" and rec.get("Licence Sub Category Id") == "Distillery":
            out.append(rec)
    print(f"lcrb: {len(out)} distillery manufacturer licences", file=sys.stderr)
    return out


def match_lcrb(pins, lcrb, fed):
    """Return {slug: [(licence row, grade, j, city_ok)]}, licence-layer rows, federal rows."""
    hits, lic, fed_rows = {}, [], []
    for p in pins:
        if p["prov"] not in ("BC", ""):
            continue
        best = {}
        for r in lcrb:
            est = re.sub(r"\s*\(\d+\)\s*$", "", r.get("Establishment") or "")
            for nm in (est, r.get("Licensee") or ""):
                ct = toks(nm)
                j = jaccard(p["toks"], ct)
                exact = toks(p["name"], True) == toks(nm, True)
                city_ok = city_eq(p["city"], r.get("Establishment Address City", ""))
                g = grade(j, exact, city_ok, p["prov"] == "BC", True, len(p["toks"]) >= 2 and p["toks"] <= ct)
                if not g:
                    continue
                score = j + (0.2 if city_ok else 0)
                key = r["Licence Number"]
                if key not in best or best[key][0] < score:
                    best[key] = (score, g, r, j, city_ok, est)
        ranked = sorted(best.values(), key=lambda x: -x[0])[:2]
        hits[p["slug"]] = ranked
        for score, g, r, j, city_ok, est in ranked:
            lic.append([p["slug"], p["name"], "Canada", "bc-lcrb", r["Licence Number"], r.get("Licensee", ""), "self",
                        "lcrb-establishment-name", g, "", SRC_LCRB,
                        f"Manufacturer - Distillery; establishment '{est}', {r.get('Establishment Address Street', '')}, "
                        f"{r.get('Establishment Address City', '')}{' (city agrees)' if city_ok else ''}; name jaccard {j:.2f}"])
            for fr in federal_exact(fed, r.get("Licensee", ""))[:1]:
                fed_rows.append(federal_row(p, fr, "lcrb-licensee+federal-bulk",
                                            f"licensee of LCRB licence {r['Licence Number']} ('{est}', "
                                            f"{r.get('Establishment Address City', '')}), name jaccard {j:.2f}",
                                            relation_for(p["toks"], r.get("Licensee", ""))))
    return hits, lic, fed_rows


# ---------------------------------------------------------------- OrgBook ----
class OrgBook:
    def __init__(self, cache_file: Path, fetch: bool, cap: int = 400):
        self.cache_file = cache_file
        self.cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
        self.fetch = fetch
        self.cap = cap
        self.requests = 0
        self.last = 0.0

    def search(self, q: str):
        key = norm(q).strip()
        if key in self.cache:
            return self.cache[key]
        if not self.fetch:
            return None
        if self.requests >= self.cap:
            print("orgbook: request cap reached", file=sys.stderr)
            return None
        wait = 1.0 - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        url = SRC_ORGBOOK + "?" + urllib.parse.urlencode({"q": q})  # current registrations only
        req = urllib.request.Request(url, headers={"User-Agent": "stillbound-distillery-map crosswalk (stdlib urllib)"})
        self.last = time.time()
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:  # noqa: BLE001
            print(f"orgbook: {q!r} failed: {e}", file=sys.stderr)
            return None
        slim = []
        for r in data.get("results", []):
            at = {a["type"]: a["value"] for a in r.get("attributes", [])}
            slim.append({"id": r["source_id"], "names": [n["text"] for n in r.get("names", []) if n.get("type") == "entity_name"],
                         "bn": next((n["text"] for n in r.get("names", []) if n.get("type") == "business_number"), ""),
                         "status": at.get("entity_status", ""), "type": at.get("entity_type", ""),
                         "registered": (at.get("registration_date") or "")[:10], "home": at.get("home_jurisdiction", "")})
        self.cache[key] = slim
        self.cache_file.write_text(json.dumps(self.cache, indent=1, ensure_ascii=False))
        return slim


def match_orgbook(pins, lcrb_hits, ob: OrgBook):
    out = []
    for p in pins:
        if p["prov"] not in ("BC", ""):
            continue
        if p["prov"] == "" and not lcrb_hits.get(p["slug"]):
            continue  # no evidence the pin is in BC
        queries = []
        for score, g, r, j, city_ok, est in lcrb_hits.get(p["slug"], []):
            lic = r.get("Licensee") or ""
            if lic and "," not in lic:  # comma = list of individuals (sole props/partners)
                queries.append((lic, f"via LCRB licence {r['Licence Number']} licensee"))
        queries.append((p["name"], "via pin name"))
        for a in p["aliases"]:
            queries.append((a, "via alias"))
        seen = {}
        for q, how in queries:
            res = ob.search(q)
            if res is None:
                continue
            qt, qfull = toks(q), toks(q, True)
            for r in res:
                for nm in r["names"]:
                    ct = toks(nm)
                    j = jaccard(qt, ct)
                    exact = qfull == toks(nm, True)
                    active = r["status"] == "ACT"
                    if how.startswith("via LCRB"):
                        # the licensee name is the legal name: only an exact hit is high
                        if exact:
                            g = "high" if active else "medium"
                        elif j >= 0.8:
                            g = "medium"
                        elif j >= 0.6 and has_signal(nm):
                            g = "low"
                        else:
                            g = None
                    else:
                        g = adjust(grade(j, exact, False, True, active, len(qt) >= 2 and qt <= ct), qt, nm, "", "", j)
                    if not g:
                        continue
                    score = j + (0.3 if active else 0) + (0.3 if how.startswith("via LCRB") else 0) + (0.2 if exact else 0)
                    key = r["id"]
                    if key not in seen or seen[key][0] < score:
                        seen[key] = (score, g, r, nm, j, how)
        ranked = sorted(seen.values(), key=lambda x: -x[0])[:3]
        if any(x[1] == "high" for x in ranked):
            ranked = [x for x in ranked if x[1] != "low"]
        for score, g, r, nm, j, how in ranked:
            if r["type"] in ("SP", "GP") and g == "high":
                g = "medium"  # firm-name registration (sole prop / partnership), not a company
            note = (f"name jaccard {j:.2f} {how}; BC Registries {r['id']} status {r['status']} type {r['type']}"
                    f"{' (firm name, not a company)' if r['type'] in ('SP', 'GP') else ''}; "
                    f"registered {r['registered'] or 'n/a'}; BN {r['bn'] or 'n/a'}; home {r['home'] or 'BC'}")
            out.append([p["slug"], p["name"], "Canada", "bc-orgbook", r["id"], nm, relation_for(p["toks"], nm), "orgbook-topic-search",
                        g, "", ORGBOOK_ENTITY.format(r["id"]), note])
    return out


# ------------------------------------------------------------------- main ----
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory holding the downloaded bulk files")
    ap.add_argument("--fetch-orgbook", action="store_true", help="allow OrgBook BC API requests (cached)")
    args = ap.parse_args()
    cache = Path(args.cache).expanduser()

    pins = load_pins()
    print(f"{len(pins)} Canadian pins", file=sys.stderr)

    fed = load_federal(cache)
    cands = match_federal(pins, fed)
    racj_c, racj_l = match_racj(pins, load_racj(cache), fed)
    agco_c, agco_l = match_agco(pins, load_agco(cache), fed)
    lcrb_hits, lcrb_l, lcrb_fed = match_lcrb(pins, load_lcrb(cache), fed)
    cands += lcrb_fed
    ob = OrgBook(cache / "orgbook-cache.json", args.fetch_orgbook)
    ob_c = match_orgbook(pins, lcrb_hits, ob)
    print(f"orgbook: {ob.requests} requests this run (cap {ob.cap}), {len(ob.cache)} cached queries", file=sys.stderr)

    hand = []
    for slug, rows in HAND.items():
        p = next((x for x in pins if x["slug"] == slug), None)
        if not p:
            continue
        for reg, num, name, rel, conf, note, src in rows:
            hand.append([slug, p["name"], "Canada", reg, num, name, rel, "hand", conf, "", src, note])

    all_rows = hand + cands + racj_c + agco_c + ob_c
    # a hand row for (slug, registry, number) replaces the machine row
    hand_keys = {(r[0], r[3], r[4]) for r in hand}
    hand_names = {(r[0], r[3], norm(r[5]).strip()) for r in hand}
    conf_rank = {"high": 0, "medium": 1, "low": 2}
    machine = {}
    for r in cands + racj_c + agco_c + ob_c:
        if (r[0], r[3], r[4]) in hand_keys or (r[0], r[3], norm(r[5]).strip()) in hand_names:
            continue
        k = (r[0], r[3], r[4] or norm(r[5]).strip())
        if k not in machine or conf_rank[r[8]] < conf_rank[machine[k][8]]:
            machine[k] = r
    final = hand + list(machine.values())
    order = {s["slug"]: i for i, s in enumerate(pins)}
    final.sort(key=lambda r: (order[r[0]], r[3], conf_rank[r[8]], r[5]))
    licences = sorted(racj_l + agco_l + lcrb_l, key=lambda r: (order[r[0]], r[3], conf_rank[r[8]]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, rows in ((OUT_CANDIDATES, final), (OUT_LICENCES, licences)):
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            w.writerows(rows)

    # summary
    by_prov = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    best = {}
    for r in final:
        best[r[0]] = min(best.get(r[0], 9), conf_rank[r[8]])
    for p in pins:
        d = by_prov[p["prov"] or "(none)"]
        d["pins"] += 1
        if p["slug"] in best:
            d[["high", "medium", "low"][best[p["slug"]]]] += 1
        else:
            d["unmatched"] += 1
    print("prov pins high medium low unmatched")
    for prov in sorted(by_prov, key=lambda k: -by_prov[k]["pins"]):
        d = by_prov[prov]
        print(f"{prov:6} {d['pins']:4} {d['high']:4} {d['medium']:6} {d['low']:3} {d['unmatched']:9}")
    tot = {k: sum(d[k] for d in by_prov.values()) for k in ("pins", "high", "medium", "low", "unmatched")}
    print(f"total  {tot['pins']:4} {tot['high']:4} {tot['medium']:6} {tot['low']:3} {tot['unmatched']:9}")
    print("unmatched:", " ".join(p["slug"] for p in pins if p["slug"] not in best))
    print(f"{len(final)} candidate rows -> {OUT_CANDIDATES.relative_to(ROOT)}; "
          f"{len(licences)} licence rows -> {OUT_LICENCES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
