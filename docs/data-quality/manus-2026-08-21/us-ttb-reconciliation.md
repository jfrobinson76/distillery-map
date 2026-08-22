# United States Reconciliation: 1,752 Map Locations vs. 5,530 Active TTB Permits

**Run date:** 21 August 2026  
**Map scope:** `country = United States` **and** `region = usa`  
**TTB source:** current *Spirits Producers and Bottlers List* retrieved through the repository’s TTB fetch script.

## Direct answer

The strict map baseline is **1,752 United States-coded locations**, not 1,898. The larger 1,898 figure is the map’s broad `usa` region and includes 143 Canadian records, two Mexican records, and one Bahamas record. The refreshed TTB source has **5,530 active producer/bottler permit records**. These figures cannot be subtracted to claim 3,778 missing US distilleries: TTB’s list covers permits that can allow production **and/or bottling**, and permit, business, premises, brand, and visitor-site counts are not one-to-one. [1]

The exact strict reconciliation identifies **1,205 unique TTB permits with a map candidate** and **4,325 TTB permits without one**. The latter is the **candidate-enrichment queue**, not an automatic add list.

| Strict reconciliation | Map records | Unique TTB permits | Share of 1,752 map records |
|---|---:|---:|---:|
| High-confidence name/state or name+address match | 1,121 | 1,120 | 64.0% |
| Review match, score 70–84 | 122 | 117 | 7.0% |
| No TTB match under the current state-bounded rule | 509 | — | 29.1% |
| **Total United States map locations** | **1,752** | — | **100.0%** |
| **Total unique TTB permits with a map candidate** | — | **1,205** | — |
| **TTB permits with no map candidate** | — | **4,325** | — |

## Exact mechanics behind the 1,205 permit figure

The high-confidence bucket contains 1,121 map rows but only 1,120 distinct permits. The review bucket contains 122 map rows but only 117 distinct permits. They overlap on 32 permits: in other words, some permits attract both a strong and a weak map-name candidate. Combining the two buckets produces **1,205 unique candidate permits**, rather than 1,237.

| Match-structure check | Count | Why it matters |
|---|---:|---|
| High-only unique permits | 1,088 | Strong map-to-permit linkage. |
| Review-only unique permits | 85 | Immediate manual-verification queue. |
| Permits represented by both high and review map rows | 32 | Do not use the review record to create a new site until resolved. |
| Unique permits matched to multiple map rows | 35 | Could be genuine multi-site operators, tasting rooms, or false fuzzy matches. |
| Extra matched map rows beyond one per permit | 38 | Confirms that map locations and permits are different entities. |

> **The important correction:** 4,325 unmatched TTB permits do not mean “add 4,325 distilleries.” The TTB list is a federal permit directory. It includes bottling and permit-level entities, and the same operating business can appear differently from its visitor or production locations on the map. [1]

## The 509 map locations without a current TTB match

The unmatched map bucket is a **data-quality queue**, not evidence that the map is wrong. It splits cleanly into 155 rows with no state parsed from their map address and 354 rows with a parsed state but no score above 70 against an in-state TTB name.

| Unmatched map blocker | Count | Fix |
|---|---:|---|
| No parsed state | 155 | Normalise addresses, add a structured `state` field, then rematch. |
| Parsed state but low name score | 354 | Review legal name, DBA, closure status, role, and address; then run a broader address-aware match. |
| **Total unmatched map rows** | **509** | Do not delete solely because TTB did not match. |

A fallback name-only search over the 155 unparsed-state records found **54 strong candidates** at score ≥95, 18 high candidates at 85–94, 40 review candidates at 70–84, and 43 without a plausible name candidate. These are verification leads—not automatic matches—because a generic name match can point at a different city or a moved producer. The existing `bismarck-brewing` case illustrates precisely why an apparent name match must be checked against the physical address before being accepted.

## The 4,325 permit candidates: how to use them safely

The downloaded TTB file has 5,530 permit rows, 5,383 distinct listed premises, 5,129 distinct owner names, and 3,177 nonblank DBA names. Even the premise count is not a confirmed count of active public distilleries because the source is a permit directory rather than an operating-site registry. [1]

The unmatched permit queue is nevertheless the strongest available US enrichment source. Its largest state concentrations are below. Treat them as **research workload estimates**, not numbers to publish or bulk-import.

| State | Unmatched active TTB permit candidates |
|---|---:|
| California | 501 |
| Michigan | 277 |
| New York | 275 |
| Texas | 265 |
| Pennsylvania | 240 |
| Washington | 191 |
| Florida | 154 |
| Ohio | 151 |
| Kentucky | 145 |
| North Carolina | 144 |
| Oregon | 125 |
| Georgia | 121 |
| Virginia | 120 |
| Colorado | 117 |
| Tennessee | 101 |

## Fix sequence

### 1. Correct the denominator before adding anything

Use **1,752** as the strict current US map count. Keep the 1,898 `usa`-region count only as a display-region diagnostic, then reassign its 143 Canada, two Mexico, and one Bahamas records to their correct region. This stops the map control from inflating the US figure.

### 2. Resolve verification before coverage

First process the 122 review matches and the 54 strong-name candidates among rows with unparsed states. Confirm address, city, current operating status, and role. This can materially improve the verified portion of the existing map, but it will **not** increase the 1,752 site count.

Next, normalise the 155 map addresses that do not parse to a state. Persist structured address fields—at least `country`, `state`, `city`, postal code, and a normalised street address—rather than repeatedly attempting to extract them from display text.

### 3. Turn the 4,325 TTB records into a site-candidate pipeline

Deduplicate the unmatched TTB rows by premise, owner, DBA, and address. Then classify each candidate into at least: `production_site`, `bottling_only`, `brand_or_office`, `duplicate_permit`, `closed_or_unverifiable`, and `needs_review`. Only geocode and add candidates confirmed as current physical distilling sites.

A workable order is California, Michigan, New York, Texas, Pennsylvania, and Washington—where the unmatched queue is largest—while retaining state-by-state review files so the work is resumable and auditable.

### 4. Separate the infographic number from the audit number

Until the pipeline is complete, use **“1,752 United States locations mapped”** for the strict country figure and identify the total as locations rather than federally permitted distilleries. Do not use 5,530 as a US distillery count. If an infographic needs a US comparison number, use the map count and cite the inclusion rule.

## Deliverables produced

The following machine-readable files contain the exact rows behind the reconciliation:

| File | Contents |
|---|---|
| `data/audit/us_1752_ttb_reconciliation/summary.tsv` | Strict bucket counts by map and TTB record. |
| `data/audit/us_1752_ttb_reconciliation/map_high_confidence.csv` | 1,121 strong map-to-TTB matches. |
| `data/audit/us_1752_ttb_reconciliation/map_review.csv` | 122 cases needing adjudication. |
| `data/audit/us_1752_ttb_reconciliation/map_unmatched.csv` | 509 map rows without a current state-bounded TTB match. |
| `data/audit/us_1752_ttb_reconciliation/ttb_permits_not_matched_to_map.csv` | 4,325 permit candidates, not yet validated as sites. |
| `data/audit/us_1752_ttb_reconciliation/map_unparsed_state_global_name_candidates.csv` | Fallback name candidates for the 155 map rows whose state could not be parsed. |

## References

[1]: https://www.ttb.gov/public-information/foia/list-of-permittees "TTB List of Permittees"; https://www.ttb.gov/data "TTB Open Data"
