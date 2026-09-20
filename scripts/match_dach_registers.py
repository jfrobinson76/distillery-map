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
Fetch JustizOnline name searches (<= 1 request/second, hard cap 400, cached):
  python3 scripts/match_dach_registers.py --cache DIR --fetch-justizonline

Cache dir may hold: de_companies_ocdata.jsonl.bz2 (-> de-offeneregister-subset.jsonl),
lindas-zefix-page-NN.csv, at_fbnr_oenace.csv, justizonline-cache.json,
ch-lohnbrennereien-2026-07.txt (BAZG PDF via pdftotext -layout, licence layer). Missing inputs are
skipped with a warning. Idempotent: same inputs -> same outputs.
"""
from __future__ import annotations

import argparse
import bz2
import csv
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
OUT_CANDIDATES = OUT_DIR / "dach-candidates.csv"
OUT_LICENCES = OUT_DIR / "dach-licences.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]
COUNTRIES = ("Germany", "Austria", "Switzerland")

SRC_OR = "https://offeneregister.de/"
OC_URL = "https://opencorporates.com/companies/de/{}"
SRC_JOP = "https://justizonline.gv.at/jop/web/firmenbuchabfrage"
JOP_SEARCH = "https://justizonline.gv.at/jop/service/fba/search"
JOP_DETAIL = "https://justizonline.gv.at/jop/service/fba/{}"
JOP_CAP = 50  # per run. 20 Sep 2026: 11 probes + 337 requests (100 answered, 237 x 429) already spent of the 400 budget
SRC_OENACE = "https://www.data.gv.at/katalog/datasets/456ce845-5d87-3877-bc0e-33c5371c7aa7"
SRC_ZEFIX = "https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex"
ZEFIX_URL = "https://www.zefix.admin.ch/de/search/entity/list/firm/{}"
LINDAS = "https://lindas.admin.ch/query"
SRC_BAZG = "https://www.bazg.admin.ch/dam/de/sd-web/7m2WSkYkaDRN/Adressliste%20Lohnbrenner_07_2026_DE.pdf"
LINDAS_PAGE = 25000
LINDAS_MAX_PAGES = 80

SUFFIX = {"gmbh", "ag", "kg", "co", "cokg", "ohg", "ek", "e", "k", "ug", "haftungsbeschrankt", "gbr", "eu",
          "sarl", "sa", "sagl", "kgaa", "eg", "mbh", "gesellschaft", "und", "and", "der", "die", "das",
          "von", "vom", "zum", "zur", "am", "im", "in", "a", "an", "the", "de", "du", "la", "le", "les",
          "des", "et", "u", "mit", "bei", "fur", "for", "inh", "inhaber", "ehem", "sohne", "sohn", "geb",
          "sarl", "snc", "liq", "liquidation", "i", "l", "d", "ltd", "limited", "inc", "gen", "reg",
          "genossenschaft", "verein", "stiftung", "familie", "fam"}
GENERIC = {"brennerei", "destillerie", "distillerie", "distillery", "distillers", "distilling", "destille",
           "destillation", "distilleria", "edelbrennerei", "obstbrennerei", "whiskydestillerie",
           "whiskybrennerei", "whisky", "whiskey", "schnapsbrennerei", "edelbrand", "edelbrande", "brand",
           "brande", "spirits", "spirituosen", "spirit", "likor", "likore", "likormanufaktur", "manufaktur",
           "hofbrennerei", "brauerei", "weingut", "gasthof", "gasthaus", "hotel", "pension", "destillate",
           "destillat", "schnaps", "obst", "weinbau", "weinhaus", "kelterei", "mosterei", "hofladen",
           "brennhutte", "brennstube", "brennstuberl", "schaubrennerei", "hof", "wirtshaus", "landgasthof",
           "weinstube", "edel", "getranke", "feinbrand", "feinbrennerei", "brennhaus", "abfindungsbrennerei",
           "kleinbrennerei", "privatbrennerei", "hausbrennerei", "landbrennerei", "kornbrennerei", "korn",
           "gin", "vodka", "rum", "absinthe", "absinth", "eaux", "vie", "eau", "geist", "brennen", "genuss",
           "genussmanufaktur", "craft", "distiller", "bio", "weinkellerei", "kellerei", "winzer", "weine",
           "wein", "vin", "vins", "cave", "caves", "domaine", "brasserie", "birra", "bier", "malt",
           "single", "whiskys", "likoerfabrik", "likorfabrik", "spezialitaten", "spezialitatenbrennerei",
           "weinbrennerei", "weinbrand", "obstbrande", "verkauf", "shop", "hofladen", "cafe", "restaurant",
           "gastronomie", "landhotel", "gaststatte", "gasthof", "kraeuter", "krauter", "naturbrennerei",
           "qualitatsbrand", "edelbranntweinbrennerei", "branntweinbrennerei", "mountain", "berg"}
STOP = SUFFIX | GENERIC
COMMON_TOKEN_CAP = 3000
SIGNAL = {"brennerei", "destillerie", "distillerie", "distillery", "distillers", "distilling", "destille",
          "destillation", "edelbrennerei", "obstbrennerei", "whiskydestillerie", "whiskybrennerei", "whisky",
          "whiskey", "schnapsbrennerei", "edelbrand", "edelbrande", "brande", "spirits", "spirituosen",
          "spirit", "likor", "likore", "likormanufaktur", "hofbrennerei", "brauerei", "destillate",
          "destillat", "schnaps", "kelterei", "mosterei", "brennhutte", "brennstube", "schaubrennerei",
          "feinbrand", "feinbrennerei", "brennhaus", "kornbrennerei", "korn", "gin", "vodka", "rum",
          "absinthe", "absinth", "weinkellerei", "kellerei", "weinbrennerei", "weinbrand", "obstbrande",
          "likorfabrik", "likoerfabrik", "getranke", "weingut", "malt", "bier", "brasserie", "naturbrennerei",
          "edelbranntweinbrennerei", "branntweinbrennerei", "spezialitatenbrennerei", "brennen", "wein"}
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
def norm(s: str) -> str:
    s = (s or "").lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.replace("&", " and ").replace("'", "").replace("’", "").replace("´", "")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str, keep_generic: bool = False) -> frozenset:
    stop = SUFFIX if keep_generic else STOP
    return frozenset(t for t in norm(s).split() if t not in stop)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def city_eq(a: str, b: str) -> bool:
    a, b = norm(a).strip(), norm(b).strip()
    if not a or not b:
        return False
    a1, b1 = a.split()[0], b.split()[0]
    return a == b or a in b or b in a or (len(a1) > 3 and a1 == b1)


def grade(j: float, exact: bool, loc_ok: bool, active: bool, distinctive: bool) -> str | None:
    if exact or j >= 0.8:
        if not active:
            return "medium"
        return "high" if (loc_ok or distinctive) else "medium"
    if j >= 0.6:
        return "medium" if loc_ok else "low"
    if j >= 0.4 and loc_ok:
        return "low"
    return None


def has_signal(name: str) -> bool:
    return bool(toks(name, keep_generic=True) & SIGNAL)


def adjust(g: str | None, pin_toks: frozenset, company_name: str, pin_city: str, company_city: str,
           j: float, purpose_ok: bool = False) -> str | None:
    """Single-token or partial matches need a drinks word in the name (or a distilling purpose);
    a known city conflict drops one level."""
    if not g:
        return None
    if (len(pin_toks) <= 1 or j < 0.8) and not (has_signal(company_name) or purpose_ok):
        return None
    if pin_city and company_city and not city_eq(pin_city, company_city):
        if len(pin_toks) <= 1:
            return None
        g = {"high": "medium", "medium": "low", "low": None}[g]
    return g


def shared_ok(pin, qt: frozenset, ct: frozenset) -> bool:
    """The overlap must contain something other than the pin's own town name."""
    return bool((qt & ct) - toks(pin["city"]))


def exact_key(name: str) -> str:
    return " ".join(sorted(toks(name, keep_generic=True)))


def relation_for(pin_toks: frozenset, legal_name: str) -> str:
    return "self" if pin_toks & toks(legal_name) else "operator"


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
                     "toks": toks(p["name"]), "full": toks(p["name"], keep_generic=True),
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
        for t in p["toks"] | set(t for a in p["aliases"] for t in toks(a)):
            if len(t) >= 3 and not t.isdigit():
                want.add(t)
    n = kept = 0
    with bz2.open(src, "rt", encoding="utf-8") as fh, out.open("w", encoding="utf-8") as oh:
        for line in fh:
            n += 1
            d = json.loads(line)
            if toks(d.get("name", "")) & want:
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
    rows, index, exact = [], defaultdict(list), defaultdict(list)
    if not path.exists():
        print(f"warn: missing {path} (run --build-de-subset)", file=sys.stderr)
        return rows, index, exact
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            t = toks(r["name"] or "")
            if not t:
                continue
            i = len(rows)
            rows.append(r)
            for tok in t:
                index[tok].append(i)
            exact[exact_key(r["name"])].append(i)
    print(f"de: {len(rows)} OffeneRegister records indexed", file=sys.stderr)
    return rows, index, exact


def de_note(r, j, loc_ok, extra=""):
    return (f"name jaccard {j:.2f}; OffeneRegister status '{r['status']}' as of {(r['retrieved'] or '')[:10]} "
            f"(2017-2019 snapshot, not current); {r['native']}; registered office {r['office'] or 'n/a'}"
            f"{' (city agrees)' if loc_ok else ''}; address {r['address'] or 'n/a'}{extra}")


def match_de(pins, de):
    rows, index, _ = de
    out = []
    for p in pins:
        if p["country"] != "Germany" and not p["address"].endswith("Germany"):
            continue
        seen = {}
        for q in [p["name"]] + p["aliases"]:
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
                ct = toks(r["name"])
                if not shared_ok(p, qt, ct):
                    continue
                j = jaccard(qt, ct)
                exact = toks(q, True) == toks(r["name"], True)
                loc_ok = city_eq(p["city"], r["office"] or "") or (bool(p["pc"]) and p["pc"] in (r["address"] or ""))
                active = (r["status"] or "") == "currently registered"
                distinctive = len(qt) >= 2 and qt <= ct
                g = adjust(grade(j, exact, loc_ok, active, distinctive), qt, r["name"], p["city"], r["office"] or "", j)
                if not g:
                    continue
                score = j + (0.3 if active else 0) + (0.2 if loc_ok else 0) + (0.2 if exact else 0)
                key = r["number"]
                if key not in seen or seen[key][0] < score:
                    seen[key] = (score, g, r, j, loc_ok)
        for score, g, r, j, loc_ok in rank_and_emit(seen):
            out.append([p["slug"], p["name"], p["country"], "de-offeneregister", r["native"] or r["number"], r["name"],
                        relation_for(p["toks"], r["name"]), "offeneregister-bulk-name", g, "",
                        OC_URL.format(r["number"]), de_note(r, j, loc_ok)])
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
    """Free JustizOnline Firmenbuch search. 20 Sep 2026: the server answers 429 after roughly 100
    requests at one per second, so the client waits 3 s between calls and stops for the run on
    the first 429 (a 429 still counts against the cap; nothing is retried)."""
    INTERVAL = 3.0

    def __init__(self, cache_file: Path, fetch: bool, cap: int = 400):
        self.cache_file = cache_file
        self.cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
        self.fetch, self.cap, self.requests, self.last, self.blocked = fetch, cap, 0, 0.0, False

    def _get(self, url: str):
        if self.blocked:
            return None
        if self.requests >= self.cap:
            print("justizonline: request cap reached", file=sys.stderr)
            return None
        wait = self.INTERVAL - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": "stillbound-distillery-map crosswalk (stdlib urllib)",
                                                   "Accept": "application/json"})
        self.last = time.time()
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:  # noqa: BLE001
            print(f"justizonline: {url} failed: {e}", file=sys.stderr)
            if "429" in str(e):
                self.blocked = True
                print("justizonline: 429 received, no further requests this run", file=sys.stderr)
            return None

    def _save(self):
        self.cache_file.write_text(json.dumps(self.cache, indent=1, ensure_ascii=False))

    def search(self, q: str):
        key = "s:" + norm(q).strip()
        if key in self.cache:
            return self.cache[key]
        if not self.fetch:
            return None
        data = self._get(JOP_SEARCH + "?" + urllib.parse.urlencode({"term": q, "size": 10, "page": 0}))
        if data is None:
            return None
        self.cache[key] = data.get("companies", [])
        self._save()
        return self.cache[key]

    def detail(self, cid: str):
        key = "d:" + cid
        if key in self.cache:
            return self.cache[key]
        if not self.fetch:
            return None
        data = self._get(JOP_DETAIL.format(urllib.parse.quote(cid)))
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
        res = jop.search(term) if (fetch_names or ("s:" + norm(term).strip()) in jop.cache) else None
        if not res:
            continue
        hit = next((r for r in res if (r.get("fnr") or "").lower() == fnr), None)
        if hit:
            out[fnr] = hit
    print(f"at: {len(out)} OENACE 11.01 companies resolved to names", file=sys.stderr)
    return out


def grade_at(p, q, r, oenace):
    nm = r.get("name") or ""
    qt, ct = toks(q), toks(nm)
    if not qt or not shared_ok(p, qt, ct):
        return None
    j = jaccard(qt, ct)
    exact = toks(q, True) == toks(nm, True)
    loc_ok = city_eq(p["city"], r.get("domicile") or "")
    active = r.get("status") == "ACTIVE"
    code = oenace.get((r.get("fnr") or "").lower(), "")
    purpose_ok = code.startswith("1101")
    distinctive = len(qt) >= 2 and qt <= ct
    g = adjust(grade(j, exact, loc_ok, active, distinctive or purpose_ok), qt, nm, p["city"], r.get("domicile") or "", j, purpose_ok)
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
            full = [t for t in norm(q).split() if t not in SUFFIX]
            distinct = sorted(toks(q))
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
            out.append([p["slug"], p["name"], "Austria", "at-firmenbuch", fn_format(r.get("fnr") or ""), r.get("name"),
                        relation_for(p["toks"], r.get("name") or ""), how, g, "",
                        SRC_JOP + "/suchergebnis?search=" + urllib.parse.quote((r.get("fnr") or "").lstrip("0")), note])
    return out


# ------------------------------------------------------------ Switzerland ----
LINDAS_Q = """PREFIX schema: <http://schema.org/> PREFIX admin: <https://schema.ld.admin.ch/>
SELECT ?c ?legal ?uid ?loc ?street ?zip ?typ ?desc FROM <https://lindas.admin.ch/foj/zefix> WHERE {
 ?c a admin:ZefixOrganisation ; schema:legalName ?legal ; schema:identifier ?id .
 FILTER(CONTAINS(STR(?id),"/UID/")) BIND(STRAFTER(STR(?id),"/UID/") AS ?uid)
 OPTIONAL { ?c schema:address ?a . ?a schema:addressLocality ?loc . OPTIONAL { ?a schema:streetAddress ?street } OPTIONAL { ?a schema:postalCode ?zip } }
 OPTIONAL { ?c schema:additionalType ?typ } OPTIONAL { ?c schema:description ?desc }
} ORDER BY ?c LIMIT %d OFFSET %d"""


def fetch_lindas(cache: Path):
    """Page through the Zefix graph on LINDAS (one request per page, cached as CSV)."""
    n = 0
    for page in range(LINDAS_MAX_PAGES):
        path = cache / f"lindas-zefix-page-{page:02d}.csv"
        if path.exists():
            continue
        q = LINDAS_Q % (LINDAS_PAGE, page * LINDAS_PAGE)
        req = urllib.request.Request(LINDAS, data=urllib.parse.urlencode({"query": q}).encode(),
                                     headers={"Accept": "text/csv", "User-Agent": "stillbound-distillery-map crosswalk (stdlib urllib)"})
        t0 = time.time()
        body = None
        for attempt, backoff in enumerate((10, 30, 60)):
            n += 1
            try:
                with urllib.request.urlopen(req, timeout=600) as resp:
                    body = resp.read().decode("utf-8")
                break
            except Exception as e:  # noqa: BLE001  (504 gateway timeouts happen on big pages)
                print(f"lindas: page {page} attempt {attempt + 1} failed: {e}; retry in {backoff}s", file=sys.stderr)
                time.sleep(backoff)
        if body is None:
            print(f"lindas: giving up on page {page}", file=sys.stderr)
            break
        path.write_text(body, encoding="utf-8")
        rows = sum(1 for _ in csv.reader(body.splitlines())) - 1
        print(f"lindas: page {page} {rows} rows in {time.time() - t0:.0f}s", file=sys.stderr)
        if rows < LINDAS_PAGE:
            break
        time.sleep(1)
    print(f"lindas: {n} requests this run", file=sys.stderr)


def load_ch(cache: Path):
    rows, index = [], defaultdict(list)
    files = sorted(cache.glob("lindas-zefix-page-*.csv"))
    if not files:
        print("warn: no lindas-zefix-page-*.csv in cache (run --fetch-lindas)", file=sys.stderr)
        return rows, index
    seen = {}
    for f in files:
        with f.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                uid = r["uid"]
                if uid in seen:  # a company can have several address rows; keep the first
                    continue
                seen[uid] = len(rows)
                rows.append({"ehraid": r["c"].rsplit("/", 1)[-1], "name": r["legal"], "uid": uid, "loc": r["loc"],
                             "street": r["street"], "zip": r["zip"], "typ": r["typ"].rsplit("/", 1)[-1],
                             "purpose": bool(PURPOSE_RE.search(r.get("desc") or ""))})
                for tok in toks(r["legal"]):
                    index[tok].append(seen[uid])
    print(f"ch: {len(rows)} Zefix entities indexed from {len(files)} LINDAS pages; "
          f"{sum(1 for r in rows if r['purpose'])} with a distilling/spirits purpose", file=sys.stderr)
    return rows, index


def uid_format(uid: str) -> str:
    m = re.match(r"^CHE(\d{3})(\d{3})(\d{3})$", uid)
    return f"CHE-{m.group(1)}.{m.group(2)}.{m.group(3)}" if m else uid


def match_ch(pins, ch):
    rows, index = ch
    out = []
    for p in pins:
        if p["country"] != "Switzerland":
            continue
        seen = {}
        for q in [p["name"]] + p["aliases"]:
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
                ct = toks(r["name"])
                if not shared_ok(p, qt, ct):
                    continue
                j = jaccard(qt, ct)
                exact = toks(q, True) == toks(r["name"], True)
                loc_ok = city_eq(p["city"], r["loc"]) or (bool(p["pc"]) and p["pc"] == r["zip"])
                distinctive = len(qt) >= 2 and qt <= ct
                g = adjust(grade(j, exact, loc_ok, True, distinctive or r["purpose"]), qt, r["name"], p["city"], r["loc"], j, r["purpose"])
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
            out.append([p["slug"], p["name"], "Switzerland", "ch-zefix", uid_format(r["uid"]), r["name"],
                        relation_for(p["toks"], r["name"]), "lindas-zefix-bulk-name", g, "",
                        ZEFIX_URL.format(r["ehraid"]), note])
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
    rows, index = ch
    lic, cands = [], []
    exact = defaultdict(list)
    for i, r in enumerate(rows):
        exact[exact_key(r["name"])].append(i)
    for p in pins:
        if p["country"] != "Switzerland":
            continue
        best = {}
        for b in bazg:
            bt = toks(b["name"])
            if not bt or not shared_ok(p, p["toks"], bt):
                continue
            j = jaccard(p["toks"], bt)
            loc_ok = (bool(p["pc"]) and p["pc"] == b["zip"]) or city_eq(p["city"], b["town"])
            g = grade(j, toks(p["name"], True) == toks(b["name"], True), loc_ok, True, len(p["toks"]) >= 2 and p["toks"] <= bt)
            if not g or (j < 0.6 and not loc_ok):
                continue
            key = b["name"] + b["zip"]
            score = j + (0.3 if loc_ok else 0)
            if key not in best or best[key][0] < score:
                best[key] = (score, g, b, j, loc_ok)
        for score, g, b, j, loc_ok in sorted(best.values(), key=lambda x: -x[0])[:2]:
            lic.append([p["slug"], p["name"], "Switzerland", "ch-bazg-lohnbrennerei", "", b["name"], "self",
                        "bazg-list-name", g, "", SRC_BAZG,
                        f"BAZG Liste der Lohnbrennereien, Stand 01.07.2026; {b['zip']} {b['town']} {b['canton']}"
                        f"{' (location agrees)' if loc_ok else ''}; name jaccard {j:.2f}; contract distiller, not a register number"])
            for i in exact.get(exact_key(b["name"]), [])[:1]:
                r = rows[i]
                cands.append([p["slug"], p["name"], "Switzerland", "ch-zefix", uid_format(r["uid"]), r["name"],
                              relation_for(p["toks"], r["name"]), "bazg-list+lindas-zefix", g, "", ZEFIX_URL.format(r["ehraid"]),
                              f"legal name from the BAZG Lohnbrennerei list ({b['zip']} {b['town']}), name jaccard {j:.2f}; "
                              f"Zefix active entity, seat {r['loc']}, {r['street']}, {r['zip']}"])
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

    pins = load_pins()
    print(f"{len(pins)} DACH pins: " + ", ".join(f"{c} {sum(1 for p in pins if p['country'] == c)}" for c in COUNTRIES), file=sys.stderr)

    if args.build_de_subset:
        build_de_subset(cache, pins)
    if args.fetch_lindas:
        fetch_lindas(cache)

    de_c = match_de(pins, load_de(cache))
    jop = JustizOnline(cache / "justizonline-cache.json", args.fetch_justizonline, JOP_CAP)
    at_c = match_at(pins, jop, load_oenace(cache), args.fetch_oenace_names, args.jop_fallback)
    print(f"justizonline: {jop.requests} requests this run (cap {jop.cap}), {len(jop.cache)} cached calls", file=sys.stderr)
    ch = load_ch(cache)
    ch_c = match_ch(pins, ch)
    lic, bazg_c = match_bazg(pins, load_bazg(cache), ch)
    ch_c += bazg_c

    hand = []
    for slug, rows in HAND.items():
        p = next((x for x in pins if x["slug"] == slug), None)
        if not p:
            continue
        for reg, num, name, rel, conf, note, src in rows:
            hand.append([slug, p["name"], p["country"], reg, num, name, rel, "hand", conf, "", src, note])

    # a machine row that finds the hand row's company fills its number (hand rows carry the relation and evidence)
    for h in hand:
        if not h[4]:
            m = next((r for r in de_c + at_c + ch_c if r[0] == h[0] and r[3] == h[3] and norm(r[5]).strip() == norm(h[5]).strip()), None)
            if m:
                h[4], h[10], h[11] = m[4], m[10], h[11] + "; " + m[11]
    hand_keys = {(r[0], r[3], r[4]) for r in hand}
    hand_names = {(r[0], r[3], norm(r[5]).strip()) for r in hand}
    conf_rank = {"high": 0, "medium": 1, "low": 2}
    machine = {}
    for r in de_c + at_c + ch_c:
        if (r[0], r[3], r[4]) in hand_keys or (r[0], r[3], norm(r[5]).strip()) in hand_names:
            continue
        k = (r[0], r[3], r[4] or norm(r[5]).strip())
        if k not in machine or conf_rank[r[8]] < conf_rank[machine[k][8]]:
            machine[k] = r
    final = hand + list(machine.values())
    order = {s["slug"]: i for i, s in enumerate(pins)}
    final.sort(key=lambda r: (order[r[0]], r[3], conf_rank[r[8]], r[5]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    licences = sorted(lic, key=lambda r: (order[r[0]], r[3], conf_rank[r[8]]))
    for path, rows_ in ((OUT_CANDIDATES, final), (OUT_LICENCES, licences)):
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            w.writerows(rows_)

    by_c = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    best = {}
    for r in final:
        best[r[0]] = min(best.get(r[0], 9), conf_rank[r[8]])
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
