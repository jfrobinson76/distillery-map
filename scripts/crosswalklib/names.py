"""Name normalisation shared by every matcher. Stdlib only."""
from __future__ import annotations

import re
import unicodedata

# Legal forms and function words, all countries. Dropping them everywhere is safe: none of
# them ever distinguishes one distillery from another.
SUFFIX = {
    # en
    "ltd", "limited", "inc", "incorporated", "corp", "corporation", "co", "company", "llc", "lp",
    "llp", "plc", "pty", "the", "and", "of", "a", "an", "dba", "trading", "as", "group", "holdings",
    # fr
    "sarl", "sas", "sa", "eurl", "scea", "earl", "gaec", "snc", "sca", "societe", "ste", "ltee",
    "limitee", "incorporee", "sencrl", "senc", "enr", "et", "de", "des", "du", "la", "le", "les",
    # de / at / ch
    "gmbh", "ag", "kg", "ohg", "ek", "eu", "ug", "kgaa", "eg", "mbh", "gesellschaft", "und", "der",
    "die", "das", "von", "vom", "zum", "zur", "am", "im", "in", "u", "mit", "bei", "fur", "inh",
    "inhaber", "sagl", "genossenschaft", "verein", "stiftung", "familie", "fam",
    # it / es
    "srl", "srls", "spa", "sas", "ss", "snc", "sc", "scarl", "coop", "societa", "agricola", "azienda",
    "sl", "slu", "sll", "slp", "sau", "sociedad", "limitada", "anonima", "cb", "sat", "y", "e", "el",
    "los", "las", "di", "del", "della", "dei", "degli",
    # ja (romaji)
    "kk", "kabushiki", "kaisha", "yugen", "godo",
    # in / za
    "pvt", "private", "proprietary",
}

# Words that say what the business does, in every language on the map. Dropped for matching
# (they carry no identity) but SIGNAL tells the grader the company is in drinks.
GENERIC = {
    "distillery", "distilleries", "distillers", "distilling", "distiller", "distill", "distillerie",
    "distillateur", "distillateurs", "microdistillerie", "microdistillery", "brennerei", "destillerie",
    "destille", "destillation", "distilleria", "distillerie", "destileria", "destilerias", "destilaria",
    "edelbrennerei", "obstbrennerei", "hofbrennerei", "schnapsbrennerei", "kornbrennerei",
    "weinbrennerei", "abfindungsbrennerei", "kleinbrennerei", "privatbrennerei", "hausbrennerei",
    "landbrennerei", "feinbrennerei", "schaubrennerei", "naturbrennerei", "spezialitatenbrennerei",
    "whisky", "whiskey", "whiskys", "bourbon", "rye", "gin", "vodka", "rum", "rhum", "brandy", "cognac",
    "armagnac", "calvados", "grappa", "schnaps", "korn", "absinthe", "absinth", "edelbrand", "edelbrande",
    "brand", "brande", "obstbrande", "weinbrand", "feinbrand", "geist", "eau", "eaux", "vie", "likor",
    "likore", "liqueur", "liqueurs", "liquori", "licores", "spirits", "spirit", "spirituosen",
    "spiritueux", "spiritus", "shuzo", "shochu", "sake", "craft", "artisan", "artisanal", "artisanale",
    "micro", "malt", "single", "cask", "barrel", "still", "stills", "brewing", "brewery", "brewers",
    "brauerei", "brasserie", "birra", "bier", "winery", "weingut", "weinkellerei", "kellerei",
    "vineyard", "vignoble", "domaine", "cidery", "cidrerie", "estate", "farm", "farms", "hof",
    "manufaktur", "genuss", "shop", "cafe", "restaurant", "hotel", "gasthof", "gasthaus", "bar",
    "tasting", "room", "cellar", "cellars", "house", "maison", "bodega", "bodegas", "chateau",
}
STOP = SUFFIX | GENERIC

# A company name with one of these is in the drinks trade; used by the grader as `signal`.
SIGNAL = {t for t in GENERIC if t not in {"craft", "artisan", "artisanal", "artisanale", "micro",
                                           "estate", "farm", "farms", "hof", "shop", "cafe",
                                           "restaurant", "hotel", "gasthof", "gasthaus", "bar",
                                           "room", "house", "maison", "chateau", "single", "still",
                                           "stills", "brand", "brande", "malt", "cellar", "cellars"}}


def fold(s: str) -> str:
    """Lowercase ASCII with accents stripped; punctuation to spaces."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def tokens(s: str, stop: set[str] | None = None) -> frozenset[str]:
    """Distinctive tokens: folded, minus SUFFIX and GENERIC (or a caller's stop set)."""
    st = STOP if stop is None else stop
    return frozenset(t for t in fold(s).split() if t not in st)


def norm(s: str, stop: set[str] | None = None) -> str:
    return " ".join(sorted(tokens(s, stop)))


def jaccard(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def exact(a: str, b: str) -> bool:
    """Same name once folded and suffix-stripped, generic words kept (so 'Yoichi Distillery'
    and 'Yoichi Beer' are not exact)."""
    return norm(a, SUFFIX) == norm(b, SUFFIX) and bool(tokens(a))


def has_signal(company_name: str) -> bool:
    return bool(set(fold(company_name).split()) & SIGNAL)


def distinctive(pin_name: str) -> bool:
    """A pin name that is more than a generic label or a single common word."""
    t = tokens(pin_name)
    return len(t) >= 2 or (len(t) == 1 and len(next(iter(t))) >= 6)
