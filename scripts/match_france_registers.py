#!/usr/bin/env python3
"""
Match the map's French distilleries against the INSEE Sirene register (via the public
Annuaire des Entreprises search API) and write candidate rows for human review.

Registers (research: docs/data-quality/france-registers-2026-09-20.md):
  fr-sirene   INSEE Sirene, Licence Ouverte / Etalab 2.0. Read through the API Recherche
              d'entreprises (https://recherche-entreprises.api.gouv.fr, no key, max
              7 requests/second per IP per its OpenAPI description; this script stays at
              <= 1 request/second and a hard cap). company_number = SIREN (9 digits);
              the SIRET of the matched establishment goes in the note.
  Two passes: (1) every legal unit whose principal activity is NAF 11.01Z "Production de
  boissons alcooliques distillées" (2,610 units on 20 Sep 2026, 105 pages of 25), matched
  locally; (2) a name search per pin still unmatched, filtered to the pin's département
  when the address carries a postcode. Both passes are cached, so reruns are offline.
  Licence layer: French customs (DGDDI) publishes no list of entrepositaires agréés, so
  there is no france-licences.csv.

Run (offline, from cache):
  python3 scripts/match_france_registers.py --cache /path/to/cache
Fetch the NAF 11.01Z pull (105 requests, cached in <cache>/naf-1101z.json):
  python3 scripts/match_france_registers.py --cache /path/to/cache --fetch-naf
Fetch name searches for unmatched pins (cached in <cache>/name-search-cache.json):
  python3 scripts/match_france_registers.py --cache /path/to/cache --fetch-names --max-requests 280

Idempotent: same cache -> same output. Never fetches without --fetch-naf / --fetch-names.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "france-candidates.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

API = "https://recherche-entreprises.api.gouv.fr/search"
SRC_SIRENE = "https://annuaire-entreprises.data.gouv.fr/entreprise/{}"
USER_AGENT = "distillery-map-world crosswalk (stdlib urllib; <=1 req/s; contact via github)"
NAF = "11.01Z"
PER_PAGE = 25

# Legal-form suffixes and filler words dropped before comparing names.
SUFFIX = {"sas", "sasu", "sarl", "sa", "eurl", "scea", "earl", "gaec", "snc", "sci", "scop", "sca",
          "ste", "societe", "soc", "ets", "etablissement", "etablissements", "cie", "compagnie", "co",
          "company", "ltd", "inc", "groupe", "holding", "fils", "freres", "frere", "pere", "et", "and",
          "the", "de", "du", "des", "d", "l", "la", "le", "les", "a", "au", "aux", "en", "un", "une",
          "sur", "sous", "chez", "monsieur", "madame", "mr", "mme"}
GENERIC = {"distillerie", "distillery", "distilleries", "distillateur", "distillateurs", "distillation",
           "domaine", "maison", "chateau", "spiritueux", "spirits", "spirit", "artisanale", "artisanal",
           "artisanales", "craft", "micro", "microdistillerie", "brasserie", "brewery", "cave", "caves",
           "vignoble", "vignobles", "ferme", "famille", "bouilleur", "bouilleurs", "ambulant", "cru",
           "producteur", "producteurs", "exploitation", "agricole", "boutique", "shop", "visite", "visites",
           "site", "production"}
STOP = SUFFIX | GENERIC
# NAF codes that make a name-search hit plausible as the distillery's own entity.
DRINKS_NAF = {"11.01Z", "11.02A", "11.02B", "11.03Z", "11.04Z", "11.05Z", "11.06Z", "11.07A", "11.07B",
              "46.34Z", "47.25Z", "01.21Z", "01.28Z", "20.53Z", "20.14Z", "10.89Z", "10.39B", "10.32Z"}
PROPERTY_NAF = ("68.", "41.", "42.", "43.")   # SCI / property / construction: never the operator
HOLDING_NAF = ("64.20Z", "70.10Z")             # holding: a parent at best
SIGNAL = {"distillerie", "distillery", "distilleries", "distillateur", "distillateurs", "distillation",
          "spiritueux", "spirits", "spirit", "whisky", "whiskies", "whiskey", "gin", "rhum", "rhums", "rum",
          "vodka", "cognac", "armagnac", "calvados", "liqueur", "liqueurs", "liquoriste", "alcool",
          "alcools", "eau", "eaux", "vie", "absinthe", "pastis", "brandy", "alambic", "elixir",
          "lavande", "lavandin", "huiles", "essentielles", "brasserie", "cidre", "cidrerie", "vins",
          "vin", "champagne", "bouilleur", "bouilleurs", "marc", "kirsch", "mirabelle", "genievre"}

# Hand cases: group-run sites. Register checked through the same API (cached), the
# relation and group come from industry knowledge and are stated in the note.
HAND = {
    "hennessy": [
        ("JAS HENNESSY & CO", "operator", "Jas Hennessy & Co runs the Cognac site; owned by Moet Hennessy (LVMH, SIREN 775670417)"),
    ],
    "palais-benedictine-distillerie-bar-a-cocktails": [
        ("BENEDICTINE", "operator", "Bacardi group brand (Palais Benedictine, Fecamp); the search only returned historical Benedictine units, the live operating company still needs a hand lookup"),
    ],
    "distillerie-chartreuse-aiguenoire": [
        ("GRANDE CHARTREUSE", "operator", "Compagnie Francaise de la Grande Chartreuse (the Carthusian order's company) runs the Aiguenoire distillery; Chartreuse Diffusion is the sales arm"),
    ],
    "distillerie-saint-james": [
        ("SAINT JAMES", "operator", "Plantations Saint James / La Martiniquaise-Bardinet group (COFEPP)"),
    ],
    "distillerie-depaz": [
        ("DEPAZ", "operator", "La Martiniquaise-Bardinet group (COFEPP)"),
    ],
    "distillerie-dillon": [
        ("DILLON", "operator", "La Martiniquaise-Bardinet group (COFEPP); Dillon rum is distilled at Depaz since 2019, the Fort-de-France site is ageing and bottling"),
    ],
    "distillerie-la-mauny": [
        ("LA MAUNY", "operator", "Campari Group since 2019 (Rhumantilles: La Mauny and Trois Rivieres)"),
    ],
    "distillerie-jm": [
        ("RHUM JM", "operator", "Groupe Bernard Hayot (GBH)"),
    ],
    "calvados-pere-magloire": [
        ("PERE MAGLOIRE", "operator", "Spirit France Diffusion group (Pere Magloire, Boulard, Lecompte)"),
    ],
    "calvados-boulard": [
        ("CALVADOS BOULARD", "operator", "Spirit France Diffusion group (Pere Magloire, Boulard, Lecompte)"),
    ],
}
# Slugs whose pin name is not the register name; searched instead of / as well as the pin name.
ALIASES = {
    "hennessy": ["JAS HENNESSY"],
    "palais-benedictine-distillerie-bar-a-cocktails": ["BENEDICTINE"],
    "distillerie-chartreuse-aiguenoire": ["CHARTREUSE DIFFUSION"],
    "distillerie-saint-james": ["SAINT JAMES"],
    "distillerie-depaz": ["DEPAZ"],
    "distillerie-dillon": ["DILLON"],
    "distillerie-la-mauny": ["LA MAUNY"],
    "distillerie-jm": ["RHUM JM"],
    "calvados-pere-magloire": ["PERE MAGLOIRE"],
    "calvados-boulard": ["CALVADOS BOULARD"],
    "dhg-domaine-des-hautes-glaces": ["HAUTES GLACES"],
    "combier": ["DISTILLERIE COMBIER"],
    "distillerie-de-paris-parfum-spiritueux": ["DISTILLERIE DE PARIS"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", " ").replace("’", " ")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str, keep_generic: bool = False) -> frozenset:
    stop = SUFFIX if keep_generic else STOP
    return frozenset(t for t in norm(s).split() if t not in stop)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def has_signal(name: str) -> bool:
    return bool(toks(name, keep_generic=True) & SIGNAL)


def relation_for(pin_toks: frozenset, legal_name: str, naf: str = "") -> str:
    if naf.startswith(HOLDING_NAF):
        return "group"
    return "self" if pin_toks & toks(legal_name) else "operator"


def query_name(name: str) -> str:
    """Trim a Google-Places style name to its head: 'Distillerie X - gin, pastis...' -> 'Distillerie X'."""
    head = re.split(r"\s+[-|:/–—]\s+|\(|,", name, maxsplit=1)[0]
    words = head.split()
    return " ".join(words[:6]).strip() or name.strip()


# --- pins -------------------------------------------------------------------------------

def dept_of(postcode: str) -> str:
    if not postcode:
        return ""
    if postcode.startswith("97") or postcode.startswith("98"):
        return postcode[:3]
    if postcode.startswith("20"):
        return "2A" if postcode[:3] in ("200", "201") else "2B"
    return postcode[:2]


def parse_pin(p: dict) -> dict:
    addr = p.get("address") or ""
    m = re.search(r"\b(\d{5})\b", addr)
    postcode = m.group(1) if m else ""
    city = ""
    if m:
        after = re.search(r"\b\d{5}\b\s+([^,]+)", addr)
        before = re.search(r"([^,]+?)\s+\d{5}\b", addr)
        territory = {"", "france", "guadeloupe", "martinique", "reunion", "la reunion", "guyane",
                     "guyane francaise", "mayotte", "corse", "french guiana"}
        if after and norm(after.group(1)).strip() not in territory:
            city = after.group(1)
        elif before:
            city = before.group(1)
    return {"slug": p["slug"], "name": p["name"], "address": addr, "postcode": postcode,
            "dept": dept_of(postcode), "city": norm(city).strip(),
            "aliases": ALIASES.get(p["slug"], [])}


def load_pins() -> list[dict]:
    g = json.loads(GEO.read_text(encoding="utf-8"))
    return [parse_pin(f["properties"]) for f in g["features"]
            if f["properties"].get("country") == "France"]


# --- API --------------------------------------------------------------------------------

class Client:
    """Rate-limited, capped, cached GET against the Annuaire des Entreprises search API."""

    def __init__(self, cache_path: Path, allow: bool, cap: int, log: Path | None):
        self.cache_path = cache_path
        self.cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        self.allow = allow
        self.cap = cap
        self.made = 0
        self.log = log
        self._last = 0.0

    def get(self, params: dict) -> dict | None:
        key = urllib.parse.urlencode(sorted(params.items()))
        if key in self.cache:
            return self.cache[key]
        if not self.allow:
            return None
        if self.made >= self.cap:
            print(f"  cap reached ({self.cap}); not fetching {key}", file=sys.stderr)
            return None
        wait = 1.0 - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        url = f"{API}?{key}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        self._last = time.monotonic()
        self.made += 1
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry = int(e.headers.get("Retry-After", "5"))
                print(f"  429, sleeping {retry}s", file=sys.stderr)
                time.sleep(retry)
                self.made -= 1
                return self.get(params)
            print(f"  HTTP {e.code} for {url}", file=sys.stderr)
            data = {"error": e.code, "results": []}
        if self.log:
            with self.log.open("a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} GET {url} -> {data.get('total_results', data.get('error'))}\n")
        self.cache[key] = data
        self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False), encoding="utf-8")
        return data


def fetch_naf(client: Client, out: Path) -> list[dict]:
    """Page through every legal unit whose principal activity is 11.01Z."""
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    if not client.allow:
        print(f"warning: {out.name} missing and --fetch-naf not given; NAF pass skipped", file=sys.stderr)
        return []
    base = {"activite_principale": NAF, "per_page": PER_PAGE, "minimal": "true",
            "include": "siege,dirigeants,matching_etablissements"}
    first = client.get({**base, "page": 1})
    if not first or "results" not in first:
        return []
    results = list(first["results"])
    pages = int(first.get("total_pages") or 1)
    print(f"  NAF {NAF}: {first.get('total_results')} legal units, {pages} pages", file=sys.stderr)
    for page in range(2, pages + 1):
        d = client.get({**base, "page": page})
        if not d or "results" not in d:
            print(f"  stopped at page {page}", file=sys.stderr)
            break
        results.extend(d["results"])
    out.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    return results


# --- records ----------------------------------------------------------------------------

def record(r: dict) -> dict:
    """Flatten one API result into the fields the matcher needs."""
    siege = r.get("siege") or {}
    names = []
    for n in (r.get("nom_raison_sociale"), re.sub(r"\s*\(.*\)\s*$", "", r.get("nom_complet") or ""),
              r.get("sigle"), siege.get("nom_commercial")):
        if n:
            names.append(n)
    for e in (siege.get("liste_enseignes") or []):
        names.append(e)
    sites = [siege] + list(r.get("matching_etablissements") or [])
    for e in r.get("matching_etablissements") or []:
        for n in (e.get("liste_enseignes") or []):
            names.append(n)
        if e.get("nom_commercial"):
            names.append(e["nom_commercial"])
    dirigeants = []
    for d in r.get("dirigeants") or []:
        if d.get("type_dirigeant") == "personne morale":
            dirigeants.append(f"{d.get('denomination')} ({d.get('qualite')}, SIREN {d.get('siren')})")
        else:
            dirigeants.append(f"{(d.get('prenoms') or '').split(' ')[0]} {d.get('nom') or ''} ({d.get('qualite')})".strip())
    legal = r.get("nom_raison_sociale") or re.sub(r"\s*\(.*\)\s*$", "", r.get("nom_complet") or "")
    return {
        "siren": r.get("siren"), "legal": legal, "names": [n for n in names if n],
        "etat": r.get("etat_administratif"), "naf": r.get("activite_principale"),
        "nature": r.get("nature_juridique"), "created": r.get("date_creation"),
        "sites": [{"siret": s.get("siret"), "postcode": s.get("code_postal") or "",
                   "city": norm(s.get("libelle_commune") or "").strip(),
                   "dept": s.get("departement") or dept_of(s.get("code_postal") or ""),
                   "etat": s.get("etat_administratif"), "siege": bool(s.get("est_siege"))}
                  for s in sites if s],
        "dirigeants": dirigeants[:3],
    }


def best_site(rec: dict, pin: dict) -> tuple[dict | None, bool, bool]:
    """Pick the establishment closest to the pin: postcode/city match, then département, then siège."""
    city_ok = dept_ok = False
    chosen = None
    for s in rec["sites"]:
        c = bool(pin["postcode"]) and s["postcode"] == pin["postcode"]
        c = c or (bool(pin["city"]) and bool(s["city"]) and (pin["city"] == s["city"] or pin["city"] in s["city"] or s["city"] in pin["city"]))
        d = bool(pin["dept"]) and s["dept"] == pin["dept"]
        if c and not city_ok:
            chosen, city_ok, dept_ok = s, True, d or dept_ok
        elif d and not city_ok and not dept_ok:
            chosen, dept_ok = s, True
    if chosen is None:
        chosen = next((s for s in rec["sites"] if s["siege"]), rec["sites"][0] if rec["sites"] else None)
    return chosen, city_ok, dept_ok or city_ok


def grade(j: float, exact: bool, city_ok: bool, dept_ok: bool, active: bool, distinctive: bool) -> str | None:
    if exact or j >= 0.8:
        if not active:
            return "medium"
        return "high" if (city_ok or distinctive) else "medium"
    if j >= 0.6:
        return "medium" if (city_ok or dept_ok) else "low"
    if j >= 0.4 and (city_ok or (dept_ok and distinctive)):
        return "low"
    return None


def score_pin(pin: dict, rec: dict, in_naf_pull: bool) -> tuple[float, str, float, str] | None:
    """Return (score, grade, jaccard, matched_name) for the best name variant, or None."""
    best = None
    queries = [pin["name"]] + pin["aliases"]
    head = query_name(pin["name"])
    if head != pin["name"]:
        queries.append(head)  # "Distillerie Octavie - Alambic & Spiritueux Haute-Savoie" -> "Distillerie Octavie"
    for q in queries:
        qt = toks(q)
        if not qt:
            continue
        for name in rec["names"]:
            ct = toks(name)
            if not ct:
                continue
            j = jaccard(qt, ct)
            exact = toks(q, True) == toks(name, True) or qt == ct
            site, city_ok, dept_ok = best_site(rec, pin)
            active = rec["etat"] == "A" and (site is None or site["etat"] in (None, "A"))
            distinctive = (len(qt) >= 2 and qt <= ct) or (len(qt) == 1 and len(next(iter(qt))) >= 7 and qt <= ct)
            g = grade(j, exact, city_ok, dept_ok, active, distinctive)
            shared = qt & ct
            if g in (None, "low") and city_ok and shared and (qt <= ct or ct <= qt):
                # One name is contained in the other and the postcode or city agrees
                # (Google Places names carry taglines: "Distillerie du Tigre Thire" vs
                # "DISTILLERIE DU TIGRE"). Strong when the shared part is distinctive.
                strong = len(shared) >= 2 or max(len(t) for t in shared) >= 6
                g = ("high" if strong else "medium") if active else "medium"
                j = max(j, len(shared) / max(len(qt), len(ct)))
            if not g:
                continue
            # A single-token or partial match needs a drinks word somewhere in the company's names,
            # unless the company is in the 11.01Z pull (already a distiller) or the postcode agrees.
            signal = in_naf_pull or city_ok or any(has_signal(n) for n in rec["names"])
            if (len(qt) <= 1 or j < 0.8) and not signal:
                g = {"high": "medium", "medium": "low", "low": None}[g]
                if not g:
                    continue
            if pin["dept"] and not dept_ok and not exact:
                # every known site is in another département: another business with the same name
                g = {"high": "medium", "medium": "low", "low": None}[g]
                if not g:
                    continue
            naf = rec["naf"] or ""
            drinks = in_naf_pull or naf in DRINKS_NAF or any(has_signal(n) for n in rec["names"])
            if naf.startswith(PROPERTY_NAF):
                g = "low"
            elif naf.startswith(HOLDING_NAF):
                g = "medium" if g == "high" else g
            elif not drinks and not city_ok:
                g = {"high": "medium", "medium": "low", "low": "low"}[g]
            elif not in_naf_pull and not city_ok and not dept_ok and naf not in DRINKS_NAF and g == "high":
                g = "medium"  # name only, no location, activity code says nothing about drinks
            score = j + (0.3 if active else 0) + (0.2 if city_ok else 0) + (0.1 if dept_ok else 0) + (0.1 if in_naf_pull else 0)
            if best is None or score > best[0]:
                best = (score, g, j, name, city_ok)
    return best


def disambiguate(hits: list[tuple]) -> list[tuple]:
    """Two or more distinct companies at the top grade with no postcode/city agreement means the
    name alone cannot pick one: drop those a grade."""
    top = [h for h in hits if h[1] == "high" and not h[5]]
    if len(top) >= 2:
        hits = [(h[0], "medium", h[2], h[3], h[4], h[5]) if h in top else h for h in hits]
    mid = [h for h in hits if h[1] == "medium" and not h[5]]
    if len(mid) >= 3:
        hits = [(h[0], "low", h[2], h[3], h[4], h[5]) if h in mid else h for h in hits]
    return hits


def note_for(rec: dict, pin: dict, j: float, matched: str, method: str) -> str:
    site, city_ok, dept_ok = best_site(rec, pin)
    bits = [f"name jaccard {j:.2f} on '{matched}'",
            f"UL {'active' if rec['etat'] == 'A' else 'ceased'}",
            f"NAF {rec['naf']}", f"created {rec['created'] or 'n/a'}"]
    if site:
        bits.append(f"SIRET {site['siret']} {site['postcode']} {site['city'].upper()}"
                    f"{' (postcode/city agrees)' if city_ok else (' (departement agrees)' if dept_ok else '')}"
                    f"{' siege' if site['siege'] else ''}{' closed' if site['etat'] == 'F' else ''}")
    if rec["dirigeants"]:
        bits.append("dirigeants: " + "; ".join(rec["dirigeants"]))
    return "; ".join(bits)


def row(pin: dict, rec: dict, g: str, j: float, matched: str, method: str, relation: str | None = None,
        extra: str = "") -> list[str]:
    qt = toks(pin["name"])
    for a in pin["aliases"]:
        qt = qt | toks(a)
    rel = relation or relation_for(qt, " ".join(rec["names"]), rec["naf"] or "")
    note = note_for(rec, pin, j, matched, method)
    if (rec["naf"] or "").startswith(PROPERTY_NAF):
        note = "property/construction company, not the operator; " + note
    if extra:
        note = extra + "; " + note
    return [pin["slug"], pin["name"], "France", "fr-sirene", rec["siren"], rec["legal"], rel, method, g, "",
            SRC_SIRENE.format(rec["siren"]), note]


# --- passes -----------------------------------------------------------------------------

LOW_VALUE = {"lavande", "lavandin", "huiles", "essentielles", "huile", "brasserie", "microbrasserie",
             "biere", "restaurant", "hotel", "galerie", "gites", "gite", "salle", "spectacle", "location",
             "cosmetique", "roseraie", "plantes", "aromatiques", "essences", "parfum", "cade"}


def low_value(name: str) -> bool:
    """Pins that are not spirits producers (lavender stills, breweries, venues) go last when the
    request budget is short."""
    return bool(set(norm(name).split()) & LOW_VALUE)

def naf_pass(pins: list[dict], recs: list[dict]) -> dict[str, list[tuple]]:
    index: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(recs):
        seen = set()
        for n in r["names"]:
            for t in toks(n):
                if t not in seen:
                    index[t].append(i)
                    seen.add(t)
    cap = max(50, len(recs) // 10)
    out: dict[str, list[tuple]] = {}
    for p in pins:
        qt = set(toks(p["name"]))
        for a in p["aliases"]:
            qt |= toks(a)
        cand = set()
        for t in qt:
            post = index.get(t, [])
            if 0 < len(post) <= cap:
                cand.update(post)
        hits = []
        for i in cand:
            s = score_pin(p, recs[i], True)
            if s:
                hits.append((s[0], s[1], s[2], s[3], recs[i], s[4]))
        hits.sort(key=lambda x: -x[0])
        hits = disambiguate(hits[:3])
        if any(h[1] == "high" for h in hits):
            hits = [h for h in hits if h[1] != "low"]
        if hits:
            out[p["slug"]] = hits
    return out


def name_pass(pins: list[dict], client: Client, skip: set[str]) -> tuple[dict[str, list[tuple]], list[str], list[str]]:
    """One search per pin (plus aliases) not already matched high/medium. Returns hits, searched, unsearched."""
    out: dict[str, list[tuple]] = {}
    searched, unsearched = [], []
    # Pins with a postcode first: the département filter makes those searches precise.
    order = sorted([p for p in pins if p["slug"] not in skip], key=lambda p: (not p["dept"], low_value(p["name"]), p["slug"]))
    for p in order:
        head = query_name(p["name"])
        queries = list(p["aliases"]) + ([head] if head not in p["aliases"] else [])
        # The API ANDs every term, so "Cognac Frapin" or "Distillery G. Miclo" returns nothing
        # when the legal name is "FRAPIN" / "DISTILLERIE G. MICLO". Second try: distinctive
        # tokens only ("frapin", "g miclo"), still filtered to the département.
        distinct = " ".join(t for t in norm(head).split() if t not in STOP)
        if distinct and distinct != norm(head).strip() and len(distinct) >= 3:
            queries.append(distinct)
        queries = [q for q in queries if toks(q)]
        if not queries:
            unsearched.append(p["slug"])  # nothing distinctive to search ("Distillerie", "ancienne distillerie")
            continue
        hits = []
        got_any = False
        for q in queries:
            params = {"q": q, "per_page": 10, "minimal": "true", "include": "siege,dirigeants,matching_etablissements"}
            if p["dept"]:
                params["departement"] = p["dept"]
            d = client.get(params)
            if d is None:
                continue
            got_any = True
            seen = set()
            for r in d.get("results") or []:
                rec = record(r)
                if rec["siren"] in seen:
                    continue
                seen.add(rec["siren"])
                s = score_pin(p, rec, rec["naf"] == NAF)
                if s:
                    hits.append((s[0], s[1], s[2], s[3], rec, s[4]))
            if any(h[1] in ("high", "medium") for h in hits):
                break  # alias found it; no need for the raw pin name
        (searched if got_any else unsearched).append(p["slug"])
        if not hits:
            continue
        best: dict[str, tuple] = {}
        for h in hits:
            if h[4]["siren"] not in best or best[h[4]["siren"]][0] < h[0]:
                best[h[4]["siren"]] = h
        ranked = disambiguate(sorted(best.values(), key=lambda x: -x[0])[:3])
        if any(h[1] == "high" for h in ranked):
            ranked = [h for h in ranked if h[1] != "low"]
        out[p["slug"]] = ranked
    return out, searched, unsearched


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", required=True, help="directory for cached API responses")
    ap.add_argument("--fetch-naf", action="store_true", help="allow the NAF 11.01Z paged pull (cached)")
    ap.add_argument("--fetch-names", action="store_true", help="allow per-pin name searches (cached)")
    ap.add_argument("--max-requests", type=int, default=280, help="hard cap on live requests this run")
    ap.add_argument("--out", type=Path, default=OUT_CANDIDATES)
    args = ap.parse_args()
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)

    pins = load_pins()
    print(f"{len(pins)} French pins; {sum(1 for p in pins if p['postcode'])} with a postcode", file=sys.stderr)

    log = cache / "request-log.txt"
    naf_client = Client(cache / "naf-search-cache.json", args.fetch_naf, args.max_requests, log)
    recs_raw = fetch_naf(naf_client, cache / "naf-1101z.json")
    recs = [record(r) for r in recs_raw]
    print(f"NAF pull: {len(recs)} legal units", file=sys.stderr)
    naf_hits = naf_pass(pins, recs)
    strong = {s for s, hs in naf_hits.items() if any(h[1] in ("high", "medium") for h in hs)}
    print(f"NAF pass: {len(naf_hits)} pins with a candidate, {len(strong)} high/medium", file=sys.stderr)

    name_client = Client(cache / "name-search-cache.json", args.fetch_names,
                         max(0, args.max_requests - naf_client.made), log)
    name_hits, searched, unsearched = name_pass(pins, name_client, strong)
    print(f"name pass: {len(searched)} pins searched ({name_client.made} live requests), "
          f"{len(name_hits)} with a candidate, {len(unsearched)} not searched", file=sys.stderr)

    rows: list[list[str]] = []
    for p in pins:
        hand = HAND.get(p["slug"])
        emitted = set()
        for method, hits in (("sirene-naf-1101z", naf_hits.get(p["slug"], [])),
                             ("sirene-name-search", name_hits.get(p["slug"], []))):
            for score, g, j, matched, rec, _city in hits:
                if rec["siren"] in emitted:
                    continue
                emitted.add(rec["siren"])
                relation, extra = None, ""
                if hand:
                    for legal, rel, why in hand:
                        lt = toks(legal, True)
                        if any(lt <= toks(n, True) or toks(n, True) <= lt for n in rec["names"]):
                            relation, extra, method = rel, why, "hand"
                            if g != "high":
                                g = "high" if rec["etat"] == "A" else "medium"
                rows.append(row(p, rec, g, j, matched, method, relation, extra))
    # Rows already in the generated spine (Wikidata gave Warenghem and Hennessy/LVMH) are not repeated.
    spine = OUT_DIR / "company-crosswalk.csv"
    if spine.exists():
        with spine.open(encoding="utf-8") as f:
            have = {(r["slug"], r["company_number"]) for r in csv.DictReader(f) if r.get("country") == "France"}
        before = len(rows)
        rows = [r for r in rows if (r[0], r[4]) not in have]
        if before != len(rows):
            print(f"dropped {before - len(rows)} rows already in company-crosswalk.csv", file=sys.stderr)
    rows.sort(key=lambda r: (r[0], {"high": 0, "medium": 1, "low": 2}[r[8]], r[4]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows)

    # summary to stderr
    by = defaultdict(set)
    for r in rows:
        by[r[8]].add(r[0])
    matched = set()
    for g in ("high", "medium", "low"):
        by[g] -= matched
        matched |= by[g]
    print(f"wrote {args.out} ({len(rows)} rows): high {len(by['high'])}, medium {len(by['medium'])}, "
          f"low {len(by['low'])}, unmatched {len(pins) - len(matched)} of {len(pins)}", file=sys.stderr)
    summary = {"pins": len(pins), "high": sorted(by["high"]), "medium": sorted(by["medium"]),
               "low": sorted(by["low"]), "unmatched": sorted(p["slug"] for p in pins if p["slug"] not in matched),
               "searched": searched, "unsearched": unsearched,
               "requests": {"naf": naf_client.made, "names": name_client.made}}
    (cache / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
