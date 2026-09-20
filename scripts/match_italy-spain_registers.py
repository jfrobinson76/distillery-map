#!/usr/bin/env python3
"""
Match the map's Italian and Spanish distilleries to register numbers, and write candidate
rows for human review. Research: docs/data-quality/italy-spain-registers-2026-09-20.md.

Neither country has a free, bulk or API company register (checked 20 Sep 2026):
  Italy   Registro Imprese free search returns name, address, legal form and PEC only (no
          codice fiscale) and its service notes forbid automatic or mass extraction; the
          Agenzia delle Entrate VAT check is one number at a time behind a CAPTCHA; there is
          no national open-data extract on dati.gov.it; Agenzia delle Dogane publishes no
          list of alcohol depositi fiscali.
  Spain   Registro Mercantil Central name lookups are paid; the AEAT publishes nothing;
          datos.gob.es holds statistics only; BORME is open data (BOE licence) but only as
          daily per-province PDFs of register acts with no NIF.

What this script does instead:
  it-registro-imprese  The codice fiscale / partita IVA (11 digits) is read from the pin's
                       OWN website. Italian law (art. 35 DPR 633/1972) requires it on the
                       site, so most sites carry "P.IVA 01234567890" in the footer or on
                       the privacy/contact page. Checksum-validated. The legal name is the
                       company name printed next to the number when one can be found.
  es-rmc               The NIF (CIF) is read the same way from the pin's own website
                       (LSSI art. 10 requires it, usually on the "aviso legal" page).
                       Checksum-validated. The register number field carries the NIF; the
                       Registro Mercantil hoja number is not free.
  es-rgseaa            Licence layer for Spain: AESAN's RGSEAA food-business register
                       (bulk xlsx, key 30 "Bebidas alcoholicas", reuse allowed with
                       attribution) matched by name + province. Gives the legal name and
                       the RGSEAA number; no NIF. Rows go to italy-spain-licences.csv.
  Hand rows            Well-known group-run sites.

Run offline (from cached files):
  python3 scripts/match_italy-spain_registers.py --cache /path/to/cache
Fetch the pins' own websites (1 request/second, hard cap, cached in <cache>/websites/):
  python3 scripts/match_italy-spain_registers.py --cache /path/to/cache --fetch-websites
Cache dir should hold rgseaa-industrias.csv (converted from the AESAN xlsx; see the note).
Idempotent: same cache -> same outputs. Never fetches without --fetch-websites.
Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import html as htmlmod
import json
import re
import socket
import ssl
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
OUT_CANDIDATES = OUT_DIR / "italy-spain-candidates.csv"
OUT_LICENCES = OUT_DIR / "italy-spain-licences.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

SRC_RGSEAA = "https://www.aesan.gob.es/registro-sanitario/empresas-alimentarias"
SRC_RI = "https://www.registroimprese.it/"
SRC_RMC = "https://www.rmc.es/"

FETCH_CAP = 800          # hard cap on website requests per run
FETCH_DELAY = 1.0        # seconds between requests
FETCH_TIMEOUT = 12
UA = "Mozilla/5.0 (compatible; distillery-map-crosswalk/1.0; +https://github.com/) research fetch, one page per site"

SUFFIX = {"srl", "spa", "snc", "sas", "ss", "sr", "sl", "slu", "sa", "sau", "sc", "scoop", "sll",
          "soc", "societa", "sociedad", "agricola", "agr", "coop", "cooperativa", "limitada", "anonima",
          "gmbh", "ohg", "kg", "ltd", "limited", "srls", "the", "il", "la", "le", "lo", "gli", "i",
          "el", "los", "las", "de", "del", "della", "delle", "dei", "degli", "di", "da", "e", "y", "and",
          "&", "a", "al", "en", "in", "con", "per", "por", "fu", "f", "lli", "flli", "fratelli", "hermanos",
          "hnos", "figli", "hijos", "eredi", "ditta", "cav", "dott", "dr"}
GENERIC = {"distilleria", "distillerie", "distillerias", "distillery", "distilleries", "distillatori",
           "distillati", "destileria", "destilerias", "destilerías", "destilería", "destiladora",
           "destilados", "destilacion", "brennerei", "destillerie", "brennereien", "spirits", "spirit",
           "liquori", "liquorificio", "liquoristeria", "licores", "licoreria", "bodega", "bodegas",
           "azienda", "aziende", "agricola", "cantina", "cantine", "vini", "vino", "grappa", "grappe",
           "acquavite", "acquaviti", "aguardientes", "aguardiente", "orujos", "orujo", "gin", "vodka",
           "whisky", "whiskey", "rum", "ron", "craft", "artigianale", "artigianali", "artesanal",
           "artesanos", "artesana", "premium", "alcoholes", "alcoles", "elaborados", "productos",
           "prodotti", "casa", "antica", "antico", "storica", "official", "sito", "web"}
STOP = SUFFIX | GENERIC
SIGNAL = GENERIC - {"azienda", "aziende", "agricola", "casa", "antica", "antico", "storica", "official",
                    "sito", "web", "craft", "premium", "prodotti", "productos", "elaborados"}

# Italian province code -> region (for the per-region table only)
IT_REGION = {
    "AG": "Sicilia", "CL": "Sicilia", "CT": "Sicilia", "EN": "Sicilia", "ME": "Sicilia", "PA": "Sicilia",
    "RG": "Sicilia", "SR": "Sicilia", "TP": "Sicilia",
    "AL": "Piemonte", "AT": "Piemonte", "BI": "Piemonte", "CN": "Piemonte", "NO": "Piemonte", "TO": "Piemonte",
    "VB": "Piemonte", "VC": "Piemonte", "AO": "Valle d'Aosta",
    "BG": "Lombardia", "BS": "Lombardia", "CO": "Lombardia", "CR": "Lombardia", "LC": "Lombardia",
    "LO": "Lombardia", "MB": "Lombardia", "MI": "Lombardia", "MN": "Lombardia", "PV": "Lombardia",
    "SO": "Lombardia", "VA": "Lombardia",
    "BZ": "Trentino-Alto Adige", "TN": "Trentino-Alto Adige",
    "BL": "Veneto", "PD": "Veneto", "RO": "Veneto", "TV": "Veneto", "VE": "Veneto", "VI": "Veneto", "VR": "Veneto",
    "GO": "Friuli-Venezia Giulia", "PN": "Friuli-Venezia Giulia", "TS": "Friuli-Venezia Giulia",
    "UD": "Friuli-Venezia Giulia",
    "GE": "Liguria", "IM": "Liguria", "SP": "Liguria", "SV": "Liguria",
    "BO": "Emilia-Romagna", "FC": "Emilia-Romagna", "FE": "Emilia-Romagna", "MO": "Emilia-Romagna",
    "PC": "Emilia-Romagna", "PR": "Emilia-Romagna", "RA": "Emilia-Romagna", "RE": "Emilia-Romagna",
    "RN": "Emilia-Romagna",
    "AR": "Toscana", "FI": "Toscana", "GR": "Toscana", "LI": "Toscana", "LU": "Toscana", "MS": "Toscana",
    "PI": "Toscana", "PO": "Toscana", "PT": "Toscana", "SI": "Toscana",
    "PG": "Umbria", "TR": "Umbria",
    "AN": "Marche", "AP": "Marche", "FM": "Marche", "MC": "Marche", "PU": "Marche",
    "FR": "Lazio", "LT": "Lazio", "RI": "Lazio", "RM": "Lazio", "VT": "Lazio",
    "AQ": "Abruzzo", "CH": "Abruzzo", "PE": "Abruzzo", "TE": "Abruzzo",
    "CB": "Molise", "IS": "Molise",
    "AV": "Campania", "BN": "Campania", "CE": "Campania", "NA": "Campania", "SA": "Campania",
    "BA": "Puglia", "BT": "Puglia", "BR": "Puglia", "FG": "Puglia", "LE": "Puglia", "TA": "Puglia",
    "MT": "Basilicata", "PZ": "Basilicata",
    "CS": "Calabria", "CZ": "Calabria", "KR": "Calabria", "RC": "Calabria", "VV": "Calabria",
    "CA": "Sardegna", "NU": "Sardegna", "OR": "Sardegna", "SS": "Sardegna", "SU": "Sardegna",
}
# Spanish province -> comunidad autonoma (address form "..., <Provincia>, Spain")
ES_CCAA = {
    "a coruna": "Galicia", "lugo": "Galicia", "ourense": "Galicia", "pontevedra": "Galicia",
    "asturias": "Asturias", "cantabria": "Cantabria", "bizkaia": "Pais Vasco", "gipuzkoa": "Pais Vasco",
    "araba": "Pais Vasco", "alava": "Pais Vasco", "navarra": "Navarra", "la rioja": "La Rioja",
    "huesca": "Aragon", "zaragoza": "Aragon", "teruel": "Aragon",
    "barcelona": "Cataluna", "girona": "Cataluna", "lleida": "Cataluna", "tarragona": "Cataluna",
    "illes balears": "Illes Balears", "islas baleares": "Illes Balears",
    "valencia": "Comunitat Valenciana", "alicante": "Comunitat Valenciana", "alacant": "Comunitat Valenciana",
    "castellon": "Comunitat Valenciana", "castello": "Comunitat Valenciana",
    "murcia": "Murcia", "madrid": "Madrid",
    "avila": "Castilla y Leon", "burgos": "Castilla y Leon", "leon": "Castilla y Leon",
    "palencia": "Castilla y Leon", "salamanca": "Castilla y Leon", "segovia": "Castilla y Leon",
    "soria": "Castilla y Leon", "valladolid": "Castilla y Leon", "zamora": "Castilla y Leon",
    "albacete": "Castilla-La Mancha", "ciudad real": "Castilla-La Mancha", "cuenca": "Castilla-La Mancha",
    "guadalajara": "Castilla-La Mancha", "toledo": "Castilla-La Mancha",
    "badajoz": "Extremadura", "caceres": "Extremadura",
    "almeria": "Andalucia", "cadiz": "Andalucia", "cordoba": "Andalucia", "granada": "Andalucia",
    "huelva": "Andalucia", "jaen": "Andalucia", "malaga": "Andalucia", "sevilla": "Andalucia",
    "las palmas": "Canarias", "santa cruz de tenerife": "Canarias", "ceuta": "Ceuta", "melilla": "Melilla",
}
# RGSEAA "Provincia" spellings -> the same keys
ES_PROV_ALIAS = {"coruña, a": "a coruna", "a coruña": "a coruna", "coruña": "a coruna", "araba/alava": "araba",
                 "araba/álava": "araba", "balears, illes": "illes balears", "illes balears": "illes balears",
                 "palmas, las": "las palmas", "rioja, la": "la rioja", "castellón/castelló": "castellon",
                 "alicante/alacant": "alicante", "valencia/valència": "valencia", "gipuzkoa": "gipuzkoa",
                 "bizkaia": "bizkaia", "ourense": "ourense"}

# Hand cases: relation known from industry knowledge; numbers only where read from the
# company's own site or a register page (see note). "" = not obtained from a free source.
HAND = {
    "stock-s-r-l-distillerie-franciacorta-s-p-a": [
        ("it-registro-imprese", "", "Stock S.r.l.", "operator", "medium",
         "Stock Spirits Group site at Gussago (BS): Distillerie Franciacorta S.p.A. was bought by Stock in 2020; "
         "P.IVA not read from a register (Registro Imprese free search does not return it)", SRC_RI),
    ],
    "distillerie-franciacorta-s-p-a": [
        ("it-registro-imprese", "", "Stock S.r.l.", "operator", "medium",
         "Distillerie Franciacorta S.p.A. is part of Stock Spirits Group since 2020; number not obtained from a free register", SRC_RI),
    ],
    "distilleria-durbino-friulia-gruppo-caffo-1915": [
        ("it-registro-imprese", "", "Distilleria F.lli Caffo S.r.l.", "operator", "medium",
         "Durbino/Friulia site is run by Gruppo Caffo 1915 (Limbadi VV); number not obtained from a free register", SRC_RI),
    ],
    "distilleries-dyc-beam-spain-s-l": [
        ("es-rmc", "", "Beam Suntory Spain, S.L.", "operator", "medium",
         "DYC distillery at Palazuelos de Eresma (Segovia) is operated by Beam Suntory Spain, S.L. (Suntory Global Spirits); "
         "legal name as printed in the RGSEAA list (30.02306/SG); NIF not obtained from a free register", SRC_RMC),
    ],
    "destilerias-whisky-dyc": [
        ("es-rmc", "", "Beam Suntory Spain, S.L.", "operator", "medium",
         "same DYC site as above (Suntory Global Spirits); NIF not obtained from a free register", SRC_RMC),
    ],
    "experiencia-43": [
        ("es-rmc", "", "Diego Zamora, S.A.", "operator", "medium",
         "Licor 43 visitor centre, Cartagena; brand owner Zamora Company; NIF not obtained from a free register", SRC_RMC),
    ],
    "anis-del-mono-factory": [
        ("es-rmc", "", "Bodegas Osborne, S.A.U.", "operator", "medium",
         "Anis del Mono, Badalona, is an Osborne group brand and plant; NIF not obtained from a free register", SRC_RMC),
    ],
    "emperador-distillers-spain": [
        ("es-rmc", "", "Grupo Emperador Spain, S.A.", "operator", "medium",
         "Emperador Inc. (Philippines) group; Spanish arm holds Bodegas Fundador; NIF not obtained from a free register", SRC_RMC),
    ],
}
# Pages to try after the home page when no number is found there (path suffixes)
IT_EXTRA = ["/privacy-policy", "/contatti"]
ES_EXTRA = ["/aviso-legal", "/contacto"]
LEGAL_LINK_RE = re.compile(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', re.S | re.I)
LEGAL_WORDS = re.compile(r"privacy|aviso[- ]legal|note[- ]legali|legal|contatt|contact|impressum|cookie|termini|condiciones|"
                         r"chi[- ]siamo|quienes[- ]somos|azienda|empresa", re.I)
AGENCY_RE = re.compile(r"(realizzato|sviluppato|progettato|web ?agency|designed by|developed by|powered by|"
                       r"credits|dise[ñn]ado por|desarrollado por|creado por|web by|site by)", re.I)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def toks(s: str, keep_generic: bool = False) -> frozenset:
    stop = SUFFIX if keep_generic else STOP
    return frozenset(t for t in norm(s).split() if t not in stop and len(t) > 1)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def has_signal(name: str) -> bool:
    return bool(toks(name, keep_generic=True) & SIGNAL)


def relation_for(pin_toks: frozenset, legal_name: str) -> str:
    return "self" if pin_toks & toks(legal_name) else "operator"


# ---------------------------------------------------------------- pins ----
def it_prov(addr: str) -> str:
    m = re.search(r"\b\d{5}\s+[^,]+?\s+([A-Z]{2}),\s*Italy", addr or "")
    return m.group(1) if m else ""


def it_city(addr: str) -> str:
    m = re.search(r"\b\d{5}\s+(.+?)\s+[A-Z]{2},\s*Italy", addr or "")
    return norm(m.group(1)).strip() if m else ""


def es_prov(addr: str) -> str:
    m = re.search(r",\s*([^,]+?),\s*Spain", addr or "")
    if not m:
        return ""
    p = norm(m.group(1)).strip()
    return ES_PROV_ALIAS.get(p, p)


def es_city(addr: str) -> str:
    m = re.search(r"\b\d{5}\s+([^,]+?),\s*[^,]+,\s*Spain", addr or "")
    return norm(m.group(1)).strip() if m else ""


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        c = p.get("country")
        if c not in ("Italy", "Spain"):
            continue
        addr = p.get("address") or ""
        if c == "Italy":
            prov = it_prov(addr)
            region = IT_REGION.get(prov, "")
            city = it_city(addr)
        else:
            prov = es_prov(addr)
            region = ES_CCAA.get(prov, "")
            city = es_city(addr)
        site = (p.get("website") or "").strip()
        if site and not re.match(r"https?://", site):
            site = "https://" + site
        pins.append({"slug": p["slug"], "name": p["name"], "country": c, "prov": prov, "region": region,
                     "city": city, "site": site, "toks": toks(p["name"]),
                     "full": toks(p["name"], keep_generic=True)})
    return pins


# ------------------------------------------------------------ checksums ----
def valid_piva(n: str) -> bool:
    """Italian partita IVA / numeric codice fiscale, 11 digits, Luhn-style check digit."""
    if not re.fullmatch(r"\d{11}", n) or n == "00000000000":
        return False
    s = 0
    for i, ch in enumerate(n[:10]):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        s += d
    return (10 - s % 10) % 10 == int(n[10])


def valid_cif(n: str) -> bool:
    """Spanish CIF (legal persons): letter + 7 digits + control digit/letter."""
    m = re.fullmatch(r"([ABCDEFGHJNPQRSUVW])(\d{7})([0-9A-J])", n)
    if not m:
        return False
    letter, digits, ctrl = m.groups()
    s = 0
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            d = d // 10 + d % 10
        s += d
    c = (10 - s % 10) % 10
    exp_digit, exp_letter = str(c), "JABCDEFGHI"[c]
    if letter in "PQRSNW":
        return ctrl == exp_letter
    if letter in "ABEH":
        return ctrl == exp_digit
    return ctrl in (exp_digit, exp_letter)


def valid_nif_person(n: str) -> bool:
    m = re.fullmatch(r"(\d{8})([A-Z])", n)
    if not m:
        return False
    return "TRWAGMYFPDXBNJZSQVHLCKE"[int(m.group(1)) % 23] == m.group(2)


# ---------------------------------------------------------------- fetch ----
class Fetcher:
    def __init__(self, cache: Path, allow: bool):
        self.dir = cache / "websites"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.log_path = cache / "websites-log.json"
        self.log = json.loads(self.log_path.read_text()) if self.log_path.exists() else {}
        self.allow = allow
        self.requests = 0
        self.ctx = ssl.create_default_context()  # TLS verified; sites with broken chains are logged as errors

    def key(self, url: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", url.lower())[:150]

    def get(self, url: str) -> str | None:
        """Cached page text (HTML) or None. Fetches only when allowed and under the cap."""
        k = self.key(url)
        path = self.dir / (k + ".html")
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")
        if k in self.log and self.log[k].get("status") not in (None, "timeout", "error", "tls"):
            return None  # known failure (404, 403 ...), do not retry
        if not self.allow or self.requests >= FETCH_CAP:
            return None
        self.requests += 1
        time.sleep(FETCH_DELAY)
        entry = {"url": url, "when": time.strftime("%Y-%m-%d")}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "it,es,en"})
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT, context=self.ctx) as resp:
                raw = resp.read(2_000_000)
                ct = resp.headers.get("Content-Type", "")
                charset = re.search(r"charset=([\w-]+)", ct)
                enc = charset.group(1) if charset else None
                if not enc:
                    m = re.search(rb'charset=["\']?([\w-]+)', raw[:4000])
                    enc = m.group(1).decode() if m else "utf-8"
                try:
                    text = raw.decode(enc, errors="ignore")
                except LookupError:
                    text = raw.decode("utf-8", errors="ignore")
                entry["status"] = resp.status
                entry["final"] = resp.geturl()
                path.write_text(text, encoding="utf-8")
                self.log[k] = entry
                self._save()
                return text
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
        except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError, ConnectionError, OSError) as e:
            entry["status"] = "timeout" if "timed out" in str(e) else ("tls" if "SSL" in str(e) or "certificate" in str(e).lower() else "error")
            entry["error"] = str(e)[:120]
        except Exception as e:  # noqa: BLE001
            entry["status"] = "error"
            entry["error"] = str(e)[:120]
        self.log[k] = entry
        self._save()
        return None

    def _save(self):
        self.log_path.write_text(json.dumps(self.log, indent=0, ensure_ascii=False))


def visible_text(page: str) -> str:
    t = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</(p|div|li|td|tr|h\d|footer|section|span|a)>", " | ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t)
    return re.sub(r"[ \t\r\n\xa0]+", " ", t)


# ------------------------------------------------------- number extraction ----
IT_NUM_RE = re.compile(r"(?:P\.?\s*I\.?\s*V\.?\s*A\.?|Partita\s+IVA|Partita\s+I\.V\.A\.?|C\.?\s*F\.?|Cod(?:ice)?\.?\s*Fisc(?:ale)?\.?|"
                       r"VAT(?:\s*(?:no|number|nr|n))?\.?|Registro\s+(?:delle\s+)?Imprese|R\.?E\.?A\.?|MwSt\.?|UID|USt-?IdNr\.?|"
                       r"Steuernummer|IVA)[^0-9A-Za-z]{0,12}(?:IT\s?)?(\d{11})\b", re.I)
IT_BARE_RE = re.compile(r"\bIT\s?(\d{11})\b")
ES_NUM_RE = re.compile(r"(?:C\.?\s*I\.?\s*F\.?|N\.?\s*I\.?\s*F\.?|VAT|Identificaci[oó]n\s+fiscal|NIF/CIF|CIF/NIF)"
                       r"[^0-9A-Za-z]{0,12}(?:ES\s?)?([ABCDEFGHJNPQRSUVW]\s?-?\s?\d{7}\s?-?\s?[0-9A-J]|\d{8}\s?-?\s?[A-Z])\b", re.I)
ES_BARE_RE = re.compile(r"\b(?:ES)?\s?([ABCDEFGHJNPQRSUVW][-\s]?\d{7}[-\s]?[0-9A-J])\b")
IT_LEGAL_RE = re.compile(r"((?-i:[A-ZÀ-Ü0-9])[^|•©®]{1,90}?\b(?:S\.?\s?r\.?\s?l\.?(?:\s?s\.?)?|S\.?\s?p\.?\s?A\.?|S\.?\s?n\.?\s?c\.?|S\.?\s?a\.?\s?s\.?|"
                         r"S\.?\s?S\.?|Soc(?:iet[àa])?\.?\s+Agr(?:icola)?\.?(?:\s+[A-Za-zÀ-ü'\s]{0,40}?)?|Societ[àa]\s+Cooperativa|S\.?\s?C\.?\s?a\.?\s?r\.?\s?l\.?|"
                         r"Soc\.?\s?Coop\.?(?:\s?a\.?\s?r\.?\s?l\.?)?|GmbH|OHG|KG|Azienda\s+Agricola\s+[A-Za-zÀ-ü'\s]{2,40}?)(?=[\s|,.;:•©®(-]|$))", re.S | re.I)
ES_LEGAL_RE = re.compile(r"((?-i:[A-ZÀ-Ü0-9])[^|•©®]{1,90}?\b(?:S\.?\s?L\.?(?:\s?U\.?|\s?L\.?|\s?P\.?)?|S\.?\s?A\.?(?:\s?U\.?)?|S\.?\s?C\.?(?:oop\.?)?(?:\s?Ltda\.?)?|"
                         r"S\.?\s?Coop\.?|Sociedad\s+Limitada|Sociedad\s+An[oó]nima|C\.?\s?B\.?|S\.?\s?A\.?\s?T\.?)(?=[\s|,.;:•©®(-]|$))", re.S | re.I)


def clean_legal(s: str) -> str:
    s = re.sub(r"^\W+|\s+$", "", s)
    s = re.sub(r"^(?:©|copyright|\(c\)|\d{4}(?:\s*[-–]\s*\d{4})?|tutti i diritti riservati|todos los derechos reservados|"
               r"all rights reserved|sede legale|ragione sociale|raz[oó]n social|denominazione|titolare|titular|"
               r"propriet[aà]|empresa|azienda|societ[àa]|di|by|realizzato da)\b\s*[:.]?\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -–:,.|")
    return s


def extract_numbers(country: str, text: str):
    """[(number, context, agency_flag)] with checksum-valid numbers only."""
    out = []
    if country == "Italy":
        pats = [IT_NUM_RE, IT_BARE_RE]
        valid = valid_piva
        fix = lambda n: re.sub(r"\D", "", n)  # noqa: E731
    else:
        pats = [ES_NUM_RE, ES_BARE_RE]
        valid = lambda n: valid_cif(n) or valid_nif_person(n)  # noqa: E731
        fix = lambda n: re.sub(r"[\s-]", "", n).upper()  # noqa: E731
    seen = set()
    for pat in pats:
        for m in pat.finditer(text):
            n = fix(m.group(1))
            if not valid(n) or n in seen:
                continue
            ctx = text[max(0, m.start() - 260): m.end() + 120]
            agency = bool(AGENCY_RE.search(text[max(0, m.start() - 90): m.end() + 40]))
            seen.add(n)
            out.append((n, ctx, agency))
    return out


def extract_legal(country: str, ctx: str) -> str:
    pat = IT_LEGAL_RE if country == "Italy" else ES_LEGAL_RE
    best = ""
    for m in pat.finditer(ctx):
        cand = clean_legal(m.group(1))
        # A legal name starts with a letter, not a postcode or a sentence fragment ("es una
        # sociedad limitada", "I-39057 Appiano s. S"): the case-insensitive suffix match needs this.
        if not re.match(r"[A-Za-zÀ-ü]", cand) or re.search(r"\b(?:es una|è una|is a|titular|adelante)\b|[()]", cand, re.I) \
                or re.match(r"^[A-Z]-?\d{4,5}\b", cand):
            continue
        if 4 <= len(cand) <= 90 and not re.search(r"\b(privacy|cookie|policy|informativa|aviso legal|all rights|diritti|derechos|"
                                                  r"iscriviti|newsletter|seguici|síguenos|tel|fax|email|mail)\b", cand, re.I):
            # prefer the candidate closest to the number = shortest tail
            if not best or len(cand) < len(best):
                best = cand
    return best


# ------------------------------------------------------------ website match ----
def legal_links(base: str, page: str, country: str) -> list:
    """Same-host links from the home page that look like privacy / legal / contact pages
    (up to 2), else two guessed paths."""
    host = urllib.parse.urlsplit(base).netloc.lower().removeprefix("www.")
    out = []
    for href, label in LEGAL_LINK_RE.findall(page):
        text = re.sub(r"<[^>]+>", " ", label)
        if not (LEGAL_WORDS.search(text) or LEGAL_WORDS.search(href)):
            continue
        u = urllib.parse.urljoin(base + "/", htmlmod.unescape(href.strip()))
        sp = urllib.parse.urlsplit(u)
        if sp.scheme not in ("http", "https") or sp.netloc.lower().removeprefix("www.") != host:
            continue
        if re.search(r"\.(pdf|jpg|png|zip|docx?)$", sp.path, re.I):
            continue
        u = urllib.parse.urlunsplit((sp.scheme, sp.netloc, sp.path, sp.query, ""))
        if u.rstrip("/") != base and u not in out:
            out.append(u)
        if len(out) >= 2:
            break
    if not out:
        out = [base + x for x in (IT_EXTRA if country == "Italy" else ES_EXTRA)]
    return out


def match_websites(pins, fetcher: Fetcher):
    rows, log = [], {}
    for p in pins:
        if not p["site"]:
            log[p["slug"]] = "no website on the pin"
            continue
        base = p["site"].rstrip("/")
        urls = [base]
        found, page_used = [], ""
        first_status = None
        i = 0
        while i < len(urls) and i < 3:  # home page + at most two legal/contact pages
            u = urls[i]
            i += 1
            page = fetcher.get(u)
            if page is None:
                if u == base:
                    first_status = fetcher.log.get(fetcher.key(u), {}).get("status")
                    if first_status in (None, "timeout", "error", "tls") or isinstance(first_status, int) and first_status >= 400:
                        break  # home page unreachable: do not try sub-pages
                continue
            if u == base:
                urls += legal_links(base, page, p["country"])
            text = visible_text(page)
            found = extract_numbers(p["country"], text)
            # drop web-agency numbers if a non-agency one exists
            own = [f for f in found if not f[2]]
            found = own or found
            if found:
                page_used = u
                break
        if not found:
            if first_status in (None, "timeout", "error", "tls"):
                log[p["slug"]] = f"site unreachable ({first_status or 'not fetched'})"
            elif isinstance(first_status, int) and first_status >= 400:
                log[p["slug"]] = f"site returned HTTP {first_status}"
            else:
                log[p["slug"]] = "no VAT/tax number on home or legal pages"
            continue
        country = p["country"]
        registry = "it-registro-imprese" if country == "Italy" else "es-rmc"
        src_reg = SRC_RI if country == "Italy" else SRC_RMC
        for n, ctx, agency in found[:2]:
            legal = extract_legal(country, ctx)
            lt = toks(legal) if legal else frozenset()
            j = jaccard(p["toks"], lt) if legal else 0.0
            subset = bool(p["toks"]) and p["toks"] <= lt
            if legal and (p["toks"] & lt):
                agency = False  # the distillery's own legal name sits next to the number
            near = toks(ctx[max(0, len(ctx) - 380):])  # the ~260 chars before the number + the number line
            own_name_near = len(p["toks"] & near) >= max(1, min(2, len(p["toks"])))
            if agency:
                conf, why = "low", "number sits next to a web-agency credit; may be the agency's, not the distillery's"
            elif legal and (j >= 0.5 or subset):
                conf, why = "high", f"legal name on the site matches the pin (jaccard {j:.2f})"
            elif legal and has_signal(legal):
                conf, why = "medium", f"legal name on the site is a drinks company but differs from the pin name (jaccard {j:.2f})"
            elif legal:
                conf, why = "medium", f"legal name on the site differs from the pin name (jaccard {j:.2f}); may be the operator"
            elif own_name_near:
                conf, why = "high", "no legal form printed, but the distillery's own name sits next to the number (sole trader or plain trading name); company name = pin name"
            else:
                conf, why = "medium", "number found but no legal name printed next to it; company name = pin name"
            if len(found) > 1 and not agency:
                conf = "medium" if conf == "high" else "low"
                why += f"; {len(found)} distinct numbers on the page"
            label = "P.IVA/codice fiscale" if country == "Italy" else "NIF"
            note = (f"{label} {n} read from the distillery's own website ({page_used}); {why}; "
                    f"checksum valid; not yet checked against the register ({'AdE VerificaPIVA by hand' if country == 'Italy' else 'RMC/BORME by hand'})")
            rel = relation_for(p["toks"], legal) if legal else "self"
            rows.append([p["slug"], p["name"], country, registry, n, legal or p["name"], rel,
                         "own-website-vat", conf, "", page_used, note])
        log[p["slug"]] = "matched"
    return rows, log


# ------------------------------------------------------------------ RGSEAA ----
def load_rgseaa(cache: Path):
    path = cache / "rgseaa-industrias.csv"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("Clave") == "30"]
    print(f"rgseaa: {len(rows)} key-30 (bebidas alcoholicas) rows", file=sys.stderr)
    return rows


def match_rgseaa(pins, rg):
    lic = []
    index = defaultdict(list)
    for i, r in enumerate(rg):
        for t in toks(r["Razon_Social"]):
            index[t].append(i)
    for p in pins:
        if p["country"] != "Spain" or not p["toks"]:
            continue
        cand = set()
        for t in p["toks"]:
            post = index.get(t, [])
            if 0 < len(post) <= 400:
                cand.update(post)
        best = {}
        for i in cand:
            r = rg[i]
            ct = toks(r["Razon_Social"])
            j = jaccard(p["toks"], ct)
            prov = ES_PROV_ALIAS.get(norm(r["Provincia"]).strip(), norm(r["Provincia"]).strip())
            prov_ok = bool(p["prov"]) and prov == p["prov"]
            prov_conflict = bool(p["prov"]) and prov != p["prov"]
            subset = len(p["toks"]) >= 2 and p["toks"] <= ct
            if j >= 0.8 or subset:
                g = "high" if (prov_ok or not p["prov"]) else "medium"
            elif j >= 0.6:
                g = "medium" if prov_ok else "low"
            elif j >= 0.4 and prov_ok:
                g = "low"
            else:
                continue
            if prov_conflict and j < 0.8 and not subset:
                continue
            if len(p["toks"]) <= 1 and toks(p["name"], True) != toks(r["Razon_Social"], True):
                # one distinctive token only (e.g. "mallorca"): never high unless the full names agree
                g = {"high": "medium", "medium": "low", "low": "low"}[g] if prov_ok else "low"
                if not has_signal(r["Razon_Social"]) and not prov_ok:
                    continue
            score = j + (0.3 if prov_ok else 0) - (0.3 if prov_conflict else 0)
            k = r["N_RGSEAA"]
            if k not in best or best[k][0] < score:
                best[k] = (score, g, r, j, prov_ok)
        for score, g, r, j, prov_ok in sorted(best.values(), key=lambda x: -x[0])[:2]:
            note = (f"name jaccard {j:.2f}; RGSEAA key 30 bebidas alcoholicas; establishment {r['Domicilio_industrial']}, "
                    f"{r['Provincia']} ({r['CCAA']}){' (province agrees)' if prov_ok else ''}; list dated 1 Sep 2026; no NIF in the list")
            lic.append([p["slug"], p["name"], "Spain", "es-rgseaa", r["N_RGSEAA"], r["Razon_Social"],
                        relation_for(p["toks"], r["Razon_Social"]), "rgseaa-bulk-name", g, "", SRC_RGSEAA, note])
    return lic


# -------------------------------------------------------------------- main ----
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory holding rgseaa-industrias.csv and the website cache")
    ap.add_argument("--fetch-websites", action="store_true",
                    help="allow fetching the pins' own websites (1 req/s, cap %d, cached)" % FETCH_CAP)
    args = ap.parse_args()
    cache = Path(args.cache).expanduser()
    cache.mkdir(parents=True, exist_ok=True)

    pins = load_pins()
    print(f"{sum(p['country'] == 'Italy' for p in pins)} Italian pins, {sum(p['country'] == 'Spain' for p in pins)} Spanish pins",
          file=sys.stderr)

    fetcher = Fetcher(cache, args.fetch_websites)
    web_rows, web_log = match_websites(pins, fetcher)
    print(f"websites: {fetcher.requests} requests this run (cap {FETCH_CAP}), {len(fetcher.log)} URLs in log", file=sys.stderr)
    lic = match_rgseaa(pins, load_rgseaa(cache))

    hand = []
    for slug, rows in HAND.items():
        p = next((x for x in pins if x["slug"] == slug), None)
        if not p:
            continue
        for reg, num, name, rel, conf, note, src in rows:
            hand.append([slug, p["name"], p["country"], reg, num, name, rel, "hand", conf, "", src, note])

    conf_rank = {"high": 0, "medium": 1, "low": 2}
    hand_keys = {(r[0], r[3], r[4]) for r in hand}
    machine = {}
    for r in web_rows:
        if (r[0], r[3], r[4]) in hand_keys:
            continue
        k = (r[0], r[3], r[4])
        if k not in machine or conf_rank[r[8]] < conf_rank[machine[k][8]]:
            machine[k] = r
    final = hand + list(machine.values())
    order = {s["slug"]: i for i, s in enumerate(pins)}
    final.sort(key=lambda r: (order[r[0]], r[3], conf_rank[r[8]], r[5]))
    lic.sort(key=lambda r: (order[r[0]], r[3], conf_rank[r[8]]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, rows in ((OUT_CANDIDATES, final), (OUT_LICENCES, lic)):
        with path.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            w.writerows(rows)

    best = {}
    for r in final:
        best[r[0]] = min(best.get(r[0], 9), conf_rank[r[8]])
    by_reg = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    for p in pins:
        d = by_reg[(p["country"], p["region"] or "(no address)")]
        d["pins"] += 1
        if p["slug"] in best:
            d[["high", "medium", "low"][best[p["slug"]]]] += 1
        else:
            d["unmatched"] += 1
    print("country region                 pins high medium low unmatched")
    for key in sorted(by_reg, key=lambda k: (k[0], -by_reg[k]["pins"])):
        d = by_reg[key]
        print(f"{key[0]:7} {key[1]:22} {d['pins']:4} {d['high']:4} {d['medium']:6} {d['low']:3} {d['unmatched']:9}")
    tot = {k: sum(d[k] for d in by_reg.values()) for k in ("pins", "high", "medium", "low", "unmatched")}
    print(f"total                          {tot['pins']:4} {tot['high']:4} {tot['medium']:6} {tot['low']:3} {tot['unmatched']:9}")
    reasons = defaultdict(list)
    for p in pins:
        if p["slug"] not in best:
            reasons[web_log.get(p["slug"], "no row")].append(p["slug"])
    for why, slugs in sorted(reasons.items(), key=lambda x: -len(x[1])):
        print(f"unmatched ({len(slugs)}): {why}: {' '.join(slugs)}")
    lic_slugs = {r[0] for r in lic}
    print(f"rgseaa licence rows cover {len(lic_slugs)} Spanish pins")
    print(f"{len(final)} candidate rows -> {OUT_CANDIDATES.relative_to(ROOT)}; {len(lic)} licence rows -> {OUT_LICENCES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
