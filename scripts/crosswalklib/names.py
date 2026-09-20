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
    "ulc",
    # ga (Ireland)
    "dac", "unlimited", "teoranta", "teo", "cuideachta",
    # fr
    "sarl", "sas", "sasu", "sa", "eurl", "scea", "earl", "gaec", "snc", "sci", "scop", "sca",
    "societe", "soc", "ste", "ets", "etablissement", "etablissements", "cie", "compagnie",
    "ltee", "limitee", "incorporee", "sencrl", "senc", "enr", "groupe", "holding", "fils",
    "freres", "frere", "pere", "et", "de", "des", "du", "d", "l", "la", "le", "les", "au", "aux",
    "en", "un", "une", "sur", "sous", "chez", "monsieur", "madame", "mr", "mme",
    # de / at / ch
    "gmbh", "ag", "kg", "ohg", "ek", "eu", "ug", "kgaa", "eg", "mbh", "gesellschaft", "und", "der",
    "die", "das", "von", "vom", "zum", "zur", "am", "im", "in", "u", "mit", "bei", "fur", "inh",
    "inhaber", "sagl", "genossenschaft", "verein", "stiftung", "familie", "fam",
    # de / at / ch additions (match_dach_registers.py, 20 Sep 2026)
    "cokg", "gbr", "haftungsbeschrankt", "ehem", "sohn", "sohne", "geb", "liq", "liquidation",
    "gen", "reg",
    # it / es
    "srl", "srls", "spa", "sas", "ss", "sr", "snc", "sc", "scarl", "scoop", "coop", "cooperativa",
    "soc", "societa", "agricola", "agr", "azienda", "sl", "slu", "sll", "slp", "sau", "sociedad",
    "limitada", "anonima", "cb", "sat", "y", "e", "el", "los", "las", "il", "lo", "gli", "i", "la",
    "le", "di", "del", "della", "delle", "dei", "degli", "da", "al", "en", "con", "per", "por", "fu",
    "f", "lli", "flli", "fratelli", "hermanos", "hnos", "figli", "hijos", "eredi", "ditta", "cav",
    "dott", "dr",
    # ja (romaji)
    "kk", "kabushiki", "kaisha", "yugen", "godo",
    # in / za
    "pvt", "private", "proprietary", "p", "cc", "npc", "m", "s", "ms", "unit", "units", "division",
    "head", "office", "corporate", "plant", "manufacturing", "india", "indian", "south", "africa",
    # en (additions for match_australia_registers.py, 20 Sep 2026)
    "trustee", "trust", "family", "nominees", "for", "australia", "australian", "aust",
    "zealand", "nz",
}

# Words that say what the business does, in every language on the map. Dropped for matching
# (they carry no identity) but SIGNAL tells the grader the company is in drinks.
GENERIC = {
    "distillery", "distilleries", "distillers", "distilling", "distiller", "distill", "distil", "distillerie",
    "distillateur", "distillateurs", "microdistillerie", "microdistillery", "brennerei", "destillerie",
    "destille", "destillation", "distilleria", "distillerie", "destileria", "destilerias", "destilaria",
    "distillerias", "distillatori", "distillati", "destiladora", "destilados", "destilacion",
    "edelbrennerei", "obstbrennerei", "hofbrennerei", "schnapsbrennerei", "kornbrennerei",
    "weinbrennerei", "abfindungsbrennerei", "kleinbrennerei", "privatbrennerei", "hausbrennerei",
    "landbrennerei", "feinbrennerei", "schaubrennerei", "naturbrennerei", "spezialitatenbrennerei",
    "brennereien",
    "whisky", "whiskey", "whiskys", "bourbon", "rye", "moonshine", "gin", "vodka", "rum", "rhum", "brandy",
    "cognac", "armagnac", "calvados", "grappa", "grappe", "acquavite", "acquaviti", "aguardientes",
    "aguardiente", "orujos", "orujo", "ron", "schnaps", "korn", "absinthe", "absinth", "edelbrand",
    "edelbrande", "brand", "brande", "obstbrande", "weinbrand", "feinbrand", "geist", "eau", "eaux", "vie",
    "likor", "likore", "liqueur", "liqueurs", "liquor", "liquori", "licores", "liquorificio",
    "liquoristeria", "licoreria", "alcool", "alcools", "alcoholes", "alcoles",
    "spirits", "spirit", "spirituosen", "spiritueux", "spiritus", "beverage", "beverages", "boissons",
    "shuzo", "shochu", "sake", "craft", "artisan", "artisanal", "artisanale", "artigianale",
    "artigianali", "artesanal", "artesanos", "artesana", "premium",
    "micro", "malt", "single", "cask", "barrel", "still", "stills", "brewing", "brewery", "breweries",
    "brewers", "brewhouse", "beer", "beers", "boutique",
    # ja (romaji additions for match_japan_registers.py, 20 Sep 2026)
    "shuzou", "syuzou", "jozo", "jyozo", "kura",
    "brauerei", "brasserie", "birra", "bier", "winery", "wineries", "wine", "weingut", "weinkellerei",
    "kellerei", "vin", "vins", "wines", "vino", "vini", "cantina", "cantine", "cider", "cidre", "meadery",
    "hydromel",
    "vineyard", "vignoble", "domaine", "cidery", "cidrerie", "estate", "farm", "farms", "hof",
    "aziende", "elaborados", "productos", "prodotti",
    "liquors", "blenders", "bottlers", "bottling",
    "manufaktur", "genuss", "shop", "cafe", "restaurant", "hotel", "gasthof", "gasthaus", "bar",
    "tasting", "tours", "venue", "backpackers", "pick", "up",
    "room", "cellar", "cellars", "house", "maison", "bodega", "bodegas", "chateau",
    "casa", "antica", "antico", "storica", "official", "sito", "web",
    # fr (additions for match_france_registers.py, 20 Sep 2026)
    "cave", "caves", "vignobles", "ferme", "famille", "bouilleur", "bouilleurs", "ambulant",
    "cru", "producteur", "producteurs", "exploitation", "agricole", "visite", "visites", "site",
    "production", "artisanales",
    # en (additions for match_australia_registers.py, 20 Sep 2026)
    "distillation", "distilled", "stillhouse", "drinks",
    # de additions (match_dach_registers.py, 20 Sep 2026)
    "whiskydestillerie", "whiskybrennerei", "likormanufaktur", "pension", "destillate", "destillat",
    "obst", "weinbau", "weinhaus", "kelterei", "mosterei", "hofladen", "brennhutte", "brennstube",
    "brennstuberl", "wirtshaus", "landgasthof", "weinstube", "edel", "brennhaus", "brennen",
    "genussmanufaktur", "bio", "winzer", "weine", "wein", "likoerfabrik", "likorfabrik",
    "spezialitaten", "verkauf", "gastronomie", "landhotel", "gaststatte", "kraeuter", "krauter",
    "qualitatsbrand", "edelbranntweinbrennerei", "branntweinbrennerei",
}
STOP = SUFFIX | GENERIC

# A company name with one of these is in the drinks trade; used by the grader as `signal`.
SIGNAL = {t for t in GENERIC if t not in {"craft", "artisan", "artisanal", "artisanale", "micro",
                                           "estate", "farm", "farms", "hof", "shop", "cafe",
                                           "restaurant", "hotel", "gasthof", "gasthaus", "bar",
                                           "room", "house", "maison", "chateau", "single", "still",
                                           "stills", "brand", "brande", "malt", "cellar", "cellars",
                                           "aziende", "casa", "antica", "antico", "storica", "official",
                                           "sito", "web", "premium", "prodotti", "productos",
                                           "elaborados", "brewhouse", "boutique", "tours", "venue",
                                           "backpackers", "pick", "up",
                                           "cave", "caves", "ferme", "famille", "site", "production",
                                           "exploitation", "visite", "visites", "artisanales",
                                           "agricole", "producteur", "producteurs", "cru",
                                           "ambulant",
                                           "pension", "obst", "weinbau", "weinhaus", "hofladen",
                                           "brennstuberl", "wirtshaus", "landgasthof", "weinstube",
                                           "edel", "genussmanufaktur", "bio", "winzer", "weine",
                                           "spezialitaten", "verkauf", "gastronomie", "landhotel",
                                           "gaststatte", "kraeuter", "krauter", "qualitatsbrand"}}


def fold(s: str) -> str:
    """Lowercase ASCII with accents stripped; punctuation to spaces."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def tokens(s: str, stop: set[str] | None = None) -> frozenset[str]:
    """Distinctive tokens: folded, minus SUFFIX and GENERIC (or a caller's stop set).

    A name made only of generic words (Château de Cognac, The Whisky Distillery) keeps them:
    when they are all there is, they are the identity."""
    st = STOP if stop is None else stop
    words = fold(s).split()
    t = frozenset(w for w in words if w not in st)
    return t if t else frozenset(w for w in words if w not in SUFFIX)


def generic_words(s: str) -> frozenset[str]:
    return frozenset(w for w in fold(s).split() if w in GENERIC)


def norm(s: str, stop: set[str] | None = None) -> str:
    return " ".join(sorted(tokens(s, stop)))


def jaccard(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def exact(a: str, b: str) -> bool:
    """Same distinctive tokens, and the generic words on one side are a subset of the other's.
    'Distillerie L'Officine' = 'L'OFFICINE' (exact); 'Yoichi Distillery' != 'Yoichi Beer'
    (distillery vs beer conflict)."""
    ta, tb = tokens(a), tokens(b)
    if not ta or ta != tb:
        return False
    ga, gb = generic_words(a), generic_words(b)
    return ga <= gb or gb <= ga


def has_signal(company_name: str) -> bool:
    return bool(set(fold(company_name).split()) & SIGNAL)


def distinctive(pin_name: str) -> bool:
    """A pin name that is more than a generic label or a single common word."""
    t = tokens(pin_name)
    return len(t) >= 2 or (len(t) == 1 and len(next(iter(t))) >= 6)
