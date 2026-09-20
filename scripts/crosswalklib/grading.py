"""
One grading table for every register match. A grade is a claim about the join, not about
the company: `high` means the crosswalk will treat this company as the entity behind the
pin; `medium` means it probably is but one signal is missing; `low` is a lead for a human.
Anything weaker is not written.

Location: "strong" = same postcode, street or city; "weak" = same state, province or
département; "none" = unknown; "conflict" = a known different city.
"""
from __future__ import annotations

from dataclasses import dataclass

ORDER = ["high", "medium", "low"]


@dataclass
class Evidence:
    jaccard: float
    exact: bool = False
    location: str = "none"       # strong | weak | none | conflict
    active: bool = True          # register status live
    distinctive: bool = True     # pin name is more than a generic label
    signal: bool = True          # company name says drinks


def grade(e: Evidence) -> str | None:
    g = _grade_ignoring_location(e)
    if e.location == "conflict":
        g = cap(g, "medium")
    if not e.distinctive:
        # A generic-label pin ('Distillerie', 'Craft Spirits') matches every company with the
        # same generic word. Only the location can carry it, and never to a join.
        if e.location == "strong":
            g = cap(g, "medium")
        elif e.location == "weak":
            g = cap(g, "low")
        else:
            g = None
    return g


def _grade_ignoring_location(e: Evidence) -> str | None:
    strong = e.location == "strong"
    weak = e.location == "weak"
    if e.exact or e.jaccard >= 0.8:
        if not e.active:
            return "medium"
        if strong or (weak and (e.distinctive or e.signal)) or (e.exact and e.distinctive and e.signal):
            return "high"
        return "medium"
    if e.jaccard >= 0.6:
        if strong:
            return "medium"
        return "low" if (weak and e.signal) else None
    if e.jaccard >= 0.4 and strong and e.signal:
        return "low"
    return None


def cap(g: str | None, level: str) -> str | None:
    """Never better than `level`."""
    if g is None:
        return None
    return ORDER[max(ORDER.index(g), ORDER.index(level))]


def relation_for(pin_tokens: frozenset, company_tokens: frozenset) -> str:
    """self when the legal name shares a distinctive token with the pin, else operator."""
    return "self" if pin_tokens & company_tokens else "operator"


def apply_guards(rows: list[dict], hand_rows: list[dict] | None = None) -> list[dict]:
    """Rules that no matcher may skip, applied to the finished candidate list in place.

    1. A premises or postcode match claimed as `self` when the names do not overlap is a
       lead (`low`), not a join: liquor shops, clinics and unions share postcodes with
       distilleries. The same match claimed as `operator` keeps its grade; that is what a
       holding company at the distillery's address looks like.
    2. Where a hand row names the operator or group of a site, machine `self` rows for that
       site are town-name collisions and become leads.
    3. A row with no register number is never better than `low`.
    Rows are annotated so the reason is visible in `note`.
    """
    hand = hand_rows if hand_rows is not None else [r for r in rows if r.get("match_method") == "hand"]
    operated = {r["slug"] for r in hand if r.get("relation") in ("operator", "group")}
    for r in rows:
        m = r.get("match_method", "")
        if r.get("confidence") == "low":
            continue
        if not r.get("company_number"):
            r["confidence"] = "low"
            r["note"] = "no register number read; " + r.get("note", "")
        elif ("postcode" in m or "premises" in m) and r.get("relation") == "self" \
                and _name_overlap(r) < 0.3:
            r["confidence"] = "low"
            r["note"] = "shared premises only, names do not overlap; " + r.get("note", "")
        elif r["slug"] in operated and m != "hand" and r.get("relation") == "self":
            r["confidence"] = "low"
            r["note"] = "site is group-run per the hand row; name match is a lead; " + r.get("note", "")
    return rows


def _name_overlap(r: dict) -> float:
    from . import names
    return names.jaccard(names.tokens(r.get("distillery_name", "")), names.tokens(r.get("company_name", "")))


def best_per_key(rows: list[dict]) -> list[dict]:
    """One row per (slug, registry, relation): high before medium before low, then file order."""
    best: dict[tuple, dict] = {}
    for r in rows:
        k = (r["slug"], r["registry"], r["relation"])
        if k not in best or ORDER.index(r["confidence"]) < ORDER.index(best[k]["confidence"]):
            best[k] = r
    return list(best.values())
