#!/usr/bin/env python3
"""Prepare a provenance-rich California TTB candidate queue.

The script intentionally operates only on the unmatched TTB permit queue and writes
research artefacts under data/audit/california_ttb_pilot.  It never reads or writes
the public GeoJSON.  A duplicate group requires an exact normalised premise address
AND token overlap between an owner or DBA value; shared addresses alone are not a
basis for a merge.
"""

from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data/audit/us_1752_ttb_reconciliation/ttb_permits_not_matched_to_map.csv"
OUT = ROOT / "data/audit/california_ttb_pilot"
EXPECTED_CA_ROWS = 501
SOURCE_NAME = "TTB Spirits Producers and Bottlers List"
SOURCE_URL = "https://www.ttb.gov/public-information/foia/list-of-permittees"

# Generic legal and beverage words are excluded only for the overlap test.  The
# original values remain untouched in every output field.
STOP_TOKENS = {
    "a", "an", "and", "at", "beverage", "beverages", "co", "company", "corp",
    "corporation", "distilling", "distillery", "inc", "incorporated", "limited",
    "llc", "lp", "ltd", "of", "spirits", "the", "wine", "winery",
}


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()


def address_key(row: dict[str, str]) -> str:
    # This intentionally includes every structured premise component so that records
    # in different suites/cities/postcodes do not collapse.
    return "|".join(normalise(row.get(field, "")) for field in ("street", "city", "state", "zip"))


def identity_tokens(value: str) -> set[str]:
    return {token for token in normalise(value).split() if token not in STOP_TOKENS and len(token) > 1}


def row_identity_tokens(row: dict[str, str]) -> set[str]:
    return identity_tokens(row.get("business_name", "")) | identity_tokens(row.get("dba_name", ""))


def identity_overlap(left: dict[str, str], right: dict[str, str]) -> set[str]:
    # An overlap of owner OR DBA tokens is sufficient, as required; a shared street
    # with no such overlap is deliberately separate.
    return row_identity_tokens(left) & row_identity_tokens(right)


def connected_components(rows: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    """Link only records that share a normalised exact address and identity token."""
    parent = list(range(len(rows)))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: int, b: int) -> None:
        a_root, b_root = find(a), find(b)
        if a_root != b_root:
            parent[b_root] = a_root

    by_address: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_address[address_key(row)].append(index)

    for indexes in by_address.values():
        for position, left in enumerate(indexes):
            for right in indexes[position + 1 :]:
                if identity_overlap(rows[left], rows[right]):
                    union(left, right)

    groups: dict[int, list[dict[str, str]]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[find(index)].append(row)
    return list(groups.values())


def first_nonblank(rows: Iterable[dict[str, str]], field: str) -> str:
    return next((row.get(field, "").strip() for row in rows if row.get(field, "").strip()), "")


def joined_distinct(rows: Iterable[dict[str, str]], field: str) -> str:
    values = sorted({row.get(field, "").strip() for row in rows if row.get(field, "").strip()}, key=str.casefold)
    return " | ".join(values)


def candidate_id(group: list[dict[str, str]]) -> str:
    # Address plus sorted component owner/DBA identities makes the identifier stable
    # across source ordering while preserving distinct businesses at a shared premise.
    key = address_key(group[0]) + "||" + "||".join(
        sorted({normalise(row.get("business_name", "")) + "|" + normalise(row.get("dba_name", "")) for row in group})
    )
    return "ca-ttb-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def make_group_row(group: list[dict[str, str]]) -> dict[str, str]:
    ordered = sorted(group, key=lambda row: row.get("permit_number", ""))
    permits = [row.get("permit_number", "").strip() for row in ordered if row.get("permit_number", "").strip()]
    permit_numbers = "; ".join(permits)
    business_name = joined_distinct(ordered, "business_name")
    dba = joined_distinct(ordered, "dba_name")
    name = dba.split(" | ")[0] if dba else business_name.split(" | ")[0]
    street = first_nonblank(ordered, "street")
    city = first_nonblank(ordered, "city")
    state = first_nonblank(ordered, "state")
    postcode = first_nonblank(ordered, "zip")
    full_address = ", ".join(part for part in (street, city, state, postcode) if part)
    duplicate_note = (
        "Pre-research duplicate-permit group: same normalised premise address and owner/DBA token overlap; "
        "requires operating-role verification."
        if len(ordered) > 1
        else "Pre-research single-permit candidate; requires operating-role verification."
    )
    registry_reference = f"{SOURCE_NAME}: {permit_numbers}"
    return {
        "candidate_id": candidate_id(ordered),
        "name": name,
        "business_name": business_name,
        "dba": dba,
        "full_premise_address": full_address,
        "city": city,
        "state": state,
        "zip": postcode,
        "permit_numbers": permit_numbers,
        "permit_count": str(len(permits)),
        "classification": "needs_review",
        "classification_reason": duplicate_note,
        "current_operating_status": "unknown",
        "operator_url": "",
        "evidence_url": "",
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "retrieval_date": "2026-08-21",
        "exact_registry_reference": registry_reference,
        "notes": "Prepared from unmatched active TTB permit queue; no public GeoJSON change.",
    }


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with INPUT.open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    california_rows = [row for row in source_rows if row.get("state", "").strip().upper() == "CA"]
    groups = connected_components(california_rows)
    prepared = sorted((make_group_row(group) for group in groups), key=lambda row: row["candidate_id"])

    fields = [
        "candidate_id", "name", "business_name", "dba", "full_premise_address", "city", "state", "zip",
        "permit_numbers", "permit_count", "classification", "classification_reason", "current_operating_status",
        "operator_url", "evidence_url", "source_name", "source_url", "retrieval_date", "exact_registry_reference", "notes",
    ]
    write_csv(OUT / "candidate_ledger_pre_research.csv", fields, prepared)

    research_fields = [
        "candidate_id", "name", "business_name", "dba", "full_premise_address", "city", "state", "zip",
        "permit_numbers", "permit_count", "operator_query", "official_registry_query", "source_name", "source_url",
        "retrieval_date", "exact_registry_reference", "research_status",
    ]
    research_inputs = []
    for row in prepared:
        research_inputs.append({
            "candidate_id": row["candidate_id"], "name": row["name"], "business_name": row["business_name"], "dba": row["dba"],
            "full_premise_address": row["full_premise_address"], "city": row["city"], "state": row["state"], "zip": row["zip"],
            "permit_numbers": row["permit_numbers"], "permit_count": row["permit_count"],
            "operator_query": f'{row["name"]} {row["city"]} California',
            "official_registry_query": f'{row["name"]} {row["full_premise_address"]}',
            "source_name": SOURCE_NAME, "source_url": SOURCE_URL, "retrieval_date": "2026-08-21",
            "exact_registry_reference": row["exact_registry_reference"], "research_status": "unreviewed",
        })
    write_csv(OUT / "research_inputs.csv", research_fields, research_inputs)

    duplicate_groups = sum(1 for row in prepared if int(row["permit_count"]) > 1)
    duplicate_rows_collapsed = len(california_rows) - len(prepared)
    sha256 = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    summary_lines = [
        "metric\tvalue\tdefinition",
        f"input_file\t{INPUT.relative_to(ROOT)}\tSource unmatched TTB permit CSV",
        f"input_sha256\t{sha256}\tSHA-256 of the source unmatched permit CSV",
        f"california_permit_rows\t{len(california_rows)}\tRows where state equals CA",
        f"expected_california_permit_rows\t{EXPECTED_CA_ROWS}\tExpected from 21 August audit brief",
        f"input_count_variance\t{len(california_rows) - EXPECTED_CA_ROWS}\tActual California rows minus expected rows",
        f"candidate_groups\t{len(prepared)}\tGroups after exact-premise plus owner/DBA-token duplicate collapse",
        f"duplicate_permit_groups\t{duplicate_groups}\tCandidate groups containing more than one retained TTB permit",
        f"duplicate_rows_collapsed\t{duplicate_rows_collapsed}\tPermit rows reduced through duplicate grouping",
        f"duplicate_collapse_rate\t{duplicate_rows_collapsed / len(california_rows):.6f}\t(permit rows minus candidate groups) divided by California permit rows",
        "grouping_rule\texact normalized street+city+state+zip AND overlap in owner or DBA identity tokens\tShared addresses alone remain separate candidates",
        "public_geojson_modified\tfalse\tThis script does not read or write public/data/distilleries.geojson",
    ]
    (OUT / "preparation_summary.tsv").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
