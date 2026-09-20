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
Names, grading and fetching come from scripts/crosswalklib (migrated 20 Sep 2026); country
parsing (postcode/département, NAF-code caveats, the Sirene search records) stays here.
"""
from __future__ import annotations

import argparse
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
OUT_CANDIDATES = OUT_DIR / "france-candidates.csv"

API = "https://recherche-entreprises.api.gouv.fr/search"
SRC_SIRENE = "https://annuaire-entreprises.data.gouv.fr/entreprise/{}"
NAF = "11.01Z"
PER_PAGE = 25
# 395 live requests already spent against this cache before the crosswalklib migration
# (docs/data-quality/france-registers-2026-09-20.md, "Request log, 20 Sep 2026"). Carried
# over via Fetcher(spent=...) so a rerun from the same cache never re-fetches them.
SPENT = 395

# NAF codes that make a name-search hit plausible as the distillery's own entity.
DRINKS_NAF = {"11.01Z", "11.02A", "11.02B", "11.03Z", "11.04Z", "11.05Z", "11.06Z", "11.07A", "11.07B",
              "46.34Z", "47.25Z", "01.21Z", "01.28Z", "20.53Z", "20.14Z", "10.89Z", "10.39B", "10.32Z"}
PROPERTY_NAF = ("68.", "41.", "42.", "43.")   # SCI / property / construction: never the operator
HOLDING_NAF = ("64.20Z", "70.10Z")             # holding: a parent at best

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
        if after and names.fold(after.group(1)).strip() not in territory:
            city = after.group(1)
        elif before:
            city = before.group(1)
    return {"slug": p["slug"], "name": p["name"], "address": addr, "postcode": postcode,
            "dept": dept_of(postcode), "city": names.fold(city).strip(),
            "aliases": ALIASES.get(p["slug"], [])}


def load_pins() -> list[dict]:
    g = json.loads(GEO.read_text(encoding="utf-8"))
    return [parse_pin(f["properties"]) for f in g["features"]
            if f["properties"].get("country") == "France"]


# --- API --------------------------------------------------------------------------------

def api_get(f: fetch.Fetcher, legacy_cache: dict, params: dict) -> dict | None:
    """One search request against the Recherche d'entreprises API. crosswalklib's Fetcher
    is tried first (its own cache, keyed by URL, and live fetches when allowed); a one-time
    shim then reads responses already cached by the pre-migration client, which keyed its
    cache by the query string instead. Never fetches beyond what allow/cap permit."""
    key = urllib.parse.urlencode(sorted(params.items()))
    url = f"{API}?{key}"
    body = f.get(url)
    if body is not None:
        return json.loads(body)
    return legacy_cache.get(key)


def fetch_naf(f: fetch.Fetcher, out: Path) -> list[dict]:
    """Page through every legal unit whose principal activity is 11.01Z."""
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    if not f.allow:
        print(f"warning: {out.name} missing and --fetch-naf not given; NAF pass skipped", file=sys.stderr)
        return []
    base = {"activite_principale": NAF, "per_page": PER_PAGE, "minimal": "true",
            "include": "siege,dirigeants,matching_etablissements"}
    first = api_get(f, {}, {**base, "page": 1})
    if not first or "results" not in first:
        return []
    results = list(first["results"])
    pages = int(first.get("total_pages") or 1)
    print(f"  NAF {NAF}: {first.get('total_results')} legal units, {pages} pages", file=sys.stderr)
    for page in range(2, pages + 1):
        d = api_get(f, {}, {**base, "page": page})
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
    names_ = []
    for n in (r.get("nom_raison_sociale"), re.sub(r"\s*\(.*\)\s*$", "", r.get("nom_complet") or ""),
              r.get("sigle"), siege.get("nom_commercial")):
        if n:
            names_.append(n)
    for e in (siege.get("liste_enseignes") or []):
        names_.append(e)
    sites = [siege] + list(r.get("matching_etablissements") or [])
    for e in r.get("matching_etablissements") or []:
        for n in (e.get("liste_enseignes") or []):
            names_.append(n)
        if e.get("nom_commercial"):
            names_.append(e["nom_commercial"])
    dirigeants = []
    for d in r.get("dirigeants") or []:
        if d.get("type_dirigeant") == "personne morale":
            dirigeants.append(f"{d.get('denomination')} ({d.get('qualite')}, SIREN {d.get('siren')})")
        else:
            dirigeants.append(f"{(d.get('prenoms') or '').split(' ')[0]} {d.get('nom') or ''} ({d.get('qualite')})".strip())
    legal = r.get("nom_raison_sociale") or re.sub(r"\s*\(.*\)\s*$", "", r.get("nom_complet") or "")
    return {
        "siren": r.get("siren"), "legal": legal, "names": [n for n in names_ if n],
        "etat": r.get("etat_administratif"), "naf": r.get("activite_principale"),
        "nature": r.get("nature_juridique"), "created": r.get("date_creation"),
        "sites": [{"siret": s.get("siret"), "postcode": s.get("code_postal") or "",
                   "city": names.fold(s.get("libelle_commune") or "").strip(),
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


def score_pin(pin: dict, rec: dict, in_naf_pull: bool) -> tuple[float, str, float, str] | None:
    """Return (score, grade, jaccard, matched_name) for the best name variant, or None.

    Base grade (exact/jaccard threshold x location x active x distinctive x signal) comes
    from crosswalklib.grading; strong location = postcode/city agree, weak = département
    agrees. Everything below that is France-specific: the containment upgrade for Google
    Places taglines, the département-conflict and no-signal demotions, and the NAF-code
    caveats (SCI/property, holding companies, non-drinks activity codes).
    """
    best = None
    queries = [pin["name"]] + pin["aliases"]
    head = query_name(pin["name"])
    if head != pin["name"]:
        queries.append(head)  # "Distillerie Octavie - Alambic & Spiritueux Haute-Savoie" -> "Distillerie Octavie"
    has_drinks_word = any(names.has_signal(n) for n in rec["names"])
    for q in queries:
        qt = names.tokens(q)
        if not qt:
            continue
        for name in rec["names"]:
            ct = names.tokens(name)
            if not ct:
                continue
            j = names.jaccard(qt, ct)
            exact = names.exact(q, name)
            site, city_ok, dept_ok = best_site(rec, pin)
            active = rec["etat"] == "A" and (site is None or site["etat"] in (None, "A"))
            distinctive = names.distinctive(q)
            loc = "strong" if city_ok else ("weak" if dept_ok else "none")
            evidence_signal = in_naf_pull or has_drinks_word
            g = grading.grade(Evidence(j, exact, loc, active, distinctive, evidence_signal))
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
            signal = evidence_signal or city_ok
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
            drinks = in_naf_pull or naf in DRINKS_NAF or has_drinks_word
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
        hits = [(h[0], grading.cap(h[1], "medium"), h[2], h[3], h[4], h[5]) if h in top else h for h in hits]
    mid = [h for h in hits if h[1] == "medium" and not h[5]]
    if len(mid) >= 3:
        hits = [(h[0], grading.cap(h[1], "low"), h[2], h[3], h[4], h[5]) if h in mid else h for h in hits]
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
        extra: str = "") -> dict:
    qt = names.tokens(pin["name"])
    for a in pin["aliases"]:
        qt = qt | names.tokens(a)
    naf = rec["naf"] or ""
    if relation is None:
        # A holding company (NAF 64.20Z/70.10Z) is a parent at best, never "self", whatever
        # the name overlap says.
        relation = "group" if naf.startswith(HOLDING_NAF) else \
            grading.relation_for(qt, names.tokens(" ".join(rec["names"])))
    note = note_for(rec, pin, j, matched, method)
    if naf.startswith(PROPERTY_NAF):
        note = "property/construction company, not the operator; " + note
    if extra:
        note = extra + "; " + note
    return rows.make(pin["slug"], pin["name"], "France", "fr-sirene", rec["siren"], rec["legal"],
                      relation, method, g, SRC_SIRENE.format(rec["siren"]), note)


# --- passes -----------------------------------------------------------------------------

LOW_VALUE = {"lavande", "lavandin", "huiles", "essentielles", "huile", "brasserie", "microbrasserie",
             "biere", "restaurant", "hotel", "galerie", "gites", "gite", "salle", "spectacle", "location",
             "cosmetique", "roseraie", "plantes", "aromatiques", "essences", "parfum", "cade"}


def low_value(name: str) -> bool:
    """Pins that are not spirits producers (lavender stills, breweries, venues) go last when the
    request budget is short."""
    return bool(set(names.fold(name).split()) & LOW_VALUE)


def naf_pass(pins: list[dict], recs: list[dict]) -> dict[str, list[tuple]]:
    index: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(recs):
        seen = set()
        for n in r["names"]:
            for t in names.tokens(n):
                if t not in seen:
                    index[t].append(i)
                    seen.add(t)
    cap = max(50, len(recs) // 10)
    out: dict[str, list[tuple]] = {}
    for p in pins:
        qt = set(names.tokens(p["name"]))
        for a in p["aliases"]:
            qt |= names.tokens(a)
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


def name_pass(pins: list[dict], f: fetch.Fetcher, legacy_cache: dict,
              skip: set[str]) -> tuple[dict[str, list[tuple]], list[str], list[str]]:
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
        distinct = " ".join(t for t in names.fold(head).split() if t not in names.STOP)
        if distinct and distinct != names.fold(head).strip() and len(distinct) >= 3:
            queries.append(distinct)
        queries = [q for q in queries if names.tokens(q)]
        if not queries:
            unsearched.append(p["slug"])  # nothing distinctive to search ("Distillerie", "ancienne distillerie")
            continue
        hits = []
        got_any = False
        for q in queries:
            params = {"q": q, "per_page": 10, "minimal": "true", "include": "siege,dirigeants,matching_etablissements"}
            if p["dept"]:
                params["departement"] = p["dept"]
            d = api_get(f, legacy_cache, params)
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

    # One-time shim for the pre-migration name-search cache: it is keyed by query string
    # (urlencode(sorted(params))), not by URL, so crosswalklib.fetch.Fetcher's own
    # URL-hash cache cannot see it directly. Read once here; api_get() falls back to it
    # when the Fetcher has neither a cache hit nor permission to fetch. Never re-fetched.
    legacy_path = cache / "name-search-cache.json"
    legacy_cache = json.loads(legacy_path.read_text(encoding="utf-8")) if legacy_path.exists() else {}

    f = fetch.Fetcher(cache, allow=False, cap=SPENT + args.max_requests, delay=1.0,
                       log=cache / "requests.log", spent=SPENT)

    f.allow = args.fetch_naf
    recs_raw = fetch_naf(f, cache / "naf-1101z.json")
    recs = [record(r) for r in recs_raw]
    print(f"NAF pull: {len(recs)} legal units", file=sys.stderr)
    naf_hits = naf_pass(pins, recs)
    strong = {s for s, hs in naf_hits.items() if any(h[1] in ("high", "medium") for h in hs)}
    print(f"NAF pass: {len(naf_hits)} pins with a candidate, {len(strong)} high/medium", file=sys.stderr)
    naf_made = f.made

    f.allow = args.fetch_names
    name_hits, searched, unsearched = name_pass(pins, f, legacy_cache, strong)
    print(f"name pass: {len(searched)} pins searched ({f.made - naf_made} live requests), "
          f"{len(name_hits)} with a candidate, {len(unsearched)} not searched", file=sys.stderr)

    out_rows: list[dict] = []
    hand_rows: list[dict] = []
    for p in pins:
        hand = HAND.get(p["slug"])
        emitted = set()
        for method, hits in (("sirene-naf-1101z", naf_hits.get(p["slug"], [])),
                             ("sirene-name-search", name_hits.get(p["slug"], []))):
            for score, g, j, matched, rec, _city in hits:
                if rec["siren"] in emitted:
                    continue
                emitted.add(rec["siren"])
                relation, extra, m = None, "", method
                if hand:
                    for legal, rel, why in hand:
                        lt = names.tokens(legal, names.SUFFIX)
                        if any(lt <= names.tokens(n, names.SUFFIX) or names.tokens(n, names.SUFFIX) <= lt
                               for n in rec["names"]):
                            relation, extra, m = rel, why, "hand"
                            if g != "high":
                                g = "high" if rec["etat"] == "A" else "medium"
                r = row(p, rec, g, j, matched, m, relation, extra)
                out_rows.append(r)
                if m == "hand":
                    hand_rows.append(r)
    grading.apply_guards(out_rows, hand_rows)
    # Every candidate is written. The builder resolves precedence against manual, operator
    # and Wikidata rows and keeps the best per (slug, registry, relation); a matcher that
    # reads the spine shrinks its own output every rebuild.

    args.out.parent.mkdir(parents=True, exist_ok=True)
    rows.write(args.out, out_rows, {p["slug"] for p in pins})

    # summary to stderr
    by = defaultdict(set)
    for r in out_rows:
        by[r["confidence"]].add(r["slug"])
    matched = set()
    for g in ("high", "medium", "low"):
        by[g] -= matched
        matched |= by[g]
    print(f"wrote {args.out} ({len(out_rows)} rows): high {len(by['high'])}, medium {len(by['medium'])}, "
          f"low {len(by['low'])}, unmatched {len(pins) - len(matched)} of {len(pins)}", file=sys.stderr)
    summary = {"pins": len(pins), "high": sorted(by["high"]), "medium": sorted(by["medium"]),
               "low": sorted(by["low"]), "unmatched": sorted(p["slug"] for p in pins if p["slug"] not in matched),
               "searched": searched, "unsearched": unsearched,
               "requests": {"naf": naf_made - SPENT, "names": f.made - naf_made}}
    (cache / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
