# California TTB Enrichment Pilot

**Run date:** 22 August 2026

**Scope:** California rows in `data/audit/us_1752_ttb_reconciliation/ttb_permits_not_matched_to_map.csv`

**Public map impact:** None. This pilot does not modify `public/data/distilleries.geojson`.

## Purpose and decision

This directory is a **research and candidate-generation record**, not an import list. The federal TTB permit directory identifies permit-level producer/bottler candidates, but its entries do not establish either a one-to-one physical distillery count or current public operation. The raw California queue contained **501 permit rows**, which prepared into **501 candidate groups** under the deliberately strict duplicate rule. The summary therefore recommends **revising, rather than scaling unchanged**, the TTB unmatched-permit workflow.

> An active TTB or state license may establish permit or statutory-function evidence. It does **not** by itself establish that a particular business is currently open.

| Result | Count | Interpretation |
|---|---:|---|
| `production_site` | 138 | A production classification supported by individual evidence or an exact-premise California ABC production-type license match. |
| `bottling_only` | 28 | The evidence indicated agent/rectifier/bottling function without a corresponding production-type classification. |
| `brand_or_office` | 9 | The evidence indicated import, wholesale, broker, agency, or other non-production role. |
| `needs_review` | 47 | An exact-premise official record was found, but it did not establish a production role. |
| `closed_or_unverifiable` | 279 | Closure was documented for some cases; the remainder could not be verified as production sites and are **not** all asserted closed. |

The **false-positive rate against the initial production-site candidate hypothesis is 72.4551%**. This is a conservative screening metric: it counts all groups not confirmed as `production_site`, including explicit non-production cases and unresolved/unverifiable cases. It is not a claim that all unconfirmed businesses are closed.

## Reproducible evidence workflow

The preparation script filters `state = CA`, preserves all underlying permit numbers, and only collapses records when they share the exact normalised street/city/state/ZIP premise and overlap in owner or DBA identity tokens. A shared address by itself cannot merge candidates. For this input no collapse occurred, so each of the 501 source permit rows remained a candidate group.

The review workflow matches the candidate premise and business identity to the **California ABC Daily Data Export**. Current issued `03`, `04`, or `74` licenses are treated as statutory production-role evidence; `05`, `07`, `08`, and `24` support an explicit bottling/rectifying role in the absence of a production-type license. California ABC’s own license descriptions explain the distinction between distilled-spirit production, manufacturer-agent, rectifier, and other functions.[1] The official export is refreshed each business day and is retained locally with a SHA-256 checksum in `source_manifest.tsv`.[2]

| File | Role |
|---|---|
| `candidate_ledger_pre_research.csv` | Pre-research 501-candidate queue, including permit provenance. |
| `research_inputs.csv` | Research queries and registry context for every candidate. |
| `preparation_summary.tsv` | Input checksum, grouping rule, and duplicate-collapse outcome. |
| `abc_premise_matches.csv` | Exact-premise, identity-token matches to the official California ABC export. |
| `candidate_ledger_reviewed.csv` | Final classifications, current-status field, cited source/evidence fields, and exact TTB references. |
| `pilot_summary.tsv` | Counts, unambiguous rates, and the scale recommendation. |
| `review_validation.tsv` | CSV schema, permit coverage, provenance, classification, and identifier checks. |
| `source_manifest.tsv` | URLs, retrieval dates, and source checksums. |

## Evidence coverage and limitations

A focused individual-source pass completed 80 candidate investigations before its available capacity was exhausted; 71 complete structured individual findings could be used in the ledger. All candidates were still screened against the official California ABC daily export using exact-premise and owner/DBA-token matching. Where no completed individual evidence and no exact-premise state match were available, the ledger uses `closed_or_unverifiable` with `current_operating_status = unverifiable`; the note field identifies that conservative limitation.

This makes the output reproducible and honest, but it is **not sufficient to justify bulk map additions**. Before expanding the approach to another state, increase individual operator/municipal-source coverage for the unresolved queue and retain the same non-import guardrail.

## References

[1]: https://www.abc.ca.gov/licensing/license-types/ "California ABC License Types"
[2]: https://www.abc.ca.gov/licensing/licensing-reports/ "California ABC Licensing Reports and Daily Data Export"
[3]: https://www.ttb.gov/public-information/foia/list-of-permittees "TTB List of Permittees"
