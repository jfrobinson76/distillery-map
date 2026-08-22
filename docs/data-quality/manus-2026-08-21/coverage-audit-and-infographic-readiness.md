# Distillery Map: Coverage Audit and Infographic Readiness

**Reviewed:** 21 August 2026  
**Repository snapshot:** `b265f5d` — *Canada, NI and Wales audits — plus a retraction*  
**Scope:** Assess the live map and selected project data for a Visual Capitalist-style LinkedIn infographic, focusing on the United States, China, and Eastern European fruit-spirit coverage.

## Executive assessment

The live map is currently publishing **6,131 locations across 141 countries**. This is a genuine full-dataset map load, not a UI that stops at roughly 1,000 US points. The best current count for United States-coded locations in the US map region is **1,752**; the wider `usa` region displays **1,898** records because it wrongly includes 143 Canada records, two Mexico records, and one Bahamas record. The shortfall relative to a rough 2,000-site US target is therefore a **data-coverage and classification issue**, not a rendering limit. [1] [2]

The present dataset is not ready to support a claim such as **“Every Whiskey Distillery in the World”** or a country ranking of true whiskey distilleries. It intentionally includes gin, vodka, schnapps, grappa, liqueur, tasting rooms, brand shops, bottling plants, and other spirit places. It also lacks a row-level whiskey classification. China has only ten entries, while several Eastern European fruit-spirit countries have small, uneven counts. Those gaps would be mistaken for real differences in distilling activity if visualised as a global league table. [3]

> **Recommended framing:** publish a transparent card about **“6,131 Distillery & Spirit Places Mapped Worldwide”** now. Defer a global **whiskey-distillery ranking** until the dataset has a reliable product taxonomy and the China/Eastern Europe discovery gaps are addressed.

| Key result | Current value | Meaning |
|---|---:|---|
| Published live dataset | 6,131 locations | The correct live total, derived directly from GeoJSON features. |
| Countries represented | 141 | Broad global reach, but not uniform country coverage. |
| `usa` map-region records | 1,898 | Not all are in the United States. |
| US-coded records in the `usa` region | 1,752 | Best current physical-map figure for the US. |
| China records | 10 | Far too incomplete for a country comparison. |
| Explicit non-distilling roles | 20 | Confirms the total is broader than operating distilleries. |
| TTB active producer/bottler permits | 5,530 | Candidate universe, not a count of unique distillery sites. |

## 1. What the live map actually loads

The live homepage says **“6,131 locations and counting.”** The count is calculated from the complete `distilleries.geojson` feature collection, and the Mapbox component fetches that entire file as one clustered source. Clustering changes how dense groups are displayed; it does not discard markers. The only visible result cap is the search-autocomplete list, which returns eight name matches and has no effect on the map source. [1] [2]

The GeoJSON audit found no blank country fields and no duplicate slugs. Its source mix is predominantly Google Places and OpenStreetMap, with smaller Wikidata, curated, community, and other contributions.

| Published GeoJSON profile | Count |
|---|---:|
| Total features | 6,131 |
| Countries | 141 |
| Google Places-origin records | 3,748 |
| OSM-origin records | 1,907 |
| Wikidata-origin records | 204 |
| Explicit `tasting_room` roles | 13 |
| Explicit `head_office` roles | 3 |
| Explicit `bottling_plant` roles | 2 |
| Explicit `brand_shop` roles | 2 |
| Records with a `spirit_type` field | 0 |

The scope is deliberately broad. The project’s data-quality policy says that a site distilling schnapps, grappa, liqueur, gin, or vodka remains in scope; spirit category alone is not a removal criterion. That is a sound choice for a map of spirit places, but it means the total cannot be re-labelled as a whiskey-only count without additional data. [3]

## 2. United States: the apparent undercount reconciled

The original concern that the map was showing only “1,000+ of 2,000” US distilleries is understandable, but the audit shows a different issue. The live US map region contains 1,898 records. Of those, 1,752 are country-coded United States, while 146 are country-assignment anomalies within the regional grouping.

| United States measure | Count | Interpretation |
|---|---:|---|
| `region = usa` | 1,898 | The figure visible through the US region control. |
| United States-coded records within `region = usa` | 1,752 | Best current map count for US locations. |
| All `country = United States` records | 1,758 | Includes six records classified into another display region. |
| Canada records within `region = usa` | 143 | The main source of regional inflation. |
| Mexico records within `region = usa` | 2 | Regional classification error. |
| Bahamas records within `region = usa` | 1 | Regional classification error. |

The repository contains a sensible US audit path based on the US Alcohol and Tobacco Tax and Trade Bureau’s weekly **Spirits Producers and Bottlers List**. A fresh run produced 5,530 active permit records. However, TTB itself explains that these permits can authorise production, bottling, importation, or distribution. Consequently, a federal permit is not equivalent to one operating distillery, one brand, or one geographic site. [4]

| TTB comparison snapshot | Count | Interpretation |
|---|---:|---|
| Active TTB producer/bottler permits | 5,530 | Federal permit records, not a physical-site census. |
| High-confidence map-to-permit matches | 1,122 | Strong verified core of current map records. |
| Borderline matches | 121 | Requires resolution before claiming an audited match. |
| Current map rows unmatched to a permit | 655 | Can include matching failures, historic sites, alternative names, non-production places, or true gaps. |
| Unmatched map rows without parsed state | 301 | An address-normalisation issue that weakens the matching rate. |
| Unique TTB permits matched to map rows | 1,205 | Useful reconciliation metric, not a coverage percentage. |

This makes the practical conclusion clear: **the map is already near a 2,000-place US target but is not yet a reconciled operating-distillery census.** The TTB list should feed a candidate-and-verification queue rather than be imported directly.

## 3. China and Eastern Europe: confirmed coverage gaps

There is no Baidu, AMap/Gaode, or other China-specific collector in the repository. China’s ten published entries consist of eight OSM records and two Google Places records. One Google-derived entry is an operating centre for Yanghe rather than a production site. The current data therefore cannot be used to count Chinese distilleries reliably.

Baidu’s official Place Search 2.0 supports administrative-area, circular, and polygon-area POI search, but uses an application key and enforces quota controls. This creates a credible collection route, yet none of that source is presently represented in the map pipeline. [5]

| Country / market | Current map count | Dominant known sources | Interpretation |
|---|---:|---|---|
| China | 10 | 8 OSM; 2 Google Places | Materially under-mapped. |
| Slovakia | 55 | 41 OSM; 14 Google Places | Better than peers, but source-dependent. |
| Hungary | 46 | Global POI mix | Fruit-spirit traditions make a generic English query unreliable. |
| Czech Republic | 38 | Global POI mix | Likely undercounts regional distillers. |
| Croatia | 24 | 19 Google Places; 4 OSM; 1 submission | Likely undercounts rakija / local fruit-spirit producers. |
| Poland | 18 | 15 Google Places; 3 OSM | Likely undercounts local fruit distillers. |
| Romania | 6 | 4 Google Places; 2 OSM | Strong evidence of a source gap. |
| Bulgaria | 6 | Global POI mix | Strong evidence of a source gap. |
| Lithuania | 0 | None | Explicit coverage void. |

Eastern European fruit distillers are **not excluded by policy**. The low counts are best explained by discovery and verification gaps: local-language naming, very small farm or orchard producers, uneven mapping on global platforms, and few centrally harvested national feeds. The European Commission’s eAmbrosia register is useful as a discovery source because it exposes spirit-drink GIs, product specifications, recognised producer groups, and a public API. It is not a site-level producer census, so it should provide vocabulary and leads rather than country totals. [6]

## 4. Data claim versus infographic claim

The reviewed visual reference uses a portrait social-card format: a high-impact headline, one dominant proportional visual, limited country labels, short explanatory callouts, and a source footer. That format can work extremely well here, provided the headline makes a claim the data can prove.

| Claim | Publish now? | Reason |
|---|---|---|
| “6,131 Distillery & Spirit Places Mapped Worldwide” | **Yes** | Matches the live data and current product scope. |
| “The World’s Distilleries, by Country” | **No** | Implies country counts are exhaustive; China and Eastern Europe are demonstrably incomplete. |
| “The World’s Whiskey Distilleries, by Country” | **No** | No row-level whiskey classification; the data includes multiple spirits and non-production roles. |
| “Where the Distillery Map Is Strongest Today” | **Yes, with care** | Could be a coverage/transparency story rather than a false production comparison. |

The first image should use the current total as an open-data achievement, not as a claim of universal completeness. A suitable editorial hierarchy would be:

1. **Masthead:** “THE WORLD’S SPIRIT PLACES, MAPPED”
2. **Headline number:** “6,131 locations in 141 countries”
3. **Main visual:** country-sized packed-circle or partitioned globe composition, labelled only for the largest mapped countries.
4. **Honest subtitle:** “Distilleries, tasting rooms, and spirit producers in a live community dataset.”
5. **Coverage note:** “China and parts of Eastern Europe are under-mapped; figures describe verified mapped places, not production volume.”
6. **Call to action:** “Know a missing distillery? Add it at distillerymap.org.”

This creates a credible, shareable image while giving the data gaps a productive role in the story: an invitation to contribute rather than a hidden weakness.

## 5. Recommended build sequence

| Priority | Workstream | Specific action | Result |
|---:|---|---|---|
| 1 | Fix public data drift | Update `public/llms.txt` from 6,497 to 6,131. | All public-facing totals agree. |
| 2 | Clarify entity scope | Publish a one-sentence inclusion rule and expose `entity_role` consistently. | The infographic denominator is explainable. |
| 3 | Clean US region metadata | Reassign Canada, Mexico, and Bahamas rows currently in `region: usa`; normalise US state parsing. | US counts and map controls become internally consistent. |
| 4 | Reconcile TTB candidates | Match by permit, entity, DBA, address, and physical site; manually adjudicate the 121 borderline cases. | A defensible US operating-site layer. |
| 5 | Build a China collection route | Collect Baidu POIs using local-language terms and tiled administrative searches; retain POI ID, raw query, harvest date, and verification status. | A deduplicated China candidate layer. |
| 6 | Build Eastern Europe discovery queues | Combine national registers, GI producer groups, OSM, and local-language POI queries for pálinka, slivovitz, rakija, schnapps, and fruit brandy. | Measurable country-by-country coverage improvement. |
| 7 | Add product taxonomy | Add `spirit_types`, `is_distilling_site`, `operational_status`, `verification_level`, `source_ids`, and `last_verified`. | A valid whiskey-only export becomes possible. |
| 8 | Produce the social asset | Create the “mapped places” infographic first; only then pursue a whiskey-specific country comparison. | A strong LinkedIn asset without overclaiming. |

## Bottom line

The map is a substantial live asset: **6,131 unique mapped places in 141 countries**, a community contribution loop, and a social-friendly data story. The map is not missing US points because of a frontend cap. Its gaps are in source acquisition, site-versus-permit reconciliation, regional metadata, and spirit classification.

A polished Visual Capitalist-style post is appropriate **now** if it celebrates the verified mapped-place dataset and clearly marks known blind spots. A global ranking of whiskey distilleries should be treated as a second project, unlocked by China/Baidu collection, Eastern European local-source work, and a transparent row-level taxonomy.

## References

[1]: https://distillerymap.org/ "Distillery Map live homepage"
[2]: https://github.com/jfrobinson76/distillery-map/blob/b265f5d/src/lib/data.ts#L17-L20 "Distillery Map count implementation"; https://github.com/jfrobinson76/distillery-map/blob/b265f5d/src/components/DistilleryMapApp.tsx#L684-L768 "Distillery Map client loading and clustering"
[3]: https://github.com/jfrobinson76/distillery-map/blob/b265f5d/docs/data-quality/removed-non-distilleries-2026-08-16.md#L8-L20 "Distillery Map scope and pruning policy"
[4]: https://www.ttb.gov/public-information/foia/list-of-permittees "TTB List of Permittees"; https://www.ttb.gov/data "TTB Open Data"
[5]: https://lbsyun.baidu.com/faq/api?title=webapi/guide/webservice-placeapi/use "Baidu Maps Place Search 2.0 documentation"
[6]: https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/ "European Commission eAmbrosia register"

## Generated audit artifacts

- `data/audit/published_dataset_summary.tsv` — country, region, provenance, and role snapshot of the published GeoJSON.
- `data/audit/ttb_comparison_summary.tsv` — current TTB-to-map comparison snapshot.
- `scripts/audit_published_dataset.mjs` — reproducible GeoJSON audit.
- `scripts/audit_ttb_comparison.py` — reproducible permit-comparison audit.
