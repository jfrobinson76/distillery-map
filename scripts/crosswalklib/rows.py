"""The crosswalk row: one schema, one validator."""
from __future__ import annotations

import csv
import re
from pathlib import Path

FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]
RELATIONS = {"self", "operator", "group"}
CONFIDENCES = {"high", "medium", "low"}

# What a register number looks like, where the register has a fixed shape. A registry not
# listed here is accepted as-is.
NUMBER_SHAPES = {
    "companies-house": r"^[A-Z0-9]{8}$",
    "cro": r"^\d{1,7}$",
    "ttb-basic-permit": r"^[A-Z]{2}-[A-Z]-\d+$",
    "corporations-canada": r"^\d{1,8}$",
    "qc-req": r"^\d{10}$",
    "bc-orgbook": r"^[A-Z]{1,2}\d{7}$",
    "fr-sirene": r"^\d{9}$",
    "au-abr": r"^\d{11}$",
    "au-asic": r"^\d{9}$",
    "jp-houjin-bangou": r"^\d{13}$",
    "in-mca": r"^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$",
    "za-cipc": r"^\d{4}/\d{6}/\d{2}$",
    "ch-zefix": r"^CHE-\d{3}\.\d{3}\.\d{3}$",
    "it-registro-imprese": r"^\d{11}$",
    "es-rmc": r"^[A-Z]\d{7}[0-9A-J]$|^\d{8}[A-Z]$",
}


def make(slug: str, distillery_name: str, country: str, registry: str, company_number: str,
         company_name: str, relation: str, match_method: str, confidence: str, source: str,
         note: str) -> dict:
    return {"slug": slug, "distillery_name": distillery_name, "country": country, "registry": registry,
            "company_number": (company_number or "").strip(), "company_name": (company_name or "").strip(),
            "relation": relation, "match_method": match_method, "confidence": confidence, "verified": "",
            "source": source, "note": note}


def validate(rows: list[dict], known_slugs: set[str] | None = None) -> list[str]:
    """Problems as strings; empty means clean. Matchers refuse to write on a non-empty list."""
    problems = []
    for i, r in enumerate(rows):
        where = f"row {i} {r.get('slug', '?')}"
        if list(r.keys()) != FIELDS:
            problems.append(f"{where}: columns {list(r.keys())}")
            continue
        if r["relation"] not in RELATIONS:
            problems.append(f"{where}: relation {r['relation']!r}")
        if r["confidence"] not in CONFIDENCES:
            problems.append(f"{where}: confidence {r['confidence']!r}")
        if r["verified"]:
            problems.append(f"{where}: verified is set by a human, not a matcher")
        if r["company_number"] and r["registry"] in NUMBER_SHAPES \
                and not re.match(NUMBER_SHAPES[r["registry"]], r["company_number"]):
            problems.append(f"{where}: {r['registry']} number {r['company_number']!r} has the wrong shape")
        if not r["company_number"] and r["confidence"] != "low":
            problems.append(f"{where}: no number but confidence {r['confidence']}")
        if known_slugs is not None and r["slug"] not in known_slugs:
            problems.append(f"{where}: slug not on the map")
    return problems


def write(path: Path, rows: list[dict], known_slugs: set[str] | None = None) -> None:
    problems = validate(rows, known_slugs)
    if problems:
        raise SystemExit("refusing to write " + str(path) + ":\n  " + "\n  ".join(problems[:20]))
    rows = sorted(rows, key=lambda r: (r["country"], r["slug"], r["relation"], r["confidence"]))
    with Path(path).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def read(path: Path) -> list[dict]:
    p = Path(path)
    return list(csv.DictReader(p.open())) if p.exists() else []
