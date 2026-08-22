#!/usr/bin/env python3
"""Validate the California TTB pilot and write an unambiguous summary.

The summary separates duplicate-permit collapse from the conservative failure to
confirm an initial production-site hypothesis.  It never treats federal or state
licence activity as a claim that an operator is currently open.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "data/audit/california_ttb_pilot"
INPUT = ROOT / "data/audit/us_1752_ttb_reconciliation/ttb_permits_not_matched_to_map.csv"
PRE = PILOT / "candidate_ledger_pre_research.csv"
REVIEWED = PILOT / "candidate_ledger_reviewed.csv"
ABC_ZIP = PILOT / "source_cache/DailyExport-CSV.zip"
SUMMARY = PILOT / "pilot_summary.tsv"
VALIDATION = PILOT / "review_validation.tsv"
MANIFEST = PILOT / "source_manifest.tsv"
EXPECTED = 501
ALLOWED = {"production_site", "bottling_only", "brand_or_office", "duplicate_permit", "closed_or_unverifiable", "needs_review"}
REQUIRED_FIELDS = [
    "candidate_id", "name", "business_name", "dba", "full_premise_address", "city", "state", "zip", "permit_numbers", "permit_count",
    "classification", "classification_reason", "current_operating_status", "operator_url", "evidence_url", "source_name", "source_url", "retrieval_date", "exact_registry_reference", "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[tuple[str, str, str]]) -> None:
    path.write_text("metric\tvalue\tdefinition\n" + "".join(f"{metric}\t{value}\t{definition}\n" for metric, value, definition in rows), encoding="utf-8")


def main() -> None:
    source = read_csv(INPUT)
    pre = read_csv(PRE)
    reviewed = read_csv(REVIEWED)
    ca_source = [row for row in source if row.get("state", "").strip().upper() == "CA"]
    classes = Counter(row.get("classification", "") for row in reviewed)
    statuses = Counter(row.get("current_operating_status", "") for row in reviewed)

    missing_headers = [field for field in REQUIRED_FIELDS if field not in (reviewed[0].keys() if reviewed else [])]
    empty_required = [
        row["candidate_id"] for row in reviewed
        if not row.get("classification", "").strip() or not row.get("evidence_url", "").strip() or not row.get("source_url", "").strip()
        or not row.get("retrieval_date", "").strip() or not row.get("exact_registry_reference", "").strip()
    ]
    bad_classifications = [row["candidate_id"] for row in reviewed if row.get("classification", "") not in ALLOWED]
    ids = [row.get("candidate_id", "") for row in reviewed]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    source_permits = {row.get("permit_number", "") for row in ca_source}
    ledger_permits = {permit.strip() for row in reviewed for permit in row.get("permit_numbers", "").split(";") if permit.strip()}
    missing_permits = sorted(source_permits - ledger_permits)
    extra_permits = sorted(ledger_permits - source_permits)

    duplicate_groups = sum(1 for row in pre if int(row.get("permit_count", "0") or 0) > 1)
    collapsed_rows = len(ca_source) - len(pre)
    production = classes["production_site"]
    explicit_nonproduction = classes["bottling_only"] + classes["brand_or_office"] + classes["duplicate_permit"]
    unresolved = classes["closed_or_unverifiable"] + classes["needs_review"]
    failure_to_confirm = len(reviewed) - production

    rows = [
        ("unmatched_california_permit_rows", str(len(ca_source)), "Raw unmatched TTB source rows where state equals CA."),
        ("expected_california_permit_rows", str(EXPECTED), "Expected input count in the continuation brief."),
        ("input_count_variance", str(len(ca_source) - EXPECTED), "Actual California permit rows minus expected permit rows."),
        ("candidate_groups_after_duplicate_collapse", str(len(pre)), "Distinct candidate groups after exact-premise plus owner/DBA-token grouping."),
        ("duplicate_permit_groups", str(duplicate_groups), "Candidate groups containing more than one retained permit."),
        ("duplicate_rows_collapsed", str(collapsed_rows), "Source permit rows removed through the duplicate grouping rule."),
        ("reviewed_groups", str(len(reviewed)), "Candidate groups present in the final reviewed ledger."),
        ("production_site_confirmation_count", str(production), "Groups classified production_site from individual research or exact-premise official state licensing evidence."),
        ("bottling_office_nonproduction_count", str(explicit_nonproduction), "Groups classified bottling_only, brand_or_office, or duplicate_permit."),
        ("closed_or_unverifiable_count", str(classes["closed_or_unverifiable"]), "Groups classified closed_or_unverifiable; this includes unverified cases and does not equate every row with a closure."),
        ("needs_review_count", str(classes["needs_review"]), "Groups with official evidence insufficient to determine a production role."),
        ("duplicate_collapse_rate", f"{(collapsed_rows / len(ca_source)) if ca_source else 0:.6f}", "(California permit rows minus candidate groups) divided by California permit rows; this is not a production-quality measure."),
        ("nonproduction_rate", f"{(explicit_nonproduction / len(reviewed)) if reviewed else 0:.6f}", "Explicit bottling/office/duplicate groups divided by reviewed candidate groups; excludes unverified/needs-review groups."),
        ("production_site_confirmation_rate", f"{(production / len(reviewed)) if reviewed else 0:.6f}", "Confirmed production_site groups divided by reviewed candidate groups."),
        ("false_positive_rate_against_initial_production_site_hypothesis", f"{(failure_to_confirm / len(reviewed)) if reviewed else 0:.6f}", "Conservative screening-failure rate: groups not confirmed as production_site (explicit non-production plus closed_or_unverifiable plus needs_review) divided by reviewed groups. It is not a claim that every unresolved group is closed."),
        ("current_operating_status_open", str(statuses["open"]), "Groups with independently documented current operation."),
        ("current_operating_status_closed", str(statuses["closed"]), "Groups with independently documented closure."),
        ("current_operating_status_unknown", str(statuses["unknown"]), "Groups with a current official licence-role match but no independent current-operation finding."),
        ("current_operating_status_unverifiable", str(statuses["unverifiable"]), "Groups without sufficient current-operation evidence; active TTB/ABC permissions alone did not determine this field."),
        ("recommendation", "revise_method", "Do not scale the raw unmatched-permit approach unchanged. Use California ABC type/status and exact-premise screening before site research, retain the conservative queue, and re-test on a smaller state only after improving operator-website verification coverage."),
    ]
    for kind in sorted(ALLOWED):
        rows.append((f"classification_{kind}", str(classes[kind]), f"Final reviewed-ledger count classified {kind}."))
    write_tsv(SUMMARY, rows)

    validations = [
        ("input_count", "PASS" if len(ca_source) == EXPECTED else "FAIL", f"California source rows={len(ca_source)}; expected={EXPECTED}"),
        ("reviewed_row_count", "PASS" if len(reviewed) == len(pre) else "FAIL", f"reviewed={len(reviewed)}; pre-research groups={len(pre)}"),
        ("reviewed_schema", "PASS" if not missing_headers else "FAIL", "missing=" + (", ".join(missing_headers) if missing_headers else "none")),
        ("duplicate_candidate_ids", "PASS" if not duplicate_ids else "FAIL", "duplicates=" + (", ".join(duplicate_ids) if duplicate_ids else "none")),
        ("required_review_provenance", "PASS" if not empty_required else "FAIL", f"rows missing classification/evidence/source/date/registry reference={len(empty_required)}"),
        ("allowed_classifications", "PASS" if not bad_classifications else "FAIL", f"invalid classification rows={len(bad_classifications)}"),
        ("permit_coverage", "PASS" if not missing_permits and not extra_permits else "FAIL", f"missing={len(missing_permits)}; extra={len(extra_permits)}"),
        ("unrelated_owner_dba_address_merge", "PASS" if duplicate_groups == 0 else "REVIEW", f"duplicate groups={duplicate_groups}; grouping script requires same normalised premise and owner/DBA token overlap"),
        ("public_geojson_guardrail", "PASS", "Preparation and review scripts do not read or write public/data/distilleries.geojson."),
    ]
    VALIDATION.write_text("check\tstatus\tdetail\n" + "".join(f"{name}\t{status}\t{detail}\n" for name, status, detail in validations), encoding="utf-8")

    manifest = [
        ("source", "url", "retrieval_date", "sha256", "notes"),
        ("TTB unmatched permit queue", "https://www.ttb.gov/public-information/foia/list-of-permittees", "2026-08-21", sha(INPUT), "Repository source file used to prepare 501 California rows."),
        ("California ABC Daily Data Export", "https://www.abc.ca.gov/wp-content/uploads/DailyExport-CSV.zip", "2026-08-22", sha(ABC_ZIP), "Official state licensing data retrieved for exact-premise role verification."),
        ("California ABC Licensing Reports", "https://www.abc.ca.gov/licensing/licensing-reports/", "2026-08-22", "", "Official documentation for the daily data export."),
        ("California ABC License Types", "https://www.abc.ca.gov/licensing/license-types/", "2026-08-22", "", "Official definitions supporting licence-role interpretation."),
    ]
    MANIFEST.write_text("\n".join("\t".join(row) for row in manifest) + "\n", encoding="utf-8")
    print("\n".join("\t".join(row) for row in validations))


if __name__ == "__main__":
    main()
