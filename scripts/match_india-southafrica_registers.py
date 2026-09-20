#!/usr/bin/env python3
"""
Match the map's Indian and South African distilleries against the free, permitted sources
found on 20 Sep 2026 and write candidate rows for human review.

Research: docs/data-quality/india-southafrica-registers-2026-09-20.md

India
  in-mca        Ministry of Corporate Affairs company master data, via the data.gov.in
                state-wise CSV extracts (Government Open Data License - India, snapshot
                "upto Mar 2015"). Matched locally. The MCA21 portal itself (mca.gov.in)
                answered 403 "Access Denied" (Akamai) to every request from this network
                and was not queried.
  in-goa-excise Goa Excise "Contact Us" page lists the manufacturing units per excise
                station (name + unit type, no licence number). Licence-layer rows only.
  Maharashtra's licensee search returned a server-side error on every query; Karnataka
  and Punjab excise sites were unreachable. No other state list was found.

South Africa
  za-cipc       CIPC has no open-data extract and its terms forbid "any technology to
                search and gain any information from this site". CIPC is NOT queried.
                Registration numbers (YYYY/NNNNNN/NN) are taken from the distilleries'
                own websites (legal footer / terms page) with --fetch-websites.
  SARS excise licences and provincial liquor-board registers are not published.

Both countries
  website-regno The distillery website sweep: homepage plus up to two legal/contact/about
                pages per site, regex for an Indian CIN or a South African registration
                number. <= 1 request/second, hard cap 400 requests per run, cached.

Run (offline, from cached files):
  python3 scripts/match_india-southafrica_registers.py --cache DIR
Fetch (each flag is explicit; nothing is fetched without one):
  --fetch-mca-states   download the data.gov.in state CSVs for the states with pins
  (the Goa Excise contact page is read from <cache>/goa-contact_us.html; excise.goa.gov.in
   serves an incomplete TLS chain, so the page was saved by hand once, see the research note)
  --fetch-websites     sweep pin websites for CIN / registration numbers (cached JSON)

Cache layout: <cache>/mca/<State>.csv, <cache>/goa-contact_us.html, <cache>/websites.json
Idempotent: same inputs -> same outputs.
"""
from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "india-southafrica-candidates.csv"
OUT_LICENCES = OUT_DIR / "india-southafrica-licences.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

SRC_MCA = "https://www.data.gov.in/catalog/company-master-data"
MCA_FILE = "https://data.gov.in/sites/default/files/dataurl15092015/company_master_data_upto_Mar_2015_{}.csv"
SRC_GOA = "https://excise.goa.gov.in/contact_us.aspx"
SRC_CIPC = "https://eservices.cipc.co.za/"
UA = "stillbound-distillery-map crosswalk (stdlib urllib; research contact via stillbound.ai)"
REQUEST_CAP = 400

# Indian states as they appear in pin addresses -> data.gov.in file name
STATE_FILES = {
    "Andhra Pradesh": "Andhra_Pradesh", "Assam": "Assam", "Bihar": "Bihar", "Chandigarh": "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu": "Daman_and_Diu", "Daman and Diu": "Daman_and_Diu",
    "Delhi": "Delhi", "Goa": "Goa", "Gujarat": "Gujarat", "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal_Pradesh", "Karnataka": "Karnataka", "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya_Pradesh", "Maharashtra": "Maharashtra", "Odisha": "Odisha",
    "Puducherry": "Puducherry", "Punjab": "Punjab", "Rajasthan": "Rajasthan", "Tamil Nadu": "Tamil_Nadu",
    "Telangana": "Telangana", "Uttar Pradesh": "Uttar_Pradesh", "West Bengal": "West_Bengal",
}
# CIN positions 8-9 carry the state of registration
CIN_STATE = {"AP": "Andhra Pradesh", "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "DN": "Dadra and Nagar Haveli",
             "DD": "Daman and Diu", "DL": "Delhi", "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh",
             "KA": "Karnataka", "KL": "Kerala", "MP": "Madhya Pradesh", "MH": "Maharashtra", "OR": "Odisha",
             "PY": "Puducherry", "PB": "Punjab", "RJ": "Rajasthan", "TN": "Tamil Nadu", "TG": "Telangana",
             "UP": "Uttar Pradesh", "WB": "West Bengal", "UR": "Uttarakhand", "JH": "Jharkhand", "CT": "Chhattisgarh"}

SUFFIX = {"ltd", "limited", "pvt", "private", "p", "llp", "inc", "co", "company", "corp", "corporation",
          "pty", "cc", "npc", "the", "of", "and", "a", "an", "m", "s", "ms", "unit", "units", "division",
          "head", "office", "corporate", "plant", "manufacturing", "india", "indian", "sa", "south", "africa"}
GENERIC = {"distillery", "distilleries", "distillers", "distilling", "distillation", "distil", "spirits", "spirit",
           "craft", "artisanal", "boutique", "micro", "brewery", "breweries", "brewers", "brewing", "brewhouse",
           "winery", "wineries", "wine", "wines", "estate", "farm", "gin", "brandy", "beverages", "beverage",
           "liquor", "liquors", "blenders", "bottlers", "bottling", "cellar", "cellars", "tours", "tasting",
           "bar", "restaurant", "venue", "backpackers", "pick", "up"}
STOP = SUFFIX | GENERIC
SIGNAL = {"distillery", "distilleries", "distillers", "distilling", "spirits", "spirit", "liquor", "liquors",
          "brewery", "breweries", "brewers", "brewing", "winery", "wineries", "wine", "wines", "beverages",
          "beverage", "blenders", "bottlers", "bottling", "gin", "brandy", "rum", "vodka", "whisky", "whiskey",
          "sugar", "sugars", "alcohol", "alcohols", "vintners", "cellar", "cellars"}
COMMON_TOKEN_CAP = 3000

CIN_RE = re.compile(r"\b([LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})\b")
ZA_RE = re.compile(r"\b((?:19|20)\d{2}\s?/\s?\d{6}\s?/\s?\d{2})\b")

# Hand cases. The company number is resolved from the local MCA files by exact legal name
# (India) or from the website sweep (South Africa); it is never typed in from memory.
# (slug, legal name, relation, confidence, note)
HAND_IN = [
    ("amrut-distillery", "AMRUT DISTILLERIES LIMITED", "self", "high",
     "Amrut Distilleries, Bengaluru (Kambipura plant); 2015 snapshot name is Amrut Distilleries Limited (now Private Limited). The pin sits at UB Tower, Diageo India's office, not the "
     "distillery; two other pins (amrut-distilleries-pvt-ltd, amrut-distilleries-private-limited) carry the plant and HQ"),
    ("amrut-distilleries-pvt-ltd", "AMRUT DISTILLERIES LIMITED", "self", "high", "Kambipura plant, Mysore Road"),
    ("amrut-distilleries-private-limited", "AMRUT DISTILLERIES LIMITED", "self", "high", "registered/head office pin"),
    ("paul-john-distillery", "JOHN DISTILLERIES PRIVATE LIMITED", "self", "high",
     "Paul John single malt is made by John Distilleries at Cuncolim, Goa; Goa Excise lists 'M/s. John Distilleries Ltd. "
     "(Distillery/Winery)' under Excise Station Salcete/Cuncolim; company registered in Karnataka (Bengaluru)"),
    ("rampur-distillery-a-unit-of-radico-khaitan-limited", "RADICO KHAITAN LIMITED", "self", "high",
     "Rampur Distillery is Radico Khaitan's own plant (Rampur UP)"),
    ("radico-nv-distilleries-maharashtra-ltd", "RADICO NV DISTILLERIES MAHARASHTRA LIMITED", "self", "high",
     "Radico Khaitan / NV Distilleries joint venture, Aurangabad MH"),
    ("radico-nv-distilleries-maharashtra-ltd", "RADICO KHAITAN LIMITED", "group", "high", "JV partner and brand owner"),
    ("allied-blenders-and-distillers-pvt-ltd", "ALLIED BLENDERS AND DISTILLERS PRIVATE LIMITED", "self", "high",
     "ABD (Officer's Choice); listed as Allied Blenders and Distillers Limited since 2024, 2015 snapshot shows the private-company name"),
    ("allied-blenders-and-distillers-limited", "ALLIED BLENDERS AND DISTILLERS PRIVATE LIMITED", "self", "high",
     "ABD's Rangapur (Telangana) distillery; company renamed Allied Blenders and Distillers Limited on listing in 2024"),
    ("allied-blenders-distillers-private-limited-gaganpahad", "ALLIED BLENDERS AND DISTILLERS PRIVATE LIMITED", "operator", "high",
     "ABD site (pin geocoded to Tumkur Road, Bengaluru; slug says Gaganpahad, Hyderabad)"),
    ("allied-blenders-and-distillers-pvt-ltd-kalyani", "ALLIED BLENDERS AND DISTILLERS PRIVATE LIMITED", "operator", "high",
     "ABD bottling unit, Kalyani WB"),
    ("allied-blenders-and-distillers-saha-ambala", "ALLIED BLENDERS AND DISTILLERS PRIVATE LIMITED", "operator", "high",
     "ABD unit, Saha industrial growth centre, Ambala HR"),
    ("anheuser-busch-inbev-india-ltd-unit-spr-distilleries-pvt-ltd", "SPR DISTILLERIES PRIVATE LIMITED", "self", "high",
     "SPR Distilleries, Maliyuru, T. Narasipura KA; the pin name says it is an AB InBev India unit"),
    ("central-distillery-and-breweries-anheuser-busch-inbev-india-limited", "SABMILLER INDIA LIMITED", "operator", "medium",
     "Central Distillery and Breweries, Meerut UP, named on the pin as an AB InBev India unit; the 2015 snapshot carries the pre-merger name SABMiller India Limited (renamed Anheuser Busch InBev India Limited after 2016)"),
    ("dcm-shriram-ltd-distillery-unit-hariawan", "DCM SHRIRAM LIMITED", "operator", "high", "DCM Shriram's Hariawan (Hardoi UP) sugar-distillery complex"),
    ("bannari-amman-sugars-ltd-distillery-division", "BANNARI AMMAN SUGARS LIMITED", "operator", "high", "distillery division of a listed sugar company, Erode TN"),
    ("nirani-sugars-ltd-distillery", "NIRANI SUGARS LIMITED", "operator", "high", "distillery of a sugar company, Mudhol/Bagalkot KA"),
    ("new-phaltan-sugar-works-distillery-division-ltd", "NEW PHALTAN SUGAR WORKS DISTILLERY DIVISION LIMITED", "self", "high", "a separate company (2013) carrying the distillery division; pin geocoded to a Pune office"),
    ("new-phaltan-sugar-works-distillery-division-ltd", "NEW PHALTAN SUGAR WORKS LTD", "group", "high", "parent sugar company, Phaltan MH"),
    ("new-phaltan-distillery-factory", "NEW PHALTAN SUGAR WORKS DISTILLERY DIVISION LIMITED", "operator", "high", "the Suravadi/Phaltan plant itself"),
    ("simbhaoli-distillery", "SIMBHAOLI SPIRITS LIMITED", "self", "high", "Simbhaoli Sugars' distillery subsidiary, Simbhaoli UP"),
    ("simbhaoli-distillery", "SIMBHAOLI SUGARS LIMITED", "group", "medium", "parent sugar company (2015 name)"),
    ("modi-distillery-modi-sugar-mill", "MODI INDUSTRIES LIMITED", "operator", "medium", "Modi Distillery is a unit of Modi Industries, Modinagar UP"),
    ("brima-sagar-maharashtra-distilleries-ltd", "TILAKNAGAR INDUSTRIES LIMITED", "group", "medium", "Brima Sagar Maharashtra Distilleries is a Tilaknagar Industries subsidiary (Mansion House brandy)"),
    ("alcobrew-distilleries-india-ltd", "ALCOBREW DISTILLERIES INDIA PRIVATE LIMITED", "self", "high", "head office pin, Gurugram HR; 2015 snapshot name (private), later Alcobrew Distilleries India Limited"),
    ("inbrew-beverages-pvt-ltd-b-t-w-kbd-sugars-and-distilleries-pvt-ltd", "KBD SUGARS & DISTILLERIES LIMITED", "self", "high",
     "pin name says Inbrew Beverages (incorporated after the 2015 snapshot) trading at the KBD Sugars and Distilleries site"),
    ("chandigarh-distillers-bottlers-ltd-cdb-group", "CHANDIGARH DISTILLERS AND BOTTLERS LIMITED", "self", "high", "CDB group head office pin"),
    ("gemini-distilleries-goa-private-limited", "GEMINI DISTILLERIES (GOA) PRIVATE LIMITED", "self", "high", "Sancoale industrial estate; on the Goa Excise unit list"),
    ("shaiv-distilleries-private-limited", "SHAIV DISTILLERIES PRIVATE LIMITED", "self", "high", "Bicholim industrial estate; 2015 file address agrees"),
    ("adinco-distilleries", "ADINCO DISTILLERIES PRIVATE LIMITED", "self", "high", "on the Goa Excise unit list (Quepem); 2015 file"),
    ("fullarton-distilleries", "FULLARTON DISTILLERIES PRIVATE LIMITED", "self", "high", "on the Goa Excise unit list (Ponda); 2015 file"),
    ("ocean-king-distillers", "OCEANKING DISTILLERS PRIVATE LIMITED", "self", "medium", "Goa Excise lists 'M/s. Oceanking Distillers (Distillery/Winery/Bottling of CL)' under Salcete; company form not confirmed"),
    ("the-east-side-distillery", "NAVEEN DISTILLERY PRIVATE LIMITED", "operator", "medium",
     "pin address is 'Shed A2/1, Naveen Distillery, Margao Industrial Estate'; Goa Excise lists 'M/s. Naveen Distillery (Distillery/Winery/Bottling of CL)' under Salcete. Doja gin is made there; company form not confirmed"),
]
# South Africa hand cases: (slug, legal name, relation, confidence, note). Numbers come from the
# website sweep when the site prints one; otherwise the number stays blank (CIPC not queried).
HAND_ZA = [
    ("james-sedgwick-distillery", "Heineken Beverages (South Africa) (Pty) Ltd", "operator", "high",
     "James Sedgwick Distillery, Wellington: Distell's whisky distillery; Distell merged into Heineken Beverages in 2023"),
    ("van-ryn-s-distillery-and-brandy-cellar", "Heineken Beverages (South Africa) (Pty) Ltd", "operator", "high",
     "Van Ryn's, Vlottenburg/Stellenbosch: Distell brandy distillery, now Heineken Beverages"),
    ("klipdrift-brandy", "Heineken Beverages (South Africa) (Pty) Ltd", "operator", "high",
     "Klipdrift distillery, Robertson: Distell brandy site, now Heineken Beverages"),
    ("boplaas-winery-and-distillery", "Boplaas Familie Wingerde (Pty) Ltd", "self", "medium", "Boplaas family estate, Calitzdorp; legal form from industry knowledge, number needs CIPC"),
    ("inverroche-distillery", "Inverroche Distillery (Pty) Ltd", "self", "medium", "Still Bay; Pernod Ricard took a majority stake in 2019; number needs CIPC"),
    ("hope-distillery", "Hope on Hopkins Distillery (Pty) Ltd", "self", "medium", "trades as Hope Distillery (Hope on Hopkins), Salt River; number needs CIPC"),
    ("mirari-gin-time-anchor-distillery", "Time Anchor Distillery (Pty) Ltd", "self", "medium", "Mirari gin, Sandton; number needs CIPC"),
    ("wilderer-gin", "Wilderer Distillery (Pty) Ltd", "self", "medium", "Wilderer, Simondium/Paarl; number needs CIPC"),
    ("oude-molen-distillery", "Edward Snell & Co. (Pty) Ltd", "operator", "medium", "Oude Molen brandy distillery, Grabouw, is run by Edward Snell & Co; number needs CIPC"),
]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str, keep_generic: bool = False) -> frozenset:
    stop = SUFFIX if keep_generic else STOP
    return frozenset(t for t in norm(s).split() if t not in stop)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def exact_key(name: str) -> str:
    return " ".join(sorted(toks(name, keep_generic=True)))


def has_signal(name: str) -> bool:
    return bool(toks(name, keep_generic=True) & SIGNAL)


def grade(j: float, exact: bool, city_ok: bool, state_ok: bool, active: bool, distinctive: bool) -> str | None:
    if exact or j >= 0.8:
        if not active:
            return "medium"
        return "high" if (city_ok or distinctive) else "medium"
    if j >= 0.6:
        return "medium" if (city_ok or state_ok) else "low"
    if j >= 0.4 and (city_ok or (state_ok and distinctive)):
        return "low"
    return None


def relation_for(pin_toks: frozenset, legal_name: str) -> str:
    return "self" if pin_toks & toks(legal_name) else "operator"


# ------------------------------------------------------------------- pins ----
ZA_POSTAL = [  # coarse South African postal-code bands -> province, for the summary table only
    (1, 299, "Gauteng"), (300, 499, "North West"), (500, 999, "Limpopo"), (1000, 1099, "Mpumalanga"),
    (1100, 1399, "Mpumalanga"), (1400, 2199, "Gauteng"), (2200, 2499, "Mpumalanga"), (2500, 2899, "North West"),
    (2900, 2999, "KwaZulu-Natal"), (3000, 4730, "KwaZulu-Natal"), (4731, 6499, "Eastern Cape"),
    (6500, 8099, "Western Cape"), (8100, 8999, "Northern Cape"), (9000, 9299, "Free State"), (9300, 9999, "Free State"),
]


def in_state(addr: str) -> str:
    for st in sorted(STATE_FILES, key=len, reverse=True):
        if re.search(r"\b" + re.escape(st) + r"\b", addr):
            return "Dadra and Nagar Haveli and Daman and Diu" if st == "Daman and Diu" else st
    return ""


def in_city(addr: str, state: str) -> str:
    """Token before the state in 'street, City, State PIN, India'."""
    if not state:
        return ""
    m = re.search(r",\s*([^,]+?),\s*" + re.escape(state.split(" and ")[0]), addr)
    return norm(m.group(1)).strip() if m else ""


def za_region(addr: str) -> str:
    m = re.search(r"\b(\d{4})\b,\s*South Africa", addr or "")
    if not m:
        return ""
    code = int(m.group(1))
    return next((p for lo, hi, p in ZA_POSTAL if lo <= code <= hi), "")


def za_city(addr: str) -> str:
    parts = [p.strip() for p in (addr or "").split(",")]
    parts = [p for p in parts if p and not re.fullmatch(r"\d{4}", p) and p != "South Africa"]
    return norm(parts[-1]).strip() if parts else ""


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        c = p.get("country")
        if c not in ("India", "South Africa"):
            continue
        addr = p.get("address") or ""
        if c == "India":
            st = in_state(addr)
            city = in_city(addr, st)
        else:
            st = za_region(addr)
            city = za_city(addr)
        pins.append({"slug": p["slug"], "name": p["name"], "country": c, "region": st, "city": city,
                     "addr": addr, "website": (p.get("website") or "").strip(),
                     "toks": toks(p["name"]), "full": toks(p["name"], keep_generic=True)})
    return pins


# -------------------------------------------------------------------- MCA ----
def fetch_mca_states(cache: Path, pins, log):
    d = cache / "mca"
    d.mkdir(parents=True, exist_ok=True)
    wanted = sorted({STATE_FILES[p["region"]] for p in pins if p["country"] == "India" and p["region"] in STATE_FILES}
                    | {STATE_FILES[s] for s in ("Daman and Diu",)})
    for st in wanted:
        path = d / f"{st}.csv"
        if path.exists() and path.stat().st_size > 0:
            continue
        url = MCA_FILE.format(st)
        log.hit("data.gov.in file")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                path.write_bytes(r.read())
            print(f"mca: fetched {st} ({path.stat().st_size} bytes)", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"mca: {st} failed: {e}", file=sys.stderr)
        time.sleep(1.0)


def load_mca(cache: Path):
    rows, index, exact, by_cin = [], defaultdict(list), defaultdict(list), {}
    files = sorted((cache / "mca").glob("*.csv")) if (cache / "mca").exists() else []
    if not files:
        print(f"warn: no MCA state files in {cache / 'mca'}", file=sys.stderr)
    for path in files:
        n = 0
        with path.open(encoding="utf-8", errors="replace", newline="") as fh:
            for r in csv.DictReader(fh):
                cin = (r.get("CORPORATE_IDENTIFICATION_NUMBER") or "").strip()
                name = (r.get("COMPANY_NAME") or "").strip()
                if not cin or not name:
                    continue
                t = toks(name)
                i = len(rows)
                rows.append((cin, name, (r.get("COMPANY_STATUS") or "").strip(), (r.get("DATE_OF_REGISTRATION") or "").strip(),
                             (r.get("REGISTERED_STATE") or "").strip(), (r.get("REGISTRAR_OF_COMPANIES") or "").strip(),
                             (r.get("REGISTERED_OFFICE_ADDRESS") or "").strip(), (r.get("COMPANY_CLASS") or "").strip(),
                             (r.get("PRINCIPAL_BUSINESS_ACTIVITY") or "").strip()))
                for tok in t:
                    index[tok].append(i)
                exact[exact_key(name)].append(i)
                by_cin[cin] = i
                n += 1
        print(f"mca: {path.name} {n} companies", file=sys.stderr)
    print(f"mca: {len(rows)} companies indexed from {len(files)} state files", file=sys.stderr)
    return rows, index, exact, by_cin


def mca_note(r, j=None, city_ok=False, extra=""):
    addr = re.sub(r"\s+", " ", r[6])[:90]
    bits = []
    if j is not None:
        bits.append(f"name jaccard {j:.2f}")
    if extra:
        bits.append(extra)
    bits.append(f"MCA status {r[2]} (2015 snapshot)")
    bits.append(f"registered {r[3]}, ROC {r[5]}, {r[4]}")
    bits.append(f"registered office {addr}{' (city agrees)' if city_ok else ''}")
    if r[8]:
        bits.append(f"activity: {r[8]}")
    return "; ".join(bits)


def mca_row(p, r, method, conf, relation, note):
    return [p["slug"], p["name"], "India", "in-mca", r[0], r[1], relation, method, conf, "", SRC_MCA, note]


def match_mca(pins, mca):
    rows, index, _, _ = mca
    out = []
    for p in pins:
        if p["country"] != "India":
            continue
        qt = p["toks"]
        if not qt:
            continue
        cand = set()
        for tok in qt:
            post = index.get(tok, [])
            if 0 < len(post) <= COMMON_TOKEN_CAP:
                cand.update(post)
        seen = {}
        for i in cand:
            r = rows[i]
            ct = toks(r[1])
            j = jaccard(qt, ct)
            exact = p["full"] == toks(r[1], True)
            state_ok = bool(p["region"]) and (r[4].lower() == p["region"].lower() or
                                              (p["region"].startswith("Dadra") and r[4] in ("Daman and Diu", "Dadra and Nagar Haveli")))
            city_ok = bool(p["city"]) and p["city"] in norm(r[6])
            active = r[2] == "ACTIVE"
            distinctive = len(qt) >= 2 and qt <= ct
            g = grade(j, exact, city_ok, state_ok, active, distinctive)
            if not g:
                continue
            if (len(qt) <= 1 or j < 0.8) and not has_signal(r[1]):
                continue
            if p["region"] and not state_ok and not exact and j < 0.8:
                continue  # registered office in another state and the name is only partly similar
            score = j + (0.3 if active else 0) + (0.2 if city_ok else 0) + (0.1 if state_ok else 0)
            if r[0] not in seen or seen[r[0]][0] < score:
                seen[r[0]] = (score, g, r, j, city_ok)
        ranked = sorted(seen.values(), key=lambda x: -x[0])[:3]
        if any(x[1] == "high" for x in ranked):
            ranked = [x for x in ranked if x[1] != "low"]
        for score, g, r, j, city_ok in ranked:
            out.append(mca_row(p, r, "mca-bulk-name", g, "self", mca_note(r, j, city_ok)))
    return out


def mca_exact(mca, legal_name: str):
    rows, _, exact, _ = mca
    return [rows[i] for i in exact.get(exact_key(legal_name), [])]


# ------------------------------------------------------------- Goa excise ----
def load_goa(cache: Path):
    path = cache / "goa-contact_us.html"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    t = path.read_text(encoding="utf-8", errors="replace")
    units = []
    for tb in re.findall(r"<table.*?</table>", t, flags=re.S):
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, flags=re.S):
            cells = [htmllib.unescape(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.S)]
            cells = [re.sub(r"\s+", " ", c).strip() for c in cells]
            if len(cells) < 2:
                continue
            m = re.match(r"^(.*?)\s*\(\s*([^()]*(?:Distill|Winery|Brew|Bottling)[^()]*)\)\s*$", cells[1], flags=re.I)
            if not m:
                continue
            units.append({"unit": m.group(1).strip(), "type": re.sub(r"\s+", " ", m.group(2)).strip(),
                          "station": cells[2] if len(cells) > 2 else ""})
    print(f"goa excise: {len(units)} manufacturing units parsed", file=sys.stderr)
    return units


def match_goa(pins, units, mca):
    cands, lic = [], []
    for p in pins:
        if p["country"] != "India" or p["region"] != "Goa":
            continue
        best = None
        for u in units:
            nm = re.sub(r"^(M/s\.?|Shri|Smt\.?)\s*", "", u["unit"])
            nm = re.sub(r",?\s*(Prop\.|Proprietor|Partner).*$", "", nm)
            ct = toks(nm)
            j = jaccard(p["toks"], ct)
            exact = p["full"] == toks(nm, True)
            g = grade(j, exact, False, True, True, len(p["toks"]) >= 2 and p["toks"] <= ct)
            if g and (best is None or best[0] < j):
                best = (j, g, u, nm)
        if not best:
            continue
        j, g, u, nm = best
        lic.append([p["slug"], p["name"], "India", "in-goa-excise", "", u["unit"], "self", "goa-excise-unit-list", g, "", SRC_GOA,
                    f"listed as a manufacturing unit ({u['type']}) under {u['station'] or 'an excise station'}; name jaccard {j:.2f}; "
                    "no licence number is published"])
        for r in mca_exact(mca, nm)[:1]:
            cands.append(mca_row(p, r, "goa-excise-unit+mca-bulk", g, relation_for(p["toks"], r[1]),
                                 mca_note(r, j, False, f"unit name from Goa Excise list ({u['type']})")))
    return cands, lic


# ---------------------------------------------------------- website sweep ----
class Log:
    def __init__(self, cap: int = REQUEST_CAP):
        self.counts = defaultdict(int)
        self.cap = cap
        self.last = 0.0

    def hit(self, endpoint: str) -> bool:
        if sum(self.counts.values()) >= self.cap:
            return False
        wait = 1.0 - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        self.counts[endpoint] += 1
        return True


def fetch_page(url: str, log: Log):
    if not log.hit("pin websites"):
        return None
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(1_500_000)
            final = r.geturl()
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e)[:120]}
    text = raw.decode("utf-8", "replace")
    return {"url": url, "final": final, "html": text}


LEGAL_LINK = re.compile(r"(contact|about|terms|privacy|legal|imprint|disclaimer|impressum|company|policy)", re.I)


def sweep_websites(pins, cache: Path, fetch: bool, log: Log):
    path = cache / "websites.json"
    store = json.loads(path.read_text()) if path.exists() else {}
    for p in pins:
        site = p["website"]
        if not site or p["slug"] in store:
            continue
        if not fetch:
            continue
        if "facebook.com" in site or "nightsbridge" in site or "yolasite" in site:
            store[p["slug"]] = {"skipped": "not the distillery's own site"}
            continue
        rec = {"pages": []}
        home = fetch_page(site, log)
        if home is None:
            break
        rec["pages"].append(home.get("final", site))
        found = extract_numbers(home.get("html", ""), p["country"])
        if not found and "html" in home:
            base = home.get("final", site)
            links = []
            for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', home["html"], flags=re.S):
                href, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
                if LEGAL_LINK.search(txt) or LEGAL_LINK.search(href):
                    u = urllib.parse.urljoin(base, href)
                    if urllib.parse.urlparse(u).netloc == urllib.parse.urlparse(base).netloc and u not in links:
                        links.append(u)
            for u in links[:2]:
                pg = fetch_page(u, log)
                if pg is None:
                    break
                rec["pages"].append(pg.get("final", u))
                found = extract_numbers(pg.get("html", ""), p["country"])
                if found:
                    break
        if "error" in home:
            rec["error"] = home["error"]
        rec["found"] = found
        store[p["slug"]] = rec
        path.write_text(json.dumps(store, indent=1, ensure_ascii=False))
    return store


def extract_numbers(html_text: str, country: str):
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style).*?</\1>", " ", html_text, flags=re.S | re.I)))
    text = re.sub(r"\s+", " ", text)
    out = []
    rx = CIN_RE if country == "India" else ZA_RE
    for m in rx.finditer(text):
        num = re.sub(r"\s", "", m.group(1))
        ctx = text[max(0, m.start() - 160): m.end() + 60]
        if any(o["number"] == num for o in out):
            continue
        out.append({"number": num, "context": ctx})
    return out


def match_websites(pins, store, mca):
    out = []
    for p in pins:
        rec = store.get(p["slug"])
        if not rec or not rec.get("found"):
            continue
        src = rec["pages"][-1] if rec.get("pages") else p["website"]
        for f in rec["found"][:2]:
            num, ctx = f["number"], f["context"]
            if p["country"] == "India":
                rows, _, _, by_cin = mca
                r = rows[by_cin[num]] if num in by_cin else None
                name = r[1] if r else ""
                if not name:
                    m = re.search(r"([A-Z][A-Za-z0-9&.,()' -]{3,80}?(?:Limited|Ltd\.?|LLP))", ctx)
                    name = m.group(1).strip() if m else ""
                j = jaccard(p["toks"], toks(name)) if name else 0.0
                conf = "high" if (name and (j >= 0.5 or p["toks"] <= toks(name))) else "medium"
                rel = relation_for(p["toks"], name) if name else "self"
                note = (f"CIN printed on the distillery's website ({src}); " +
                        (f"MCA 2015 snapshot: {name}, status {r[2]}, registered {r[3]}, {r[4]}" if r else
                         f"not in the 2015 MCA snapshot (incorporated later or other state); name from page: '{name or 'n/a'}'") +
                        f"; page context: '{ctx.strip()[:140]}'")
                out.append([p["slug"], p["name"], "India", "in-mca", num, name or p["name"], rel, "website-regno", conf, "", src, note])
            else:
                m = re.search(r"([A-Z][A-Za-z0-9&.,'’() -]{2,80}?\s*(?:\(Pty\)\s*Ltd\.?|Pty\s*\(?Ltd\)?|\(PTY\)\s*LTD|CC\b|Ltd\.?|NPC|Inc\.?))", ctx)
                name = m.group(1).strip() if m else ""
                j = jaccard(p["toks"], toks(name)) if name else 0.0
                conf = "high" if (name and (j >= 0.5 or (p["toks"] and p["toks"] <= toks(name)))) else "medium"
                rel = relation_for(p["toks"], name) if name else "self"
                note = (f"registration number printed on the distillery's website ({src}); legal name from the page: "
                        f"'{name or 'n/a'}'; CIPC not queried (terms forbid automated search); page context: '{ctx.strip()[:140]}'")
                out.append([p["slug"], p["name"], "South Africa", "za-cipc", num, name or p["name"], rel, "website-regno", conf, "", src, note])
    return out


# ------------------------------------------------------------------- main ----
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--fetch-mca-states", action="store_true")
    ap.add_argument("--fetch-websites", action="store_true")
    args = ap.parse_args()
    cache = Path(args.cache).expanduser()
    cache.mkdir(parents=True, exist_ok=True)
    log = Log()

    pins = load_pins()
    print(f"{sum(p['country'] == 'India' for p in pins)} India pins, {sum(p['country'] == 'South Africa' for p in pins)} South Africa pins", file=sys.stderr)

    if args.fetch_mca_states:
        fetch_mca_states(cache, pins, log)
    mca = load_mca(cache)
    cands = match_mca(pins, mca)
    goa_c, goa_l = match_goa(pins, load_goa(cache), mca)
    store = sweep_websites(pins, cache, args.fetch_websites, log)
    web_c = match_websites(pins, store, mca)

    hand = []
    by_slug = {p["slug"]: p for p in pins}
    for slug, legal, rel, conf, note in HAND_IN:
        p = by_slug.get(slug)
        if not p:
            continue
        hits = mca_exact(mca, legal)
        if hits:
            r = hits[0]
            hand.append(mca_row(p, r, "hand", conf, rel, mca_note(r, None, False, note)))
        else:
            hand.append([slug, p["name"], "India", "in-mca", "", legal, rel, "hand", "medium" if conf == "high" else "low", "",
                         SRC_MCA, note + "; legal name not found in the 2015 MCA snapshot, CIN needs an MCA21 lookup"])
    for slug, legal, rel, conf, note in HAND_ZA:
        p = by_slug.get(slug)
        if not p:
            continue
        num = ""
        rec = store.get(slug) or {}
        for f in rec.get("found", []):
            if jaccard(toks(legal), toks(f["context"])) > 0 or True:
                num = f["number"]
                break
        if num:
            hand.append([slug, p["name"], "South Africa", "za-cipc", num, legal, rel, "hand", conf, "", SRC_CIPC,
                         note + "; number from the site's own website"])
        else:
            # No CIPC number on file or on the site, and CIPC's terms forbid an automated
            # search, so the row cannot carry a register number. Per the crosswalk rule, a
            # hand row without a number stays `low` rather than the researcher's hand-set
            # confidence, and the note says so explicitly.
            hand.append([slug, p["name"], "South Africa", "za-cipc", "", legal, rel, "hand", "low", "", SRC_CIPC,
                         note + "; CIPC not queried (terms), number blank; name known, number not read"])

    conf_rank = {"high": 0, "medium": 1, "low": 2}
    hand_keys = {(r[0], r[3], r[4]) for r in hand if r[4]}
    hand_names = {(r[0], r[3], norm(r[5]).strip()) for r in hand}
    machine = {}
    for r in cands + goa_c + web_c:
        if (r[0], r[3], r[4]) in hand_keys or (r[0], r[3], norm(r[5]).strip()) in hand_names:
            continue
        k = (r[0], r[3], r[4] or norm(r[5]).strip())
        if k not in machine or conf_rank[r[8]] < conf_rank[machine[k][8]]:
            machine[k] = r
    final = hand + list(machine.values())
    order = {p["slug"]: i for i, p in enumerate(pins)}
    final.sort(key=lambda r: (order[r[0]], r[3], conf_rank[r[8]], r[5]))
    licences = sorted(goa_l, key=lambda r: (order[r[0]], r[3]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, rows in ((OUT_CANDIDATES, final), (OUT_LICENCES, licences)):
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            w.writerows(rows)

    best = {}
    for r in final:
        if r[4]:  # only rows with a register number count as matched
            best[r[0]] = min(best.get(r[0], 9), conf_rank[r[8]])
    by_reg = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    for p in pins:
        d = by_reg[(p["country"], p["region"] or "(none)")]
        d["pins"] += 1
        if p["slug"] in best:
            d[["high", "medium", "low"][best[p["slug"]]]] += 1
        else:
            d["unmatched"] += 1
    print("country region pins high medium low unmatched")
    for key in sorted(by_reg, key=lambda k: (k[0], -by_reg[k]["pins"])):
        d = by_reg[key]
        print(f"{key[0]:13} {key[1]:40} {d['pins']:4} {d['high']:4} {d['medium']:6} {d['low']:3} {d['unmatched']:9}")
    for c in ("India", "South Africa"):
        tot = {k: sum(d[k] for kk, d in by_reg.items() if kk[0] == c) for k in ("pins", "high", "medium", "low", "unmatched")}
        print(f"{c:13} {'total':40} {tot['pins']:4} {tot['high']:4} {tot['medium']:6} {tot['low']:3} {tot['unmatched']:9}")
        print(f"unmatched {c}:", " ".join(p["slug"] for p in pins if p["country"] == c and p["slug"] not in best))
    print("requests this run:", dict(log.counts), f"(cap {log.cap})")
    print(f"{len(final)} candidate rows -> {OUT_CANDIDATES.relative_to(ROOT)}; {len(licences)} licence rows -> {OUT_LICENCES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
