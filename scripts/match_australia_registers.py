#!/usr/bin/env python3
"""
Match the map's Australian and New Zealand distilleries against free, permitted company
registers and liquor-licence lists, and write candidate rows for human review.

Registers and lists (research: docs/data-quality/australia-registers-2026-09-20.md):
  au-abr     ABN Lookup bulk extract, data.gov.au (CC-BY 3.0 AU), 20 XML files in two
             zips (~1 GB compressed, 12.6 GB uncompressed). Streamed once with
             --build-abr-index into <cache>/abr-slim.tsv (only records whose entity,
             business or trading name resembles a pin name or carries a drinks word).
             Gives ABN, ABN status, entity type, entity name, business/trading names,
             ACN, GST status, state and postcode of the main business location.
  au-asic    ASIC Company Dataset, data.gov.au (CC-BY 3.0 AU), one 400 MB TSV inside
             company_YYYYMM.zip. Gives ACN, company name (current and former), type,
             class, status, registration date, ABN. No address. Streamed once per run,
             keeping rows whose ACN was reached through the ABR or whose name resembles
             a pin name.
  vic-lcv    Liquor Control Victoria "Victorian liquor licences by location" monthly
             stocktake (CC-BY 4.0), xlsx. Licensee = legal name, plus Trading As,
             category, suburb, postcode. Producer's Licence rows bridge trading name
             to legal name; the legal name is then resolved in the ABR/ASIC files.
  tas-list   Tasmanian LIST "Liquor Licences" layer (CC-BY 3.0 AU), Esri REST, fetched
             only with --fetch-tas. Sub-category Brewery/Distillery: licence number,
             premises name, suburb, postcode. No licensee, so licence layer only.
  nz-companies  NZ Companies Register. No anonymous bulk or API route (bulk needs an
             access request, the NZBN API a subscription key) and the search app's
             robots.txt disallows all agents, so it is not queried. Rows come only from
             one saved page (cache/nz_search_sample.html, the first 15 results for
             "distillery" fetched by hand on 20 Sep 2026) plus hand rows.
  NOT used: ABN Lookup web services (needs a GUID registration), ASIC Connect (web
  form), NSW Liquor API (sandbox key, 5 calls/min), QLD OLGR search (licensee details
  are $45.65 per licence), SA CBS register (form, no bulk since 2019), WA RGL (no public
  list found), ATO excise manufacturer licences (not published).

Names, grading and the one HTTP client come from scripts/crosswalklib (see
match_ttb_permits.py for the pattern); this script keeps its own address parsing, the
ABR/ASIC/VIC/TAS/NZ file readers, and the drinks-vs-other category-mismatch check.

Run (offline, from cached files):
  python3 scripts/match_australia_registers.py --cache /path/to/cache
First run: build the ABR slim index (streams the two zips, ~15-30 min):
  python3 scripts/match_australia_registers.py --cache /path/to/cache --build-abr-index
Fetch the Tasmanian LIST layer (one request, cached):
  python3 scripts/match_australia_registers.py --cache /path/to/cache --fetch-tas

Cache dir must hold: public_split_1_10.zip, public_split_11_20.zip (ABR), company_*.zip
(ASIC), vic_licences_by_location_*.xlsx, and optionally tas_list_liquor_brewery_distillery.json
and nz_search_sample.html. Missing files are skipped with a warning.
Idempotent: same inputs -> same outputs. Never fetches without an explicit --fetch flag.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crosswalklib import fetch, grading, names, rows  # noqa: E402
from crosswalklib.grading import Evidence  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "australia-candidates.csv"
OUT_LICENCES = OUT_DIR / "australia-licences.csv"

SRC_ABR = "https://data.gov.au/data/dataset/abn-bulk-extract"
SRC_ASIC = "https://data.gov.au/data/dataset/asic-companies"
SRC_VIC = "https://discover.data.vic.gov.au/dataset/victorian-liquor-licences-by-location"
SRC_TAS = "https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/16"
TAS_QUERY = (SRC_TAS + "/query?where=SUB_CATEGO%3D%27Brewery%2FDistillery%27&outFields=*"
             "&returnGeometry=false&f=json")
SRC_NZ = ("https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search?q=distillery"
          "&entityTypes=ALL&entityStatusGroups=ALL&addressTypes=ALL&start=0&limit=15&advancedPanel=true&mode=advanced")
NZ_ENTITY = "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{}"

STATES = ("NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT")
STATE_RE = re.compile(r"\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b\s*(\d{4})?", re.I)
STATE_WORDS = {"new south wales": "NSW", "victoria": "VIC", "queensland": "QLD", "south australia": "SA",
               "western australia": "WA", "tasmania": "TAS", "northern territory": "NT"}
# Category words that flag a name-quality mismatch, kept local to this matcher (not identity
# normalisation, so out of scope for crosswalklib.names).
DIST_KIND = {"distillery", "distillers", "distilling", "distilleries", "distiller", "distillation", "distilled",
             "spirits", "spirit", "gin", "whisky", "whiskey", "rum", "vodka", "liqueur", "liqueurs", "moonshine",
             "brandy", "stillhouse", "schnapps", "absinthe", "agave"}
OTHER_KIND = {"brewing", "brewery", "brewers", "brewhouse", "winery", "wines", "wine", "vineyard", "vineyards",
              "cellar", "cellars", "estate", "farm", "farms", "cidery", "cider", "meadery", "mead", "vintners",
              "orchard", "orchards", "cafe", "restaurant", "hotel", "resort", "motel", "accommodation"}
PARTNERSHIP_TYPES = {"PTR", "FPT", "LPT", "OTP"}
NAME_TYPES = {"MN": "entity name", "BN": "business name", "TRD": "trading name", "LGL": "legal name",
              "OTN": "other name", "DGR": "DGR fund name"}

# Slugs that need a different search string than the pin name (trading name -> known legal name,
# or the pin name minus a suffix that the register drops).
ALIASES = {
    "sullivan-s-cove-distillery": ["Sullivans Cove Distillery", "Tasmania Distillery"],
    "lark-distillery": ["Lark Distilling Co", "Lark Distillery"],
    "lark-distillery-pontville": ["Lark Distilling Co", "Lark Distillery"],
    "four-pillars-gin-distillery": ["Four Pillars Gin", "Healesville Distilling"],
    "archie-rose-distilling-co": ["Archie Rose Distilling"],
    "starward-distillery-bar": ["New World Whisky Distillery", "Starward"],
    "bundaberg-rum-distillery": ["Bundaberg Rum Distillery"],
    "beenleigh-rum-distillery": ["Beenleigh Rum Distillery", "Beenleigh Artisan Distillers"],
    "hellyers-road-distillery": ["Hellyers Road Distillery"],
    "old-young-s": ["Old Youngs", "Old Young's Distillery"],
    "kimberley-rum-c": ["Kimberley Rum Company"],
    "limeburners-and-ginversity-in-the-valley": ["Great Southern Distilling Company", "Limeburners"],
    "limeburners": ["Great Southern Distilling Company", "Limeburners Distillery"],
    "the-canberra-distillery": ["Canberra Distillery"],
    "here-s-looking-at-you-kid": ["Heres Looking At You Kid"],
    "mcgregor-young": ["McGregor and Young"],
    "st-marks-bridport": ["St Marks Bridport"],
    "saint-felix": ["Saint Felix Distillery"],
    "jimmyrum": ["JimmyRum", "Jimmy Rum"],
    "the-distillery-pty-ltd-trading-as-distillery-software": [],
    "wildbrumby-schnapps-distillery": ["Wild Brumby Distillery", "Wild Brumby Schnapps"],
    "wildstreak-distillery": ["Wild Streak Distillery"],
    "southarm-craft-distillery": ["South Arm Distillery", "South Arm Craft Distillery"],
    "30-knots-distillery": ["Thirty Knots Distillery"],
    "broken-hill-distillery-wed-to-sun-from-12pm-all-day-gin-tastings": ["Broken Hill Distillery"],
    "montvale-gin-distillery-bar": ["Montvale Distillery", "Montvale Gin"],
    "ambra-spirits-distillery-bar-restaurant": ["Ambra Spirits Distillery", "Ambra Spirits"],
    "storytellers-distillery-in-the-vale": ["Storytellers Distillery"],
    "spirited-distilling-company-and-tasmanian-tonic-company-cellar-door": ["Spirited Distilling Company", "Tasmanian Tonic Company"],
    "ladbroken-distillery-brewhouse": ["Lad Broken Distillery", "Ladbroken Distillery"],
    "bent-road-winery-distillery": ["Bent Road Wines", "Bent Road Distillery"],
    "skin-gin": [],
}

# Hand cases: relation known from industry knowledge; number checked in the bulk file during
# the 20 Sep 2026 run (see the research note). number "" = not obtainable from a free register.
HAND = {
    "four-pillars-gin-distillery": [
        ("au-abr", "89606461367", "HEALESVILLE DISTILLING PTY LTD", "self", "high",
         "ABN active, private company, business names 'Four Pillars Gin' and 'Four Pillars Laboratory'; ACN 606461367; "
         "operating company of the Healesville distillery", SRC_ABR),
        ("au-abr", "13008596370", "LION-BEER,SPIRITS & WINE PTY LTD", "group", "high",
         "ABN active, ACN 008596370; Lion (Kirin) owns Four Pillars outright since 2023; ABR lists 'Four Pillars Distillery' "
         "as a business name on this ABN", SRC_ABR),
    ],
    "starward-distillery-bar": [
        ("au-abr", "78603892888", "NEW WORLD WHISKY DISTILLERY PTY LTD", "self", "high",
         "ABN active, private company, main business location VIC 3207 (Port Melbourne, postcode agrees); ACN 603892888; "
         "Starward is the brand of New World Whisky Distillery", SRC_ABR),
    ],
    "beenleigh-rum-distillery": [
        ("au-abr", "29102738670", "INNER CIRCLE DISTILLERY PTY LIMITED", "operator", "high",
         "ABN active, private company, business names 'Beenleigh Rum Distillery', 'Beenleigh Artisan Distillers', "
         "'Inner Circle Rum'; ACN 102738670; main business location SA 5106 (Bickford's group address)", SRC_ABR),
        ("au-abr", "35109800213", "BICKFORDS TRADING PTY LTD", "group", "high",
         "ABN active, ACN 109800213; business name 'Beenleigh Distilling Company'; Bickford's Group owns Beenleigh", SRC_ABR),
    ],
    "bundaberg-rum-distillery": [
        ("au-abr", "97009657069", "BUNDABERG DISTILLING COMPANY PTY. LIMITED", "self", "high",
         "ABN active, private company, other name 'Bundaberg Rum Distillery', QLD 4670 (postcode agrees); ACN 009657069; "
         "Diageo subsidiary", SRC_ABR),
        ("au-abr", "", "Diageo Australia Limited", "group", "high",
         "Diageo owns Bundaberg Distilling Company; the Diageo Australia ABN/ACN was not in the slim index (no drinks word "
         "in the name) and was not looked up", SRC_ABR),
    ],
    "sullivan-s-cove-distillery": [
        ("au-abr", "91614780460", "SULLIVANS COVE DISTILLERY PTY LTD", "self", "high",
         "ABN active, private company, business name 'Tasmania Distillery'; ACN 614780460; the earlier Tasmania Distillery "
         "Pty Ltd is now A.C.N. 085 534 514 Pty Ltd with a cancelled ABN (82085534514)", SRC_ABR),
    ],
    "lark-distillery": [
        ("au-abr", "57100738074", "LARK DISTILLERY PTY LTD", "self", "high",
         "ABN active, private company; ACN 100738074; subsidiary of the ASX-listed Lark Distilling Co. Ltd", SRC_ABR),
        ("au-abr", "62104600544", "LARK DISTILLING CO. LTD", "group", "high",
         "ABN active, public company (ASX: LRK); ACN 104600544; main business location TAS 7030", SRC_ABR),
    ],
    "lark-distillery-pontville": [
        ("au-abr", "57100738074", "LARK DISTILLERY PTY LTD", "self", "high",
         "ABN active, private company; ACN 100738074; Pontville is Lark's production site (Shene Rd)", SRC_ABR),
        ("au-abr", "62104600544", "LARK DISTILLING CO. LTD", "group", "high",
         "ABN active, public company (ASX: LRK); ACN 104600544; main business location TAS 7030 (postcode agrees)", SRC_ABR),
    ],
    "limeburners": [
        ("au-abr", "78110857504", "LATRO SOUTHERN PTY LTD", "self", "high",
         "ABN active, private company, trading name 'Great Southern Distilling Company', WA 6330 (Albany, postcode agrees); "
         "ACN 110857504; Limeburners is its whisky brand", SRC_ABR),
    ],
    "limeburners-and-ginversity-in-the-valley": [
        ("au-abr", "78110857504", "LATRO SOUTHERN PTY LTD", "operator", "high",
         "ABN active, trading name 'Great Southern Distilling Company' (Albany WA 6330); ACN 110857504; "
         "the Swan Valley site is its second distillery", SRC_ABR),
    ],
}


def kind_mismatch(pin_name: str, name: str) -> bool:
    """True when the pin says distillery/gin/... but the matched name says brewing/winery/farm/...
    with no distilling word of its own (same site may run both, but it is weaker evidence)."""
    pt, nt = set(names.fold(pin_name).split()), set(names.fold(name).split())
    return bool(pt & DIST_KIND) and bool(nt & OTHER_KIND) and not (nt & DIST_KIND)


# ------------------------------------------------------------------- pins ----
def parse_address(addr: str):
    a = addr or ""
    state, pc = "", ""
    m = STATE_RE.search(a)
    if m:
        state = m.group(1).upper()
        pc = m.group(2) or ""
    else:
        low = a.lower()
        for w, s in STATE_WORDS.items():
            if w in low:
                state = s
                break
    if not pc:
        m2 = re.search(r"\b(\d{4})\b(?!.*\b\d{4}\b)", a)
        pc = m2.group(1) if m2 else ""
    # suburb = the token before the state, or before the postcode
    sub = ""
    m3 = re.search(r",\s*([^,\d]+?)\s+(?:NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b", a, re.I)
    if m3:
        sub = names.fold(m3.group(1)).strip()
    else:
        m4 = re.search(r",\s*([^,\d]+?)\s*\d{4}\b", a)
        if m4:
            sub = names.fold(m4.group(1)).strip()
    return state, pc, sub


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        if p.get("country") not in ("Australia", "New Zealand"):
            continue
        addr = p.get("address") or ""
        state, pc, sub = parse_address(addr)
        if p["country"] == "New Zealand":
            state = "NZ"
        if "Germany" in addr:
            state, pc, sub = "", "", ""  # mislabelled pin, matched by nothing
        pins.append({"slug": p["slug"], "name": p["name"], "country": p["country"], "state": state,
                     "pc": pc, "suburb": sub, "toks": names.tokens(p["name"]),
                     "aliases": ALIASES.get(p["slug"], []), "addr": addr})
    return pins


def pin_queries(p):
    return [p["name"]] + p["aliases"]


# --------------------------------------------------------------------- ABR ----
ABR_FIELDS = ["abn", "status", "status_from", "type", "type_text", "name", "state", "postcode", "acn",
              "gst", "updated", "other"]
RE_ABN = re.compile(r'<ABN status="(\w+)" ABNStatusFromDate="(\d+)">(\d+)</ABN>')
RE_TYPE = re.compile(r"<EntityTypeInd>(\w+)</EntityTypeInd><EntityTypeText>([^<]*)</EntityTypeText>")
RE_MAIN = re.compile(r'<MainEntity><NonIndividualName type="(\w+)"><NonIndividualNameText>([^<]*)</NonIndividualNameText>')
RE_IND = re.compile(r"<LegalEntity><IndividualName[^>]*>(.*?)</IndividualName>", re.S)
RE_ADDR = re.compile(r"<AddressDetails><State>([^<]*)</State><Postcode>([^<]*)</Postcode>")
RE_ACN = re.compile(r"<ASICNumber[^>]*>(\d+)</ASICNumber>")
RE_GST = re.compile(r'<GST status="(\w+)"')
RE_OTHER = re.compile(r'<OtherEntity><NonIndividualName type="(\w+)"><NonIndividualNameText>([^<]*)</NonIndividualNameText>')
RE_UPD = re.compile(r'recordLastUpdatedDate="(\d+)"')


def build_abr_index(cache: Path, pins):
    """Stream the ABR bulk zips once; keep records whose names resemble a pin or carry a drinks word."""
    zips = sorted(cache.glob("public_split_*.zip"))
    if not zips:
        print("warn: no public_split_*.zip in cache; ABR index not built", file=sys.stderr)
        return
    tok_pins = defaultdict(set)
    for i, p in enumerate(pins):
        for q in pin_queries(p):
            for t in names.tokens(q):
                tok_pins[t].add(i)
    out = cache / "abr-slim.tsv"
    kept = seen = 0
    with out.open("w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(ABR_FIELDS)
        for zp in zips:
            z = zipfile.ZipFile(zp)
            for zname in sorted(z.namelist()):
                print(f"abr: {zp.name}/{zname}", file=sys.stderr)
                with z.open(zname) as raw:
                    for line in io.TextIOWrapper(raw, encoding="utf-8", errors="replace"):
                        if "<ABR " not in line:
                            continue
                        seen += 1
                        found = []
                        m = RE_MAIN.search(line)
                        if m:
                            found.append(("MN", html.unescape(m.group(2))))
                        else:
                            m = RE_IND.search(line)
                            if m:
                                parts = re.findall(r"<(?:GivenName|FamilyName)>([^<]*)</", m.group(1))
                                found.append(("LGL", html.unescape(" ".join(parts))))
                        for t, n in RE_OTHER.findall(line):
                            found.append((t, html.unescape(n)))
                        keep = False
                        for _, n in found:
                            nt = names.tokens(n)
                            if names.has_signal(n):
                                keep = True
                                break
                            cand = set()
                            for t in nt:
                                cand |= tok_pins.get(t, set())
                            for i in cand:
                                if names.jaccard(pins[i]["toks"], nt) >= 0.4:
                                    keep = True
                                    break
                            if keep:
                                break
                        if not keep:
                            continue
                        kept += 1
                        ab = RE_ABN.search(line)
                        ty = RE_TYPE.search(line)
                        ad = RE_ADDR.search(line)
                        ac = RE_ACN.search(line)
                        gs = RE_GST.search(line)
                        up = RE_UPD.search(line)
                        main = found[0][1] if found and found[0][0] in ("MN", "LGL") else ""
                        other = "|".join(f"{t}:{n}" for t, n in found[1:]) if found else ""
                        w.writerow([ab.group(3) if ab else "", ab.group(1) if ab else "", ab.group(2) if ab else "",
                                    ty.group(1) if ty else "", ty.group(2) if ty else "", main,
                                    ad.group(1) if ad else "", ad.group(2) if ad else "", ac.group(1) if ac else "",
                                    gs.group(1) if gs else "", up.group(1) if up else "", other])
    print(f"abr: {seen} records seen, {kept} kept -> {out}", file=sys.stderr)


def load_abr(cache: Path):
    path = cache / "abr-slim.tsv"
    recs, index, exact, by_abn, by_acn = [], defaultdict(list), defaultdict(list), {}, defaultdict(list)
    if not path.exists():
        print(f"warn: missing {path} (run --build-abr-index)", file=sys.stderr)
        return recs, index, exact, by_abn, by_acn
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            i = len(recs)
            names_list = [("MN" if r["type"] != "IND" else "LGL", r["name"])] if r["name"] else []
            for part in (r["other"] or "").split("|"):
                if ":" in part:
                    t, n = part.split(":", 1)
                    names_list.append((t, n))
            r["names"] = names_list
            recs.append(r)
            by_abn[r["abn"]] = i
            if r["acn"]:
                by_acn[r["acn"]].append(i)
            for t, n in names_list:
                for tok in names.tokens(n):
                    index[tok].append(i)
                exact[names.norm(n, names.SUFFIX)].append(i)
    print(f"abr: {len(recs)} slim records loaded", file=sys.stderr)
    return recs, index, exact, by_abn, by_acn


def abr_note(r, j, via, pc_ok, state_ok):
    loc = f"{r['state']} {r['postcode']}".strip()
    return (f"name jaccard {j:.2f} via {via}; ABN {r['status']} from {r['status_from'][:4]}; "
            f"{r['type_text']}; main business location {loc or 'n/a'}"
            f"{' (postcode agrees)' if pc_ok else (' (state agrees)' if state_ok else '')}; "
            f"ACN {r['acn'] or 'none'}; GST {r['gst'] or 'n/a'}; ABR record updated {r['updated'][:4]}")


def match_abr(pins, abr):
    recs, index, _, _, _ = abr
    hits = {}
    for p in pins:
        if p["country"] != "Australia":
            continue
        best = {}
        for q in pin_queries(p):
            qt = names.tokens(q)
            if not qt:
                continue
            cand = set()
            for tok in qt:
                post = index.get(tok, [])
                if 0 < len(post) <= 20000:
                    cand.update(post)
            for i in cand:
                r = recs[i]
                for t, n in r["names"]:
                    nt = names.tokens(n)
                    j = names.jaccard(qt, nt)
                    exact = names.exact(q, n)
                    pc_ok = bool(p["pc"]) and p["pc"] == r["postcode"]
                    state_ok = bool(p["state"]) and p["state"] == r["state"]
                    if p["state"] and r["state"] and r["state"] != p["state"] and not exact:
                        continue
                    active = r["status"] == "ACT"
                    distinctive = names.distinctive(q)
                    loc = "strong" if pc_ok else ("weak" if state_ok else "none")
                    g = grading.grade(Evidence(j, exact, loc, active, distinctive,
                                               names.has_signal(n) or names.has_signal(r["name"])))
                    if not g:
                        continue
                    if len(qt) <= 1 and not (names.has_signal(n) or pc_ok):
                        continue
                    if len(qt) <= 1 and not names.has_signal(n):
                        g = grading.cap(g, "medium")  # one shared word plus a postcode is not proof
                    if r["type"] in ({"IND"} | PARTNERSHIP_TYPES) and g == "high":
                        g = "medium"  # sole trader / partnership of persons, not a company
                    mismatch = kind_mismatch(q, n) and not any(set(names.fold(x).split()) & DIST_KIND for _, x in r["names"])
                    if mismatch:
                        g = grading.cap(g, "low" if len(qt) <= 1 else "medium")
                    score = j + (0.3 if active else 0) + (0.3 if pc_ok else 0) + (0.1 if state_ok else 0) + (0.2 if exact else 0)
                    key = r["abn"]
                    if key not in best or best[key][0] < score:
                        best[key] = (score, g, r, j, NAME_TYPES.get(t, t) + f" '{n}'" + (" (category word differs, no distilling word on this ABN)" if mismatch else ""), pc_ok, state_ok)
        ranked = sorted(best.values(), key=lambda x: -x[0])[:3]
        if any(x[1] == "high" for x in ranked):
            ranked = [x for x in ranked if x[1] != "low"]
        hits[p["slug"]] = ranked
    return hits


def abr_row(p, r, g, j, via, pc_ok, state_ok, method):
    trades = via.split(chr(39))[1] if chr(39) in via else p["name"]
    if r["type"] == "IND":
        company_name = f"(individual, sole trader ABN; trades as {trades})"
        rel = "self"
    elif r["type"] in PARTNERSHIP_TYPES and not names.has_signal(r["name"]) and " & " in r["name"]:
        company_name = f"(partnership of individuals, {r['type_text']}; trades as {trades})"
        rel = "self"
    else:
        company_name = r["name"]
        rel = grading.relation_for(p["toks"], names.tokens(r["name"])) if p["toks"] else "self"
        if any(names.tokens(n) & p["toks"] for t, n in r["names"] if t in ("BN", "TRD", "OTN")):
            rel = "self"  # the pin name is a registered business/trading name of this ABN
    return rows.make(p["slug"], p["name"], p["country"], "au-abr", r["abn"], company_name, rel, method, g,
                      SRC_ABR, abr_note(r, j, via, pc_ok, state_ok))


# -------------------------------------------------------------------- ASIC ----
def scan_asic(cache: Path, pins, wanted_acns: set):
    """One pass over the ASIC company TSV. Returns {acn: [rows]} for wanted ACNs and name hits."""
    zips = sorted(cache.glob("company_*.zip"))
    by_acn, name_index, recs = defaultdict(list), defaultdict(list), []
    if not zips:
        print("warn: no company_*.zip (ASIC) in cache", file=sys.stderr)
        return by_acn, name_index, recs
    tok_pins = defaultdict(set)
    for i, p in enumerate(pins):
        for q in pin_queries(p):
            for t in names.tokens(q):
                tok_pins[t].add(i)
    z = zipfile.ZipFile(zips[-1])
    name = z.namelist()[0]
    n = 0
    with z.open(name) as raw:
        rd = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"), delimiter="\t")
        for r in rd:
            n += 1
            acn = (r.get("ACN") or "").strip()
            nm = r.get("Company Name") or ""
            keep = acn in wanted_acns
            if not keep:
                nt = names.tokens(nm)
                cand = set()
                for t in nt:
                    cand |= tok_pins.get(t, set())
                for i in cand:
                    if names.jaccard(pins[i]["toks"], nt) >= 0.5:
                        keep = True
                        break
            if not keep:
                continue
            rec = {k: (v or "").strip() for k, v in r.items() if k}
            i = len(recs)
            recs.append(rec)
            by_acn[acn].append(i)
            for tok in names.tokens(nm):
                name_index[tok].append(i)
    print(f"asic: {n} rows scanned, {len(recs)} kept ({zips[-1].name}/{name})", file=sys.stderr)
    return by_acn, name_index, recs


def asic_current(recs, idx_list):
    """Prefer the row flagged as the current name."""
    cur = [recs[i] for i in idx_list if recs[i].get("Current Name Indicator") == "Y"]
    return cur[0] if cur else (recs[idx_list[0]] if idx_list else None)


def asic_note(r, evidence):
    cur = r.get("Current Name Indicator") == "Y"
    return (f"{evidence}; ASIC status {r.get('Status')}; {r.get('Type')}/{r.get('Class')}/{r.get('Sub Class')}; "
            f"registered {r.get('Date of Registration')}"
            f"{'; deregistered ' + r['Date of Deregistration'] if r.get('Date of Deregistration') else ''}; "
            f"state of registration {r.get('Previous State of Registration') or 'n/a'}; ABN {r.get('ABN') or 'n/a'}"
            + ("" if cur else f"; FORMER name, current name {r.get('Current Name')}"))


def asic_row(p, r, g, method, evidence, rel):
    name = r.get("Company Name") if r.get("Current Name Indicator") == "Y" else (r.get("Current Name") or r.get("Company Name"))
    if r.get("Status") != "REGD" and g == "high":
        g = "medium"
    return rows.make(p["slug"], p["name"], p["country"], "au-asic", r.get("ACN"), name, rel, method, g,
                      SRC_ASIC, asic_note(r, evidence))


def match_asic_by_name(pins, asic):
    by_acn, name_index, recs = asic
    out = []
    for p in pins:
        if p["country"] != "Australia":
            continue
        best = {}
        for q in pin_queries(p):
            qt = names.tokens(q)
            if not qt:
                continue
            cand = set()
            for tok in qt:
                cand.update(name_index.get(tok, []))
            for i in cand:
                r = recs[i]
                nm = r.get("Company Name") or ""
                nt = names.tokens(nm)
                j = names.jaccard(qt, nt)
                exact = names.exact(q, nm)
                st = r.get("Previous State of Registration") or ""
                state_ok = bool(p["state"]) and st == p["state"]
                if p["state"] and st and st != p["state"] and not exact:
                    continue
                active = r.get("Status") == "REGD"
                distinctive = names.distinctive(q)
                loc = "weak" if state_ok else "none"
                g = grading.grade(Evidence(j, exact, loc, active, distinctive, names.has_signal(nm)))
                if not g:
                    continue
                if g == "high" and not (state_ok or (distinctive and names.has_signal(nm))):
                    g = "medium"  # no address in the ASIC file: name alone is not enough
                if len(qt) <= 1 and not names.has_signal(nm):
                    continue
                if kind_mismatch(q, nm):
                    g = grading.cap(g, "low" if len(qt) <= 1 else "medium")
                if not names.has_signal(nm) or r.get("Current Name Indicator") != "Y":
                    g = grading.cap(g, "medium")  # no drinks word, or a former name: not proof on its own
                score = j + (0.3 if active else 0) + (0.1 if state_ok else 0) + (0.2 if exact else 0)
                key = r.get("ACN")
                if key not in best or best[key][0] < score:
                    best[key] = (score, g, r, j, state_ok)
        ranked = sorted(best.values(), key=lambda x: -x[0])[:3]
        if any(x[1] == "high" for x in ranked):
            ranked = [x for x in ranked if x[1] != "low"]
        for score, g, r, j, state_ok in ranked:
            ev = f"name jaccard {j:.2f} on '{r.get('Company Name')}'" + (" (state of registration agrees)" if state_ok else "")
            out.append(asic_row(p, r, g, "asic-bulk-name", ev,
                                 grading.relation_for(p["toks"], names.tokens(r.get("Company Name") or ""))))
    return out


# --------------------------------------------------------------------- VIC ----
def load_vic(cache: Path):
    files = sorted(cache.glob("vic_licences_by_location_*.xlsx"))
    if not files:
        print("warn: no vic_licences_by_location_*.xlsx in cache", file=sys.stderr)
        return [], ""
    path = files[-1]
    z = zipfile.ZipFile(path)
    x = z.read("xl/worksheets/sheet1.xml").decode("utf-8", "replace")
    rows_xml = re.findall(r"<row[^>]*>(.*?)</row>", x, flags=re.S)

    def cells(row_xml):
        d = {}
        for m in re.finditer(r'<c [^>]*?r="([A-Z]+)\d+"[^>]*?>(.*?)</c>', row_xml, flags=re.S):
            col, inner = m.groups()
            d[col] = html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", inner, flags=re.S))).strip()
        return d
    hdr = None
    out = []
    asof = ""
    for row_xml in rows_xml:
        c = cells(row_xml)
        if not c:
            continue
        if hdr is None:
            if c.get("A") == "Licence Number":
                hdr = c
            else:
                m = re.search(r"as of (\d\d/\d\d/\d{4})", " ".join(c.values()))
                if m:
                    asof = m.group(1)
            continue
        rec = {hdr[k]: v for k, v in c.items() if k in hdr}
        if rec.get("Licence Category", "").startswith("Producer"):
            out.append(rec)
    print(f"vic: {len(out)} producer's licences ({path.name}, as of {asof or '?'})", file=sys.stderr)
    return out, asof


def match_vic(pins, vic, asof, abr):
    """Licence rows + legal-name bridge into ABR (exact legal name -> ABN/ACN)."""
    abr_recs, _, exact, _, _ = abr
    lic, cands = [], []
    for p in pins:
        if p["state"] not in ("VIC", "") or p["country"] != "Australia":
            continue
        best = {}
        for r in vic:
            for field in ("Trading As", "Licensee"):
                nm = r.get(field) or ""
                nt = names.tokens(nm)
                j = names.jaccard(p["toks"], nt)
                exact_nm = names.exact(p["name"], nm)
                pc_ok = bool(p["pc"]) and p["pc"] == r.get("Postcode", "")
                sub_ok = bool(p["suburb"]) and p["suburb"] == names.fold(r.get("Suburb", "")).strip()
                loc = "strong" if (pc_ok or sub_ok) else "weak"
                g = grading.grade(Evidence(j, exact_nm, loc, True, names.distinctive(p["name"]),
                                            names.has_signal(nm)))
                if not g:
                    continue
                if len(p["toks"]) <= 1 and not (names.has_signal(nm) or pc_ok):
                    continue
                score = j + (0.3 if pc_ok or sub_ok else 0) + (0.2 if exact_nm else 0)
                key = r["Licence Number"]
                if key not in best or best[key][0] < score:
                    best[key] = (score, g, r, j, pc_ok or sub_ok, field)
        for score, g, r, j, loc_ok, field in sorted(best.values(), key=lambda x: -x[0])[:2]:
            legal = r.get("Licensee", "")
            lic.append(rows.make(p["slug"], p["name"], "Australia", "vic-lcv", r["Licence Number"], legal, "self",
                                  "lcv-licence-name", g, SRC_VIC,
                                  f"Producer's Licence, stocktake as of {asof}; trading as '{r.get('Trading As', '')}', "
                                  f"{r.get('Street Address', '')}, {r.get('Suburb', '')} {r.get('Postcode', '')}"
                                  f"{' (location agrees)' if loc_ok else ''}; name jaccard {j:.2f} on {field.lower()}"))
            # bridge: licensee legal name -> ABR exact name -> ABN (+ACN)
            rel = grading.relation_for(p["toks"], names.tokens(legal))
            for i in exact.get(names.norm(legal, names.SUFFIX), [])[:2]:
                ar = abr_recs[i]
                if ar["type"] == "IND":
                    continue
                gg = "high" if (ar["status"] == "ACT" and g in ("high", "medium")) else "medium"
                if g == "low":
                    gg = "low"
                pc_ok2 = bool(p["pc"]) and p["pc"] == ar["postcode"]
                cands.append(rows.make(p["slug"], p["name"], "Australia", "au-abr", ar["abn"], ar["name"], rel,
                                        "lcv-licensee+abr-bulk", gg, SRC_ABR,
                                        f"licensee of LCV producer's licence {r['Licence Number']} ('{r.get('Trading As', '')}', "
                                        f"{r.get('Suburb', '')}), name jaccard {j:.2f}; "
                                        + abr_note(ar, 1.0, "licensee legal name", pc_ok2, ar["state"] == "VIC")))
    return lic, cands


# --------------------------------------------------------------------- TAS ----
def load_tas(cache: Path, f: fetch.Fetcher) -> list[dict]:
    """TAS LIST liquor layer. Reuses the pre-crosswalklib cache file if present (one-time shim,
    never re-fetched); otherwise goes through the Fetcher, which only fetches when --fetch-tas
    is passed."""
    legacy = cache / "tas_list_liquor_brewery_distillery.json"
    body = legacy.read_bytes() if legacy.exists() else f.get(TAS_QUERY)
    if body is None:
        print(f"warn: no Tasmanian LIST data (run --fetch-tas, or place {legacy.name} in the cache)",
              file=sys.stderr)
        return []
    feats = json.loads(body).get("features", [])
    return [feat["attributes"] for feat in feats]


def match_tas(pins, tas):
    lic = []
    for p in pins:
        if p["state"] not in ("TAS", "") or p["country"] != "Australia":
            continue
        best = {}
        for r in tas:
            nm = r.get("PREMISE_NA") or ""
            nt = names.tokens(nm)
            j = names.jaccard(p["toks"], nt)
            exact_nm = names.exact(p["name"], nm)
            pc_ok = bool(p["pc"]) and p["pc"] == (r.get("POSTCODE") or "")
            sub_ok = bool(p["suburb"]) and p["suburb"] == names.fold(r.get("SUBURB") or "").strip()
            loc = "strong" if (pc_ok or sub_ok) else "weak"
            g = grading.grade(Evidence(j, exact_nm, loc, True, names.distinctive(p["name"]),
                                        names.has_signal(nm)))
            if not g:
                continue
            if len(p["toks"]) <= 1 and not (names.has_signal(nm) or pc_ok):
                continue
            score = j + (0.3 if pc_ok or sub_ok else 0) + (0.2 if exact_nm else 0)
            key = r["LICENCE_NO"]
            if key not in best or best[key][0] < score:
                best[key] = (score, g, r, j, pc_ok or sub_ok)
        for score, g, r, j, loc_ok in sorted(best.values(), key=lambda x: -x[0])[:2]:
            lic.append(rows.make(p["slug"], p["name"], "Australia", "tas-list", str(r["LICENCE_NO"]), "", "self",
                                  "list-premises-name", g, SRC_TAS,
                                  f"Special licence, sub-category Brewery/Distillery; premises '{r.get('PREMISE_NA')}', "
                                  f"{r.get('PREMISE_AD') or ''}, {r.get('SUBURB')} {r.get('POSTCODE')}{' (location agrees)' if loc_ok else ''}; "
                                  f"currency {r.get('CURRENCY')}; licensee name not in the LIST layer; name jaccard {j:.2f}"))
    return lic


# ---------------------------------------------------------------------- NZ ----
NZ_RE = re.compile(r"([A-Z0-9&'’\-\.,()/ ]+?) \((\d+)\) \(NZBN: (\d+)\) (Registered|Removed|In Liquidation|In Receivership)"
                   r"[^A-Za-z]*(NZ Limited Company|[A-Za-z ]+?) (.*?) Incorporation Date: (\d\d \w{3} \d{4})")


def load_nz_sample(cache: Path):
    path = cache / "nz_search_sample.html"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    t = path.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    out = []
    for m in NZ_RE.finditer(t):
        out.append({"name": m.group(1).strip(), "number": m.group(2), "nzbn": m.group(3), "status": m.group(4),
                    "type": m.group(5).strip(), "address": m.group(6).strip(), "incorporated": m.group(7)})
    print(f"nz: {len(out)} companies parsed from the saved search page", file=sys.stderr)
    return out


def match_nz(pins, nz):
    out = []
    for p in pins:
        if p["country"] != "New Zealand":
            continue
        for r in nz:
            for q in pin_queries(p):
                qt = names.tokens(q)
                nt = names.tokens(r["name"])
                if not qt:
                    continue
                j = names.jaccard(qt, nt)
                exact = names.exact(q, r["name"])
                if not (exact or j >= 0.6):
                    continue
                addr = names.fold(r["address"])
                loc_ok = bool(p["suburb"]) and p["suburb"] in addr
                pc_ok = bool(p["pc"]) and p["pc"] in r["address"]
                active = r["status"] == "Registered"
                loc = "strong" if (pc_ok or loc_ok) else "weak"
                g = grading.grade(Evidence(j, exact, loc, active, names.distinctive(q), names.has_signal(r["name"])))
                if len(qt) <= 1 and not (pc_ok or loc_ok):
                    g = grading.cap(g, "medium")
                if not g:
                    continue
                out.append(rows.make(p["slug"], p["name"], "New Zealand", "nz-companies", r["number"], r["name"],
                                      grading.relation_for(qt, names.tokens(r["name"])), "nz-search-page-name", g,
                                      NZ_ENTITY.format(r["number"]),
                                      f"name jaccard {j:.2f}; status {r['status']}; {r['type']}; incorporated {r['incorporated']}; "
                                      f"registered office {r['address']}{' (location agrees)' if (pc_ok or loc_ok) else ''}; "
                                      f"NZBN {r['nzbn']}; from the saved first page of results for 'distillery' (20 Sep 2026), "
                                      f"not a live query"))
    return out


# -------------------------------------------------------------------- main ----
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory holding the downloaded bulk files")
    ap.add_argument("--build-abr-index", action="store_true", help="stream the ABR zips into abr-slim.tsv")
    ap.add_argument("--fetch-tas", action="store_true", help="fetch the Tasmanian LIST liquor layer (one request)")
    args = ap.parse_args()
    cache = Path(args.cache).expanduser()

    pins = load_pins()
    au = [p for p in pins if p["country"] == "Australia"]
    print(f"{len(au)} Australian pins, {len(pins) - len(au)} New Zealand pins", file=sys.stderr)

    if args.build_abr_index:
        build_abr_index(cache, pins)

    f = fetch.Fetcher(cache, allow=args.fetch_tas, cap=4, delay=1.0, log=cache / "requests.log", spent=2)

    abr = load_abr(cache)
    abr_recs, _, _, _, abr_by_acn = abr
    abr_hits = match_abr(pins, abr)
    vic, vic_asof = load_vic(cache)
    vic_l, vic_c = match_vic(pins, vic, vic_asof, abr)
    tas_l = match_tas(pins, load_tas(cache, f))
    nz_c = match_nz(pins, load_nz_sample(cache))

    # ABR -> rows, and the set of ACNs to resolve in the ASIC file
    abr_c = []
    wanted = set()
    for p in pins:
        for score, g, r, j, via, pc_ok, state_ok in abr_hits.get(p["slug"], []):
            abr_c.append(abr_row(p, r, g, j, via, pc_ok, state_ok, "abr-bulk-name"))
            if r["acn"]:
                wanted.add(r["acn"])
    for row in vic_c:
        acn = re.search(r"ACN (\d{9})", row["note"])
        if acn:
            wanted.add(acn.group(1))

    asic = scan_asic(cache, pins, wanted)
    asic_by_acn, _, asic_recs = asic
    asic_c = match_asic_by_name(pins, asic)
    # ASIC rows reached through an ABR/licence ACN link
    for row in abr_c + vic_c:
        acn = re.search(r"ACN (\d{9})", row["note"])
        if not acn or acn.group(1) not in asic_by_acn:
            continue
        r = asic_current(asic_recs, asic_by_acn[acn.group(1)])
        if not r:
            continue
        p = next(x for x in pins if x["slug"] == row["slug"])
        method = row["match_method"].replace("abr-bulk-name", "abr-acn-link").replace(
            "lcv-licensee+abr-bulk", "lcv-licensee+abr-acn-link")
        asic_c.append(asic_row(p, r, row["confidence"], method,
                                f"ACN from ABN {row['company_number']} ({row['company_name']})", row["relation"]))

    hand = []
    for slug, entries in HAND.items():
        p = next((x for x in pins if x["slug"] == slug), None)
        if not p:
            continue
        for reg, num, name, rel, conf, note, src in entries:
            hand.append(rows.make(slug, p["name"], p["country"], reg, num, name, rel, "hand", conf, src, note))

    machine_all = abr_c + vic_c + asic_c + nz_c
    hand_keys = {(r["slug"], r["registry"], r["company_number"]) for r in hand}
    conf_rank = {"high": 0, "medium": 1, "low": 2}
    machine = {}
    for r in machine_all:
        if (r["slug"], r["registry"], r["company_number"]) in hand_keys:
            continue
        k = (r["slug"], r["registry"], r["company_number"] or names.fold(r["company_name"]).strip())
        if k not in machine or conf_rank[r["confidence"]] < conf_rank[machine[k]["confidence"]]:
            machine[k] = r
    final = hand + list(machine.values())
    grading.apply_guards(final, hand)
    order = {s["slug"]: i for i, s in enumerate(pins)}
    final.sort(key=lambda r: (order[r["slug"]], r["registry"], conf_rank[r["confidence"]], r["company_name"]))
    licences = sorted(vic_l + tas_l, key=lambda r: (order[r["slug"]], r["registry"], conf_rank[r["confidence"]]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    known_slugs = {p["slug"] for p in pins}
    rows.write(OUT_CANDIDATES, final, known_slugs)
    rows.write(OUT_LICENCES, licences, known_slugs)

    # summary
    by_state = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    best = {}
    for r in final:
        best[r["slug"]] = min(best.get(r["slug"], 9), conf_rank[r["confidence"]])
    for p in pins:
        d = by_state[p["state"] or "(none)"]
        d["pins"] += 1
        if p["slug"] in best:
            d[["high", "medium", "low"][best[p["slug"]]]] += 1
        else:
            d["unmatched"] += 1
    print("state  pins high medium low unmatched")
    for st in sorted(by_state, key=lambda k: -by_state[k]["pins"]):
        d = by_state[st]
        print(f"{st:6} {d['pins']:4} {d['high']:4} {d['medium']:6} {d['low']:3} {d['unmatched']:9}")
    tot = {k: sum(d[k] for d in by_state.values()) for k in ("pins", "high", "medium", "low", "unmatched")}
    print(f"total  {tot['pins']:4} {tot['high']:4} {tot['medium']:6} {tot['low']:3} {tot['unmatched']:9}")
    print("unmatched:", " ".join(p["slug"] for p in pins if p["slug"] not in best))
    print(f"{len(final)} candidate rows -> {OUT_CANDIDATES.relative_to(ROOT)}; "
          f"{len(licences)} licence rows -> {OUT_LICENCES.relative_to(ROOT)}")
    print(f.summary(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
