#!/usr/bin/env python3
"""Build the California reviewed ledger from reproducible official evidence.

This script merges three sources without modifying public GeoJSON:
1. the California pre-research candidate ledger;
2. the California ABC daily export downloaded on the review date; and
3. completed individual research records, where present and internally complete.

It applies deliberately conservative defaults.  An active federal or state licence is
not rendered as an assertion that a site is currently open.  Candidates with no
individual review and no exact-premise ABC match remain closed_or_unverifiable with
an operating status of unverifiable—not closed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "data/audit/california_ttb_pilot"
PRE = PILOT / "candidate_ledger_pre_research.csv"
ABC = PILOT / "source_cache/ABC-DailyDataExport.csv"
ABC_ZIP = PILOT / "source_cache/DailyExport-CSV.zip"
BATCH = Path("/home/ubuntu/research_california_ttb_candidates.json")
OUT = PILOT / "candidate_ledger_reviewed.csv"
ABC_MATCHES = PILOT / "abc_premise_matches.csv"
SOURCE_TTB_NAME = "TTB Spirits Producers and Bottlers List"
SOURCE_TTB_URL = "https://www.ttb.gov/public-information/foia/list-of-permittees"
SOURCE_ABC_NAME = "California ABC Daily Data Export"
SOURCE_ABC_URL = "https://www.abc.ca.gov/wp-content/uploads/DailyExport-CSV.zip"
ABC_REPORT_URL = "https://www.abc.ca.gov/licensing/licensing-reports/"
RETRIEVAL_DATE = "2026-08-22"
ALLOWED = {"production_site", "bottling_only", "brand_or_office", "duplicate_permit", "closed_or_unverifiable", "needs_review"}
STATUSES = {"open", "closed", "unknown", "unverifiable"}
STOP = {"a", "and", "at", "beverage", "beverages", "co", "company", "corp", "corporation", "distilling", "distillery", "inc", "incorporated", "limited", "llc", "lp", "ltd", "of", "spirits", "the", "wine", "winery"}


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()


def tokens(value: str) -> set[str]:
    return {item for item in norm(value).split() if item not in STOP and len(item) > 1}


def address_key(street: str, city: str, state: str, postcode: str) -> str:
    # Some ABC premise records carry ZIP+4 while TTB has 5 digits.
    return "|".join((norm(street), norm(city), norm(state), norm(postcode)[:5]))


def license_classification(types: set[str]) -> tuple[str, str]:
    # The state’s public licence descriptions are decisive about statutory function,
    # not a claim that the business is presently open to the public.
    if types & {"03", "04", "74"}:
        return "production_site", "Official California ABC export shows a matching active brandy/distilled-spirits/craft-distiller licence at the TTB premise."
    if types & {"05", "07", "08", "24"} and not types & {"03", "04", "06", "74"}:
        return "bottling_only", "Official California ABC export shows matching active manufacturer-agent/rectifier privileges but no matching active distilled-spirits production licence."
    if types & {"09", "10", "11", "12", "13", "17", "18", "19", "25", "26", "27", "28"} and not types & {"03", "04", "06", "74"}:
        return "brand_or_office", "Official California ABC export shows matching active importer, wholesaler, broker, or agency privileges rather than a production licence."
    return "needs_review", "Official California ABC export has an exact-premise identity match, but the listed licence type does not independently establish spirits production."


def read_pre() -> list[dict[str, str]]:
    with PRE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_abc() -> list[dict[str, str]]:
    # Keep the compressed official download as the reproducibility artefact and
    # re-create its untracked 27 MB CSV only when the pipeline needs it.
    if not ABC.exists():
        if not ABC_ZIP.exists():
            raise FileNotFoundError(f"Missing official ABC source archive: {ABC_ZIP}")
        with zipfile.ZipFile(ABC_ZIP) as archive:
            archive.extract("ABC-DailyDataExport.csv", path=ABC.parent)
    # The official data has a timestamp/banner line before the actual header.
    with ABC.open(newline="", encoding="utf-8-sig") as handle:
        next(handle)
        return list(csv.DictReader(handle))


def identity_match(candidate: dict[str, str], row: dict[str, str]) -> bool:
    left = tokens(candidate.get("business_name", "")) | tokens(candidate.get("dba", "")) | tokens(candidate.get("name", ""))
    right = tokens(row.get("Primary Name", "")) | tokens(row.get("DBA Name", ""))
    return bool(left & right)


def load_individual() -> dict[str, dict[str, str]]:
    if not BATCH.exists():
        return {}
    raw = json.loads(BATCH.read_text(encoding="utf-8"))
    retained: dict[str, dict[str, str]] = {}
    for record in raw.get("results", []):
        output = record.get("output") or {}
        if record.get("error") or not output:
            continue
        candidate_id = output.get("candidate_id", "").strip()
        classification = output.get("classification", "").strip()
        status = output.get("current_operating_status", "").strip()
        evidence = output.get("evidence_url", "").strip()
        source = output.get("source_url", "").strip()
        reference = output.get("exact_registry_reference", "").strip()
        if candidate_id and classification in ALLOWED and status in STATUSES and evidence.startswith("http") and source.startswith("http") and reference:
            retained[candidate_id] = {key: str(value or "").strip() for key, value in output.items()}
    return retained


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidates = read_pre()
    abc_rows = read_abc()
    individual = load_individual()

    # Only current issued licence records are relevant to a statutory-function match;
    # application/pending records are intentionally not proof of a production site.
    active_by_address: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in abc_rows:
        if row.get("Lic or App", "").strip() == "LIC" and row.get("Type Status", "").strip() == "ACTIVE":
            key = address_key(row.get("Prem Addr 1", ""), row.get("Prem City", ""), row.get(" Prem State", ""), row.get("Prem Zip", ""))
            active_by_address[key].append(row)

    match_rows: list[dict[str, str]] = []
    reviewed: list[dict[str, str]] = []
    fields = list(candidates[0].keys())
    for candidate in candidates:
        key = address_key(candidate["full_premise_address"].split(", ")[0] if candidate["full_premise_address"] else "", candidate["city"], candidate["state"], candidate["zip"])
        # Use structured premise address rather than display line for canonical match.
        street = candidate["full_premise_address"]
        prefix = f", {candidate['city']}, {candidate['state']}"
        if prefix in street:
            street = street.split(prefix, 1)[0]
        key = address_key(street, candidate["city"], candidate["state"], candidate["zip"])
        official_matches = [row for row in active_by_address.get(key, []) if identity_match(candidate, row)]
        types = {row.get("License Type", "").strip().zfill(2) for row in official_matches}
        abc_files = sorted({row.get("File Number", "").strip() for row in official_matches if row.get("File Number", "").strip()})
        abc_desc = "; ".join(f"Type {row.get('License Type', '').strip()} file {row.get('File Number', '').strip()} ({row.get('Primary Name', '').strip()} / {row.get('DBA Name', '').strip()})" for row in official_matches)
        for row in official_matches:
            match_rows.append({
                "candidate_id": candidate["candidate_id"], "candidate_name": candidate["name"], "candidate_address": candidate["full_premise_address"],
                "abc_license_type": row.get("License Type", "").strip(), "abc_file_number": row.get("File Number", "").strip(),
                "abc_primary_name": row.get("Primary Name", "").strip(), "abc_dba_name": row.get("DBA Name", "").strip(),
                "abc_premise_address": ", ".join(item.strip() for item in (row.get("Prem Addr 1", ""), row.get(" Prem Addr 2", ""), row.get("Prem City", ""), row.get(" Prem State", ""), row.get("Prem Zip", "")) if item.strip()),
                "abc_lic_or_app": row.get("Lic or App", "").strip(), "abc_type_status": row.get("Type Status", "").strip(),
                "retrieval_date": RETRIEVAL_DATE, "source_url": SOURCE_ABC_URL,
            })

        row = dict(candidate)
        individual_result = individual.get(candidate["candidate_id"])
        if individual_result:
            # Individual research can supply more-specific website/current-status evidence.
            for name in ("classification", "classification_reason", "current_operating_status", "operator_url", "evidence_url", "source_name", "source_url", "retrieval_date", "exact_registry_reference", "notes"):
                if individual_result.get(name):
                    row[name] = individual_result[name]
            if abc_desc:
                row["notes"] = (row.get("notes", "") + " Official ABC exact-premise match: " + abc_desc + ".").strip()
        elif official_matches:
            classification, reason = license_classification(types)
            row.update({
                "classification": classification,
                "classification_reason": reason,
                "current_operating_status": "unknown",
                "operator_url": "",
                "evidence_url": ABC_REPORT_URL,
                "source_name": SOURCE_ABC_NAME,
                "source_url": SOURCE_ABC_URL,
                "retrieval_date": RETRIEVAL_DATE,
                "exact_registry_reference": f"{candidate['exact_registry_reference']}; California ABC Daily Data Export: {', '.join(abc_files)} ({', '.join(sorted(types))})",
                "notes": f"Automated exact premise plus owner/DBA-token match in official ABC export: {abc_desc}.",
            })
        else:
            row.update({
                "classification": "closed_or_unverifiable",
                "classification_reason": "No operator, local-government, or exact-premise California ABC evidence was located in the completed review; the TTB listing verifies permit identity only.",
                "current_operating_status": "unverifiable",
                "operator_url": "",
                "evidence_url": SOURCE_TTB_URL,
                "source_name": SOURCE_TTB_NAME,
                "source_url": SOURCE_TTB_URL,
                "retrieval_date": RETRIEVAL_DATE,
                "exact_registry_reference": candidate["exact_registry_reference"],
                "notes": "Conservative default after no completed individual evidence and no exact-premise owner/DBA match in California ABC daily data; not a finding of closure.",
            })
        reviewed.append(row)

    write_csv(OUT, fields, reviewed)
    match_fields = ["candidate_id", "candidate_name", "candidate_address", "abc_license_type", "abc_file_number", "abc_primary_name", "abc_dba_name", "abc_premise_address", "abc_lic_or_app", "abc_type_status", "retrieval_date", "source_url"]
    write_csv(ABC_MATCHES, match_fields, match_rows)
    print(f"reviewed_rows={len(reviewed)}")
    print(f"individual_research_rows_used={sum(1 for row in reviewed if row['candidate_id'] in individual)}")
    print(f"official_abc_match_rows={len(match_rows)}")
    print("classification_counts=" + json.dumps(Counter(row["classification"] for row in reviewed), sort_keys=True))
    print("status_counts=" + json.dumps(Counter(row["current_operating_status"] for row in reviewed), sort_keys=True))


if __name__ == "__main__":
    main()
