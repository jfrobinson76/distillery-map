# Manus Continuation Brief — California TTB Enrichment Pilot

## Context

Continue the Distillery Map data-quality work from the 21 August 2026 coverage audit.

Repository: `/Users/frankrobinson1/Projects/distillery-map`

The map currently publishes 6,131 locations across 141 countries. The strict United States baseline is 1,752 records where `country = United States` and `region = usa`. The TTB reconciliation produced 5,530 active producer/bottler permit rows, of which 4,325 have no current map candidate. California is the first enrichment pilot because it has 501 unmatched permit rows.

The existing US reconciliation files are already in:

`data/audit/us_1752_ttb_reconciliation/`

The most important input is:

`ttb_permits_not_matched_to_map.csv`

Filter by `state == CA`; the expected input count is 501. If the current source produces a different count, record the difference before proceeding.

## Objective

Build a provenance-rich California candidate queue and determine whether the TTB unmatched-permit approach is reliable enough to run on other states.

This is a research and candidate-generation task. It is not a public GeoJSON import.

## Required work

### 1. Prepare the California queue

Use the supplied preparation logic in `prepare_california_ttb_candidates.py`, or implement the equivalent under:

`scripts/prepare_california_ttb_candidates.py`

The script must:

- read `data/audit/us_1752_ttb_reconciliation/ttb_permits_not_matched_to_map.csv`;
- filter to California;
- deduplicate only when premise/address matches and owner or DBA tokens overlap;
- leave unrelated businesses at the same address as separate candidates;
- retain every underlying TTB permit number;
- create a stable candidate ID;
- never modify `public/data/distilleries.geojson`.

Allowed initial classifications:

- `production_site`
- `bottling_only`
- `brand_or_office`
- `duplicate_permit`
- `closed_or_unverifiable`
- `needs_review`

### 2. Verify candidates

For every candidate group, verify against the strongest available evidence.

Priority order:

1. operator’s own website;
2. official state, county or city source;
3. official TTB record for permit identity;
4. reputable secondary source only when primary evidence is unavailable.

Where an operator website exists, inspect it for evidence of a physical production site in California. Do not treat a brand page, office, tasting room, retailer, or bottling address as a production site without evidence.

Record current operating status separately from classification. Do not infer “open” merely because a TTB permit is active.

### 3. Produce the reviewed ledger

Create:

`data/audit/california_ttb_pilot/candidate_ledger_reviewed.csv`

Each row must include at least:

- `candidate_id`
- `name`
- `business_name`
- `dba`
- `full_premise_address`
- `city`
- `state`
- `zip`
- `permit_numbers`
- `permit_count`
- `classification`
- `classification_reason`
- `current_operating_status`
- `operator_url`
- `evidence_url`
- `source_name`
- `source_url`
- `retrieval_date`
- `exact_registry_reference`
- `notes`

Do not leave source URL, retrieval date or registry reference blank for a reviewed row.

Also retain the pre-research output:

- `candidate_ledger_pre_research.csv`
- `research_inputs.csv`
- `preparation_summary.tsv`

### 4. Report the pilot result

Create:

`data/audit/california_ttb_pilot/pilot_summary.tsv`

Include:

- unmatched California permit rows;
- candidate groups after duplicate collapse;
- duplicate-permit groups;
- reviewed groups;
- counts by final classification;
- counts by current operating status;
- production-site confirmation count;
- bottling/office/non-production count;
- closed or unverifiable count;
- needs-review count;
- duplicate-collapse rate;
- non-production rate;
- false-positive rate against the initial “production-site candidate” hypothesis;
- a short recommendation: scale to another state, revise method, or stop.

Define the rates in the summary so they are not ambiguous. At minimum, distinguish duplicate-permit collapse from candidates that fail the production-site test.

## Guardrails

- Do not bulk-import any TTB registry or candidate ledger into the public GeoJSON.
- Do not present 501 permits as 501 distilleries.
- Do not present active permits as proof of current operation.
- Do not merge separate businesses solely because they share an address.
- Do not use a name-only match as confirmation when the city/address disagrees.
- Keep source name, URL, retrieval date and exact permit reference on every row.
- Do not start China, Hungary, Poland or Czech Republic collection in this task.
- Do not design the infographic in this task.
- Do not alter the published map count or public taxonomy as part of the pilot.

## Validation

Before handoff:

1. Check that the California input count is 501 or explain the variance.
2. Check for duplicate `candidate_id` values.
3. Check that every reviewed row has a classification, evidence URL, retrieval date and permit reference.
4. Check that every classification is one of the six allowed values.
5. Check that candidate groups do not contain unrelated owner/DBA/address combinations.
6. Run a CSV schema and row-count validation.
7. Run `git diff --check`.
8. Run `npm run lint` if source code or TypeScript changes.
9. Run `npm run build` if application code changes.
10. Report the exact files created and the false-positive result.

## Handoff

Leave the public GeoJSON unchanged. The valuable output of this task is a reviewed, reproducible California candidate queue and an honest decision about whether the TTB enrichment method scales.

The next task should only expand to another state if the California pilot’s classification quality and false-positive rate justify it.

