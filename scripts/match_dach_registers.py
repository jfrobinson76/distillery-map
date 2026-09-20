#!/usr/bin/env python3
"""
Match the map's German, Austrian and Swiss distilleries against free, permitted company
registers and write candidate rows for human review.

Registers (research: docs/data-quality/dach-registers-2026-09-20.md):
  de-offeneregister  OffeneRegister.de, the OKFN Deutschland / OpenCorporates dump of the
                     Handelsregister (CC-BY 4.0, attribution to OpenCorporates). Snapshot of
                     June 2017 - January 2019, 5.3 M records, 260 MB bz2 JSONL. Matched
                     locally after a one-off filter pass (--build-de-subset, no network).
                     handelsregister.de itself is NOT queried: its Nutzungsordnung caps use
                     at 60 searches per hour and forbids systematic retrieval.
  at-firmenbuch      JustizOnline Firmenbuchabfrage, the Ministry of Justice's free public
                     name search (name, FN, status, Sitz; the detail call adds legal form
                     and address). Only fetched with --fetch-justizonline; cached. The
                     Statistik Austria FN -> OENACE list (CC-BY 4.0) flags FNs classified
                     11.01 "Herstellung von Spirituosen".
  ch-zefix           Zefix core data pulled from the federal LINDAS SPARQL endpoint
                     (opendata.swiss "Zefix - Zentraler Firmenindex", OGD terms_by). Only
                     fetched with --fetch-lindas; paged CSV cached. Legal name, UID,
                     address and the Zweck (purpose) text are matched locally. The Zefix
                     PublicREST API needs an account and is not used; the web app's own
                     backend is not used (robots.txt disallows everything).
  Sole traders (Obstbrennerei, Abfindungsbrennerei, Hofbrennerei) are not in any of these
  registers unless registered as e.K. / e.U., so most DACH pins stay unmatched by design.

Run (offline, from cached files):
  python3 scripts/match_dach_registers.py --cache /path/to/cache
One-off local filter of the OffeneRegister dump (needs de_companies_ocdata.jsonl.bz2):
  python3 scripts/match_dach_registers.py --cache DIR --build-de-subset
Fetch Zefix core data via LINDAS (16 paged SPARQL requests, cached):
  python3 scripts/match_dach_registers.py --cache DIR --fetch-lindas
Fetch JustizOnline name searches (<= 1 request/3s, cached):
  python3 scripts/match_dach_registers.py --cache DIR --fetch-justizonline

Cache dir may hold: de_companies_ocdata.jsonl.bz2 (-> de-offeneregister-subset.jsonl),
lindas-zefix-page-NN.csv, at_fbnr_oenace.csv, justizonline-cache.json,
ch-lohnbrennereien-2026-07.txt (BAZG PDF via pdftotext -layout, licence layer). Missing inputs are
skipped with a warning. Idempotent: same inputs -> same outputs.

Names, grading, fetching and the row schema come from scripts/crosswalklib. Fetching goes
through one crosswalklib.fetch.Fetcher (TLS verified, one request every `delay` seconds, a
hard cap, everything logged before it is sent); 20 Sep 2026: 436 requests already spent this
pass across LINDAS paging and JustizOnline name/detail lookups, over the historical 400
budget, so the Fetcher is built with spent=436 and makes nothing further unless a --fetch-*
flag is passed and the cap is raised.
"""
from __future__ import annotations

import argparse
import bz2
import csv
import json
import re
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crosswalklib import fetch, grading, names, rows  # noqa: E402
from crosswalklib.grading import Evidence  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "dach-candidates.csv"
OUT_LICENCES = OUT_DIR / "dach-licences.csv"
COUNTRIES = ("Germany", "Austria", "Switzerland")

SRC_OR = "https://offeneregister.de/"
OC_URL = "https://opencorporates.com/companies/de/{}"
SRC_JOP = "https://justizonline.gv.at/jop/web/firmenbuchabfrage"
JOP_SEARCH = "https://justizonline.gv.at/jop/service/fba/search"
JOP_DETAIL = "https://justizonline.gv.at/jop/service/fba/{}"
SRC_OENACE = "https://www.data.gv.at/katalog/datasets/456ce845-5d87-3877-bc0e-33c5371c7aa7"
SRC_ZEFIX = "https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex"
ZEFIX_URL = "https://www.zefix.admin.ch/de/search/entity/list/firm/{}"
LINDAS = "https://lindas.admin.ch/query"
SRC_BAZG = "https://www.bazg.admin.ch/dam/de/sd-web/7m2WSkYkaDRN/Adressliste%20Lohnbrenner_07_2026_DE.pdf"
LINDAS_PAGE = 25000
LINDAS_MAX_PAGES = 80

COMMON_TOKEN_CAP = 3000
PURPOSE_RE = re.compile(r"brennerei|destill|distill|spirituos|schnaps|whisk|edelbr|obstbr|liqueur|likör|likor|"
                        r"eaux?[- ]de[- ]vie|alcool|alkohol|absinth|gin\b|vodka|wodka|rum\b|grappa", re.I)

# Hand rows: group-run or renamed sites. Numbers were read from the same bulk data (see note);
# "" = the group entity is outside the free data (post-2019 German entity, or foreign parent).
HAND = {
    "weinbrennerei-wilthen": [
        ("de-offeneregister", "Göttingen früher Northeim HRB 130424", "Hardenberg-Wilthen Aktiengesellschaft", "operator", "high",
         "Wilthener Weinbrennerei was carried as a Zweigniederlassung of Hardenberg-Wilthen AG (Dresden HRB 16688, removed) in the "
         "OffeneRegister snapshot; the AG (Nörten-Hardenberg) was 'currently registered' as of 2018", SRC_OR),
    ],
    "schlichte-brennerei": [
        ("de-offeneregister", "Münster HRB 12037", "Schwarze und Schlichte GmbH", "operator", "high",
         "Schlichte Steinhäger (Steinhagen) is a Schwarze & Schlichte brand; group company at Paulsburg 1-3, 59302 Oelde, "
         "'currently registered' in the OffeneRegister snapshot (2018)", SRC_OR),
    ],
    "slyrs": [
        ("de-offeneregister", "München HRA 82320", "SLYRS Destillerie GmbH & Co. KG", "self", "high",
         "Slyrs, Bayrischzeller Str., Schliersee; 'currently registered' in the OffeneRegister snapshot; sister company of "
         "LANTENHAMMER Destillerie GmbH (München HRB 155682), Stetter family", SRC_OR),
    ],
    "santis-malt": [
        ("ch-zefix", "CHE-101.250.882", "Brauerei Locher Aktiengesellschaft", "operator", "high",
         "Säntis Malt is the whisky brand of Brauerei Locher Aktiengesellschaft, Appenzell; UID CHE-101.250.882 and "
         "address Brauereiplatz 1, 9050 Appenzell read directly from the LINDAS Zefix core-data dump "
         "(register.ld.admin.ch/zefix/company/457869)", "https://www.zefix.admin.ch/de/search/entity/list/firm/457869"),
    ],
    "diwisa": [
        ("ch-zefix", "CHE-101.803.195", "DIWISA AG", "self", "high",
         "Diwisa is the trading name of DIWISA AG, Willisau (Menznauerstrasse 23); UID CHE-101.803.195 read directly "
         "from the LINDAS Zefix core-data dump (register.ld.admin.ch/zefix/company/45938). The older name 'Diwisa "
         "Distillerie Willisau SA' used in the hand row before this pass no longer exists in the current Zefix "
         "extract as a company name -- it survives only as the historical name embedded in the linked pension "
         "foundation 'Personalfürsorgestiftung der Diwisa Distillerie Willisau SA' (CHE-109.768.645). Zweck: "
         "'Fabrikation von und Handel mit Getränken aller Art, insbesondere Spirituosen und Likören' (distilling "
         "purpose confirmed).", "https://www.zefix.admin.ch/de/search/entity/list/firm/45938"),
    ],
    "pfau-brand": [
        ("at-firmenbuch", "", "Vereinigte Kärntner Brauereien AG", "operator", "medium",
         "Pfau is distilled at the Schleppe brewery site, Klagenfurt, owned by Vereinigte Kärntner Brauereien AG. "
         "No FN could be confirmed from cached data: the name does not appear in the Statistik Austria FN->OENACE "
         "list (at_fbnr_oenace.csv -- breweries are not classified under 11.01 Herstellung von Spirituosen) and no "
         "JustizOnline name search for it is cached. A live JustizOnline search would resolve the FN but was not "
         "run this pass to stay inside the request cap; company_number stays blank rather than guessed.", SRC_JOP),
    ],
}
ALIASES = {
    "slyrs": ["SLYRS Destillerie"],
    "santis-malt": ["Brauerei Locher"],
    "diwisa": ["Distillerie Willisau"],
    "pfau-brand": ["Vereinigte Kärntner Brauereien"],
    "weinbrennerei-wilthen": ["Hardenberg-Wilthen"],
    "schlichte-brennerei": ["Schwarze und Schlichte"],
    "st-kilian-distillers": ["St. Kilian Distillers"],
    "langatun": ["Langatun Distillery"],
    "matte-brennerei": ["Matte Brennerei"],
    "highglen-whisky-distillery": ["HighGlen"],
    "marcado": ["Macardo"],
    "distillery-aarau-klg": ["Monkey in a Bottle", "Distillery Aarau"],
    "bailoni-erste-wachauer-marillen-destillerie-gmbh": ["Eugen Bailoni"],
    "eugen-bailoni-gmbh": ["Eugen Bailoni"],
    "whiskydestillerie-haider": ["Haider Roggenreith", "Destillerie Haider"],
    "reisetbauer-qualitatsbrand": ["Reisetbauer"],
    "destillerie-freihof": ["Freihof Destillerie"],
    "fassbind": ["Fassbind"],
    "distillerie-morand": ["Louis Morand"],
    "distillerie-studer": ["Distillerie Studer"],
    "regiomat-finch-whiskydestillerie": ["finch Whiskydestillerie", "Regiomat"],
    "schladerer": ["Alfred Schladerer"],
    "sasse-feinbrennerei": ["Sasse Feinbrennerei", "Sasse Korn"],
    "blaue-maus": ["Fleischmann Whisky", "Destillerie Fleischmann"],
}


# ---------------------------------------------------------------- helpers ----
def city_eq(a: str, b: str) -> bool:
    a, b = names.fold(a).strip(), names.fold(b).strip()
    if not a or not b:
        return False
    a1, b1 = a.split()[0], b.split()[0]
    return a == b or a in b or b in a or (len(a1) > 3 and a1 == b1)


def location_for(pin_city: str, other_city: str) -> str:
    """Evidence.location when the direct city/postcode check already failed: a known
    different city is a `conflict`, otherwise there simply is not enough to say."""
    if pin_city and other_city and not city_eq(pin_city, other_city):
        return "conflict"
    return "none"


def shared_ok(pin, qt: frozenset, ct: frozenset) -> bool:
    """The overlap must contain something other than the pin's own town name."""
    return bool((qt & ct) - names.tokens(pin["city"]))


ADDR_RE = re.compile(r"(?:^|,)\s*([A-Z]{1,2}-)?(\d{4,5})\s+([^,]+?)\s*(?:,|$)")


def pin_location(addr: str):
    """Return (postcode, city) from '... , 63924 Rüdenau, Germany' style addresses."""
    m = ADDR_RE.search(addr or "")
    if not m:
        return "", ""
    return m.group(2), m.group(3).strip()


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        if p.get("country") not in COUNTRIES:
            continue
        pc, city = pin_location(p.get("address") or "")
        pins.append({"slug": p["slug"], "name": p["name"], "country": p["country"], "pc": pc, "city": city,
                     "toks": names.tokens(p["name"]),
                     "aliases": ALIASES.get(p["slug"], []), "address": p.get("address") or ""})
    return pins


def rank_and_emit(seen: dict, keep: int = 3):
    ranked = sorted(seen.values(), key=lambda x: -x[0])[:keep]
    if any(x[1] == "high" for x in ranked):
        ranked = [x for x in ranked if x[1] != "low"]
    return ranked


# ---------------------------------------------------------------- Germany ----
def build_de_subset(cache: Path, pins) -> Path:
    """Stream the OffeneRegister dump once and keep records sharing a distinctive token with a pin."""
    src = cache / "de_companies_ocdata.jsonl.bz2"
    out = cache / "de-offeneregister-subset.jsonl"
    if not src.exists():
        print(f"warn: missing {src}", file=sys.stderr)
        return out
    want = set()
    for p in pins:
        for t in p["toks"] | set(t for a in p["aliases"] for t in names.tokens(a)):
            if len(t) >= 3 and not t.isdigit():
                want.add(t)
    n = kept = 0
    with bz2.open(src, "rt", encoding="utf-8") as fh, out.open("w", encoding="utf-8") as oh:
        for line in fh:
            n += 1
            d = json.loads(line)
            if names.tokens(d.get("name", "")) & want:
                a = d.get("all_attributes", {})
                oh.write(json.dumps({"name": d.get("name"), "number": d.get("company_number"),
                                     "native": a.get("native_company_number"), "office": a.get("registered_office"),
                                     "state": a.get("federal_state"), "status": d.get("current_status"),
                                     "address": d.get("registered_address"), "retrieved": d.get("retrieved_at"),
                                     "art": a.get("_registerArt")}, ensure_ascii=False) + "\n")
                kept += 1
    print(f"de subset: {kept} of {n} records kept -> {out}", file=sys.stderr)
    return out


def load_de(cache: Path):
    path = cache / "de-offeneregister-subset.jsonl"
    recs, index, exact = [], defaultdict(list), defaultdict(list)
    if not path.exists():
        print(f"warn: missing {path} (run --build-de-subset)", file=sys.stderr)
        return recs, index, exact
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            t = names.tokens(r["name"] or "")
            if not t:
                continue
            i = len(recs)
            recs.append(r)
            for tok in t:
                index[tok].append(i)
            exact[names.norm(r["name"], names.SUFFIX)].append(i)
    print(f"de: {len(recs)} OffeneRegister records indexed", file=sys.stderr)
    return recs, index, exact


def de_note(r, j, loc_ok, extra=""):
    return (f"name jaccard {j:.2f}; OffeneRegister status '{r['status']}' as of {(r['retrieved'] or '')[:10]} "
            f"(2017-2019 snapshot, not current); {r['native']}; registered office {r['office'] or 'n/a'}"
            f"{' (city agrees)' if loc_ok else ''}; address {r['address'] or 'n/a'}{extra}")


def match_de(pins, de):
    recs, index, _ = de
    out = []
    for p in pins:
        if p["country"] != "Germany" and not p["address"].endswith("Germany"):
            continue
        seen = {}
        for q in [p["name"]] + p["aliases"]:
            qt = names.tokens(q)
            if not qt:
                continue
            cand = set()
            for tok in qt:
                post = index.get(tok, [])
                if 0 < len(post) <= COMMON_TOKEN_CAP:
                    cand.update(post)
            for i in cand:
                r = recs[i]
                ct = names.tokens(r["name"])
                if not shared_ok(p, qt, ct):
                    continue
                j = names.jaccard(qt, ct)
                exact = names.exact(q, r["name"])
                loc_ok = city_eq(p["city"], r["office"] or "") or (bool(p["pc"]) and p["pc"] in (r["address"] or ""))
                active = (r["status"] or "") == "currently registered"
                location = "strong" if loc_ok else location_for(p["city"], r["office"] or "")
                e = Evidence(j, exact, location, active, names.distinctive(p["name"]), names.has_signal(r["name"]))
                g = grading.grade(e)
                if not g:
                    continue
                score = j + (0.3 if active else 0) + (0.2 if loc_ok else 0) + (0.2 if exact else 0)
                key = r["number"]
                if key not in seen or seen[key][0] < score:
                    seen[key] = (score, g, r, j, loc_ok)
        for score, g, r, j, loc_ok in rank_and_emit(seen):
            out.append(rows.make(p["slug"], p["name"], p["country"], "de-offeneregister",
                                  r["native"] or r["number"], r["name"],
                                  grading.relation_for(p["toks"], names.tokens(r["name"])),
                                  "offeneregister-bulk-name", g, OC_URL.format(r["number"]),
                                  de_note(r, j, loc_ok)))
    return out


# ---------------------------------------------------------------- Austria ----
def load_oenace(cache: Path):
    path = cache / "at_fbnr_oenace.csv"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return {}
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            out[r["FB_NUMMER"].strip().lower()] = r["OENACE_ZUORD"].strip()
    print(f"at: {len(out)} FN -> OENACE rows, {sum(1 for v in out.values() if v.startswith('1101'))} in 11.01 (spirits)", file=sys.stderr)
    return out


class JustizOnline:
    """Free JustizOnline Firmenbuch search. 20 Sep 2026: the server answers 429 after roughly
    100 requests at one per second, so the shared Fetcher is built with a 3s delay and stops
    for the run on the first 429. Requests, pacing, the cap, logging and TLS all come from
    crosswalklib.fetch.Fetcher; this class keeps only its own cache file, since past answers
    were saved keyed by search term / detail id, not by request URL (the Fetcher's cache is
    URL-hash keyed) -- that old-format file is read as-is and never re-fetched."""

    def __init__(self, cache_file: Path, f: fetch.Fetcher):
        self.cache_file = cache_file
        self.cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
        self.f = f

    def _save(self) -> None:
        self.cache_file.write_text(json.dumps(self.cache, indent=1, ensure_ascii=False))

    def search(self, q: str):
        key = "s:" + names.fold(q).strip()
        if key in self.cache:
            return self.cache[key]
        url = JOP_SEARCH + "?" + urllib.parse.urlencode({"term": q, "size": 10, "page": 0})
        data = self.f.json(url, headers={"Accept": "application/json"})
        if data is None:
            return None
        self.cache[key] = data.get("companies", [])
        self._save()
        return self.cache[key]

    def detail(self, cid: str):
        key = "d:" + cid
        if key in self.cache:
            return self.cache[key]
        data = self.f.json(JOP_DETAIL.format(urllib.parse.quote(cid)), headers={"Accept": "application/json"})
        if data is None:
            return None
        self.cache[key] = {"legalForm": (data.get("legalForm") or {}).get("name"),
                           "address": data.get("address") or {}}
        self._save()
        return self.cache[key]


def fn_format(fnr: str) -> str:
    m = re.match(r"^(\d+)([a-z])$", fnr.strip().lower())
    return f"FN {int(m.group(1))} {m.group(2)}" if m else fnr


def resolve_oenace_1101(jop: JustizOnline, oenace: dict, fetch_names: bool):
    """Names of every FN classified OENACE 11.01 (Herstellung von Spirituosen): one FN search each
    (only sent with --fetch-oenace-names; otherwise cached answers only)."""
    out = {}
    for fnr, code in sorted(oenace.items()):
        if not code.startswith("1101"):
            continue
        term = fnr.lstrip("0")
        res = jop.search(term) if (fetch_names or ("s:" + names.fold(term).strip()) in jop.cache) else None
        if not res:
            continue
        hit = next((r for r in res if (r.get("fnr") or "").lower() == fnr), None)
        if hit:
            out[fnr] = hit
    print(f"at: {len(out)} OENACE 11.01 companies resolved to names", file=sys.stderr)
    return out


def grade_at(p, q, r, oenace):
    nm = r.get("name") or ""
    qt, ct = names.tokens(q), names.tokens(nm)
    if not qt or not shared_ok(p, qt, ct):
        return None
    j = names.jaccard(qt, ct)
    exact = names.exact(q, nm)
    loc_ok = city_eq(p["city"], r.get("domicile") or "")
    active = r.get("status") == "ACTIVE"
    code = oenace.get((r.get("fnr") or "").lower(), "")
    purpose_ok = code.startswith("1101")
    location = "strong" if loc_ok else location_for(p["city"], r.get("domicile") or "")
    e = Evidence(j, exact, location, active, names.distinctive(p["name"]), names.has_signal(nm) or purpose_ok)
    g = grading.grade(e)
    if not g:
        return None
    score = j + (0.3 if active else 0) + (0.2 if loc_ok else 0) + (0.3 if purpose_ok else 0) + (0.2 if exact else 0)
    return score, g, r, j, loc_ok, code


def at_priority(p) -> tuple:
    """Pins whose name carries a legal form go first, then the most distinctive names."""
    legal = bool(re.search(r"\b(GmbH|KG|OG|AG|e\.?U\.?)\b", p["name"]))
    return (0 if legal else 1, -len(p["toks"]), p["slug"])


def match_at(pins, jop: JustizOnline, oenace: dict, fetch_names: bool = False, fallback: bool = False):
    spirits = resolve_oenace_1101(jop, oenace, fetch_names) if oenace else {}
    out = []
    for p in sorted(pins, key=at_priority):
        if p["country"] != "Austria":
            continue
        seen = {}
        # 1. local match against the OENACE 11.01 producers (no request per pin)
        for q in [p["name"]] + p["aliases"]:
            for r in spirits.values():
                hit = grade_at(p, q, r, oenace)
                if hit and (r["fnr"] not in seen or seen[r["fnr"]][0] < hit[0]):
                    seen[r["fnr"]] = hit + ("oenace-1101-list",)
        # 2. JustizOnline word search: full name first, distinctive tokens as a fallback
        for q in [p["name"]] + p["aliases"]:
            full = [t for t in names.fold(q).split() if t not in names.SUFFIX]
            distinct = sorted(names.tokens(q))
            terms = [" ".join(full)] if full else []
            if fallback and len(distinct) >= 2 and " ".join(distinct) != " ".join(full):
                terms.append(" ".join(distinct))
            for i, term in enumerate(terms):
                if len(term) < 3:
                    continue
                res = jop.search(term)
                if res is None:
                    continue
                for r in res:
                    hit = grade_at(p, q, r, oenace)
                    if hit and (r["fnr"] not in seen or seen[r["fnr"]][0] < hit[0]):
                        seen[r["fnr"]] = hit + ("justizonline-name-search",)
                if res:
                    break  # the fallback term only runs when the full term found nothing
        for score, g, r, j, loc_ok, code, how in rank_and_emit(seen):
            note = (f"name jaccard {j:.2f}; Firmenbuch status {r.get('status')}; Sitz {r.get('domicile')}"
                    f"{' (city agrees)' if loc_ok else ''}; "
                    + (f"OENACE {code[:2]}.{code[2:4]}{' = Herstellung von Spirituosen' if code.startswith('1101') else ''}"
                       if code else "no OENACE code in the Statistik Austria list")
                    + "; JustizOnline free search, legal form from the name")
            out.append(rows.make(p["slug"], p["name"], "Austria", "at-firmenbuch", fn_format(r.get("fnr") or ""),
                                  r.get("name"), grading.relation_for(p["toks"], names.tokens(r.get("name") or "")),
                                  how, g,
                                  SRC_JOP + "/suchergebnis?search=" + urllib.parse.quote((r.get("fnr") or "").lstrip("0")),
                                  note))
    return out


# ------------------------------------------------------------ Switzerland ----
LINDAS_Q = """PREFIX schema: <http://schema.org/> PREFIX admin: <https://schema.ld.admin.ch/>
SELECT ?c ?legal ?uid ?loc ?street ?zip ?typ ?desc FROM <https://lindas.admin.ch/foj/zefix> WHERE {
 ?c a admin:ZefixOrganisation ; schema:legalName ?legal ; schema:identifier ?id .
 FILTER(CONTAINS(STR(?id),"/UID/")) BIND(STRAFTER(STR(?id),"/UID/") AS ?uid)
 OPTIONAL { ?c schema:address ?a . ?a schema:addressLocality ?loc . OPTIONAL { ?a schema:streetAddress ?street } OPTIONAL { ?a schema:postalCode ?zip } }
 OPTIONAL { ?c schema:additionalType ?typ } OPTIONAL { ?c schema:description ?desc }
} ORDER BY ?c LIMIT %d OFFSET %d"""


def fetch_lindas(cache: Path, f: fetch.Fetcher) -> None:
    """Page through the Zefix graph on LINDAS. One request per page, written straight to the
    same page filename the matcher has always used (the cache lookup below is by filename,
    not by the Fetcher's own URL-hash cache, so this is idempotent the same way it always was:
    an existing page file is never re-requested)."""
    for page in range(LINDAS_MAX_PAGES):
        path = cache / f"lindas-zefix-page-{page:02d}.csv"
        if path.exists():
            continue
        q = LINDAS_Q % (LINDAS_PAGE, page * LINDAS_PAGE)
        url = LINDAS + "?" + urllib.parse.urlencode({"query": q})
        body = f.text(url, headers={"Accept": "text/csv"})
        if body is None:
            print(f"lindas: page {page} not fetched; stopping", file=sys.stderr)
            break
        path.write_text(body, encoding="utf-8")
        n_rows = sum(1 for _ in csv.reader(body.splitlines())) - 1
        print(f"lindas: page {page} {n_rows} rows", file=sys.stderr)
        if n_rows < LINDAS_PAGE:
            break
    print("lindas: " + f.summary(), file=sys.stderr)


def load_ch(cache: Path):
    recs, index = [], defaultdict(list)
    files = sorted(cache.glob("lindas-zefix-page-*.csv"))
    if not files:
        print("warn: no lindas-zefix-page-*.csv in cache (run --fetch-lindas)", file=sys.stderr)
        return recs, index
    seen = {}
    for f in files:
        with f.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                uid = r["uid"]
                if uid in seen:  # a company can have several address rows; keep the first
                    continue
                seen[uid] = len(recs)
                recs.append({"ehraid": r["c"].rsplit("/", 1)[-1], "name": r["legal"], "uid": uid, "loc": r["loc"],
                             "street": r["street"], "zip": r["zip"], "typ": r["typ"].rsplit("/", 1)[-1],
                             "purpose": bool(PURPOSE_RE.search(r.get("desc") or ""))})
                for tok in names.tokens(r["legal"]):
                    index[tok].append(seen[uid])
    print(f"ch: {len(recs)} Zefix entities indexed from {len(files)} LINDAS pages; "
          f"{sum(1 for r in recs if r['purpose'])} with a distilling/spirits purpose", file=sys.stderr)
    return recs, index


def uid_format(uid: str) -> str:
    m = re.match(r"^CHE(\d{3})(\d{3})(\d{3})$", uid)
    return f"CHE-{m.group(1)}.{m.group(2)}.{m.group(3)}" if m else uid


def match_ch(pins, ch):
    recs, index = ch
    out = []
    for p in pins:
        if p["country"] != "Switzerland":
            continue
        seen = {}
        for q in [p["name"]] + p["aliases"]:
            qt = names.tokens(q)
            if not qt:
                continue
            cand = set()
            for tok in qt:
                post = index.get(tok, [])
                if 0 < len(post) <= COMMON_TOKEN_CAP:
                    cand.update(post)
            for i in cand:
                r = recs[i]
                ct = names.tokens(r["name"])
                if not shared_ok(p, qt, ct):
                    continue
                j = names.jaccard(qt, ct)
                exact = names.exact(q, r["name"])
                loc_ok = city_eq(p["city"], r["loc"]) or (bool(p["pc"]) and p["pc"] == r["zip"])
                location = "strong" if loc_ok else location_for(p["city"], r["loc"])
                e = Evidence(j, exact, location, True, names.distinctive(p["name"]),
                             names.has_signal(r["name"]) or r["purpose"])
                g = grading.grade(e)
                if not g:
                    continue
                score = j + (0.2 if loc_ok else 0) + (0.3 if r["purpose"] else 0) + (0.2 if exact else 0)
                key = r["uid"]
                if key not in seen or seen[key][0] < score:
                    seen[key] = (score, g, r, j, loc_ok)
        for score, g, r, j, loc_ok in rank_and_emit(seen):
            note = (f"name jaccard {j:.2f}; Zefix active entity (LINDAS core data, daily); legal form eCH-0097 {r['typ']}; "
                    f"seat {r['loc']}{' (city agrees)' if loc_ok else ''}, {r['street']}, {r['zip']}; "
                    + ("Zweck mentions distilling/spirits" if r["purpose"] else "Zweck has no distilling word"))
            out.append(rows.make(p["slug"], p["name"], "Switzerland", "ch-zefix", uid_format(r["uid"]), r["name"],
                                  grading.relation_for(p["toks"], names.tokens(r["name"])),
                                  "lindas-zefix-bulk-name", g, ZEFIX_URL.format(r["ehraid"]), note))
    return out


# ------------------------------------------------- BAZG Lohnbrennereien (CH) ----
BAZG_LINE = re.compile(r"^(.*?)\s{2,}(?:(.*?)\s{2,})?(\d{4})\s+(.+?)\s{2,}([A-Z]{2})\s*$")


def load_bazg(cache: Path):
    """BAZG 'Liste der Lohnbrennereien in der Schweiz' (Stand 01.07.2026), converted once with
    pdftotext -layout to ch-lohnbrennereien-2026-07.txt. Columns: Nachname, Vorname, PLZ, Ort, Kanton."""
    path = cache / "ch-lohnbrennereien-2026-07.txt"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith(("Liste", "Stand", "Nachname")):
            continue
        m = BAZG_LINE.match(line)
        if m:
            out.append({"name": " ".join(x for x in (m.group(2), m.group(1)) if x).strip(), "zip": m.group(3),
                        "town": m.group(4).strip(), "canton": m.group(5)})
    print(f"ch: {len(out)} BAZG Lohnbrennereien", file=sys.stderr)
    return out


def match_bazg(pins, bazg, ch):
    recs, index = ch
    lic, cands = [], []
    exact_idx = defaultdict(list)
    for i, r in enumerate(recs):
        exact_idx[names.norm(r["name"], names.SUFFIX)].append(i)
    for p in pins:
        if p["country"] != "Switzerland":
            continue
        best = {}
        for b in bazg:
            bt = names.tokens(b["name"])
            if not bt or not shared_ok(p, p["toks"], bt):
                continue
            j = names.jaccard(p["toks"], bt)
            loc_ok = (bool(p["pc"]) and p["pc"] == b["zip"]) or city_eq(p["city"], b["town"])
            location = "strong" if loc_ok else location_for(p["city"], b["town"])
            exact = names.exact(p["name"], b["name"])
            e = Evidence(j, exact, location, True, names.distinctive(p["name"]), names.has_signal(b["name"]))
            g = grading.grade(e)
            if not g:
                continue
            key = b["name"] + b["zip"]
            score = j + (0.3 if loc_ok else 0)
            if key not in best or best[key][0] < score:
                best[key] = (score, g, b, j, loc_ok)
        for score, g, b, j, loc_ok in sorted(best.values(), key=lambda x: -x[0])[:2]:
            lic.append(rows.make(p["slug"], p["name"], "Switzerland", "ch-bazg-lohnbrennerei", "", b["name"], "self",
                                  "bazg-list-name", g, SRC_BAZG,
                                  f"BAZG Liste der Lohnbrennereien, Stand 01.07.2026; {b['zip']} {b['town']} {b['canton']}"
                                  f"{' (location agrees)' if loc_ok else ''}; name jaccard {j:.2f}; contract distiller, not a register number"))
            for i in exact_idx.get(names.norm(b["name"], names.SUFFIX), [])[:1]:
                r = recs[i]
                cands.append(rows.make(p["slug"], p["name"], "Switzerland", "ch-zefix", uid_format(r["uid"]), r["name"],
                                        grading.relation_for(p["toks"], names.tokens(r["name"])),
                                        "bazg-list+lindas-zefix", g, ZEFIX_URL.format(r["ehraid"]),
                                        f"legal name from the BAZG Lohnbrennerei list ({b['zip']} {b['town']}), name jaccard {j:.2f}; "
                                        f"Zefix active entity, seat {r['loc']}, {r['street']}, {r['zip']}"))
    return lic, cands


# ------------------------------------------------------------------- main ----
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory holding the downloaded bulk files")
    ap.add_argument("--build-de-subset", action="store_true", help="filter de_companies_ocdata.jsonl.bz2 locally (no network)")
    ap.add_argument("--fetch-lindas", action="store_true", help="page the Zefix graph from LINDAS (cached CSV)")
    ap.add_argument("--fetch-justizonline", action="store_true", help="allow JustizOnline pin-name searches (cached)")
    ap.add_argument("--fetch-oenace-names", action="store_true", help="also resolve every OENACE 11.01 FN to a name (151 searches)")
    ap.add_argument("--jop-fallback", action="store_true", help="retry a pin with distinctive tokens only when the full name finds nothing")
    args = ap.parse_args()
    cache = Path(args.cache).expanduser()
    cache.mkdir(parents=True, exist_ok=True)

    # One Fetcher for the whole run: LINDAS paging and JustizOnline both go through it. 20 Sep
    # 2026: 436 requests already spent this pass, over the historical 400 budget -- spent=436
    # carries that count over, so nothing more is fetched until a --fetch-* flag raises it back
    # under cap. delay=3.0 matches JustizOnline's tighter rate limit (the binding constraint of
    # the two registries this touches); the slower pace is harmless for LINDAS too.
    f = fetch.Fetcher(cache, allow=(args.fetch_lindas or args.fetch_justizonline), cap=400,
                       delay=3.0, log=cache / "requests.log", spent=436)

    pins = load_pins()
    print(f"{len(pins)} DACH pins: " + ", ".join(f"{c} {sum(1 for p in pins if p['country'] == c)}" for c in COUNTRIES), file=sys.stderr)

    if args.build_de_subset:
        build_de_subset(cache, pins)
    if args.fetch_lindas:
        fetch_lindas(cache, f)

    de_c = match_de(pins, load_de(cache))
    jop = JustizOnline(cache / "justizonline-cache.json", f)
    at_c = match_at(pins, jop, load_oenace(cache), args.fetch_oenace_names, args.jop_fallback)
    ch = load_ch(cache)
    ch_c = match_ch(pins, ch)
    lic, bazg_c = match_bazg(pins, load_bazg(cache), ch)
    ch_c += bazg_c
    print("fetch: " + f.summary(), file=sys.stderr)

    hand = []
    for slug, hrows in HAND.items():
        p = next((x for x in pins if x["slug"] == slug), None)
        if not p:
            continue
        for reg, num, name, rel, conf, note, src in hrows:
            hand.append(rows.make(slug, p["name"], p["country"], reg, num, name, rel, "hand", conf, src, note))

    # a machine row that finds the hand row's company fills its number (hand rows carry the relation and evidence)
    machine_pool = de_c + at_c + ch_c
    for h in hand:
        if not h["company_number"]:
            m = next((r for r in machine_pool if r["slug"] == h["slug"] and r["registry"] == h["registry"]
                      and names.fold(r["company_name"]).strip() == names.fold(h["company_name"]).strip()), None)
            if m:
                h["company_number"] = m["company_number"]
                h["note"] = h["note"] + "; " + m["note"]
    hand_keys = {(r["slug"], r["registry"], r["company_number"]) for r in hand}
    hand_names = {(r["slug"], r["registry"], names.fold(r["company_name"]).strip()) for r in hand}
    machine = {}
    for r in machine_pool:
        key_name = names.fold(r["company_name"]).strip()
        if (r["slug"], r["registry"], r["company_number"]) in hand_keys or (r["slug"], r["registry"], key_name) in hand_names:
            continue
        k = (r["slug"], r["registry"], r["company_number"] or key_name)
        if k not in machine or grading.ORDER.index(r["confidence"]) < grading.ORDER.index(machine[k]["confidence"]):
            machine[k] = r
    final = hand + list(machine.values())
    grading.apply_guards(final, hand)
    order = {s["slug"]: i for i, s in enumerate(pins)}
    final.sort(key=lambda r: (order[r["slug"]], r["registry"], grading.ORDER.index(r["confidence"]), r["company_name"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    licences = sorted(lic, key=lambda r: (order[r["slug"]], r["registry"], grading.ORDER.index(r["confidence"])))
    grading.apply_guards(licences, [])
    known_slugs = {p["slug"] for p in pins}
    rows.write(OUT_CANDIDATES, final, known_slugs)
    rows.write(OUT_LICENCES, licences, known_slugs)

    by_c = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    best = {}
    for r in final:
        best[r["slug"]] = min(best.get(r["slug"], 9), grading.ORDER.index(r["confidence"]))
    for p in pins:
        d = by_c[p["country"]]
        d["pins"] += 1
        if p["slug"] in best:
            d[["high", "medium", "low"][best[p["slug"]]]] += 1
        else:
            d["unmatched"] += 1
    print("country      pins high medium low unmatched")
    for c in COUNTRIES:
        d = by_c[c]
        print(f"{c:12} {d['pins']:4} {d['high']:4} {d['medium']:6} {d['low']:3} {d['unmatched']:9}")
    tot = {k: sum(d[k] for d in by_c.values()) for k in ("pins", "high", "medium", "low", "unmatched")}
    print(f"{'total':12} {tot['pins']:4} {tot['high']:4} {tot['medium']:6} {tot['low']:3} {tot['unmatched']:9}")
    print(f"{len(final)} candidate rows -> {OUT_CANDIDATES.relative_to(ROOT)}; "
          f"{len(licences)} licence rows -> {OUT_LICENCES.relative_to(ROOT)}")
    print("unmatched:", " ".join(p["slug"] for p in pins if p["slug"] not in best))
    return 0


if __name__ == "__main__":
    sys.exit(main())
