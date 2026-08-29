# TTB permit list: can it tell us who actually distils?

Research note, 29 August 2026. Read-only. Question: can `data/enriched/ttb_dsp_raw.csv`
support a "listed AND trading, producers only" merge into `public/data/distilleries.geojson`?

**Short answer: no.** The file is a list of FAA Act Basic Permits, not DSP registrations.
It has no operations field, no volume field, and no beverage/industrial split. TTB does
not publish any of those per plant. Details and the fallback below.

## 1. What the local file carries

`data/enriched/ttb_dsp_raw.csv`: 5,484 data rows (5,485 lines with header). Downloaded 24 Jun 2026.

Header: `permit_number,business_name,dba_name,street,city,state,zip,permit_type,status,issue_date`

```
AK-S-15000,GLACIER CREEK DISTILLERY LLC,,1540 N SHORELINE DR,WASILLA,AK,99654,S,ACTIVE,
AK-S-20001,"HIGH MARK DISTILLERY, INC.",,37200 THOMAS ST,STERLING,AK,99672,S,ACTIVE,
AK-S-20002,ROBERT BORLAND,Ursa Major Distilling,3738 MARIPOSA LN,FAIRBANKS,AK,99709,S,ACTIVE,
AK-S-20003,PORT CHILKOOT DISTILLERY LLC,Port Chilkoot Distillery,35 TOTEM ST,HAINES,AK,99827,S,ACTIVE,
AK-S-20004,PATRICK LEVY,Fairbanks Distilling Company,410 CUSHMAN ST,FAIRBANKS,AK,99701,S,ACTIVE,
```

Three of the ten columns are synthetic. `scripts/phase1_fetch_ttb.py` derives `permit_type`
from the permit number, hard-codes `status = 'ACTIVE'`, and leaves `issue_date` blank
(0 of 5,484 rows populated). `dba_name` is blank on 2,191 rows. 52 state codes.

## 2. Is there a permit-type or operations field?

No. Value distributions:

- `permit_type`: `S` on all 5,484 rows. The middle segment of every permit number is `S`.
- `status`: `ACTIVE` on all 5,484 rows (hard-coded, not from TTB).
- `issue_date`: blank on all rows.

`S` is the FAA Act Basic Permit code for a spirits plant. It is not a DSP operations code.
The DSP registration number (`DSP-XX-NNNNN`), which is where distiller / warehouseman /
processor operations live, is not in this file and TTB does not publish it.

The fetch script dropped two raw columns. Re-downloaded today, the raw TTB CSV header is:
`Permit_Number, Owner_Name, Operating_Name, Street, City, State, Prem_Zip, Prem_County, Industry_Type, New_Permit_Flag`
(5,545 rows today). `Industry_Type` is `Distilled Spirits Plant` on all 5,545 rows.
`New_Permit_Flag` is `1` on 18 rows (issued in the last 7 days). Neither helps.

What the names show: the list is much wider than producers. Name keywords across the
5,484 rows: `BREW` 635, `WINERY` 179, `BOTTL` 34, `BLEND` 12, `ETHANOL` 7 (e.g.
`ARKALON ETHANOL, LLC`, KS), plus universities (`MISSOURI STATE UNIVERSITY`), hotels
(`TRILOGY HOSPITALITY / The Carlton Hotel`) and corporate multi-permit holders
(`DIAGEO AMERICAS SUPPLY, INC.` 9 permits, `E. & J. GALLO WINERY` 9). 47 rows are an
individual's name with no trading name at all.

## 3. What the existing pipeline already does

- `phase1_parse_geojson.py`: pulls `region == 'usa'` features into `us_distilleries_seed.csv` (1,911 rows; 1,898 US features in the live geojson today).
- `phase1_fetch_ttb.py`: downloads the FOIA CSV and writes the file above.
- `phase1_match.py`: fuzzy-matches map rows to TTB by state and name (rapidfuzz `token_sort_ratio`, thresholds 85 / 70, address overlap can lift 70-84 to 85).
- `phase1_report.py`: writes `data/enriched/enrichment_report.txt`.

Direction matters: the pipeline enriches map rows with a permit. It never merges TTB rows in.

Existing results (`data/enriched/enrichment_report.txt`, 25 Jun 2026; CSVs refreshed 16 Aug):
- Map rows matched high confidence: 1,182 (61.6%). Review band: 139. Unmatched map rows: 590 (183 of those had no parseable state).
- Unique TTB permits touched by any match: 1,271 (1,176 high + 133 review, 6 map rows share a permit).
- **TTB permits not matched to any map row: 4,213 of 5,484.** That is the merge candidate pool.
- `enrichment_report_phase2.txt` loaded 1,322 matched entities into `data/stillbound_intelligence.db`. No state licence enrichment succeeded.

Nothing in `data/audit/` covers TTB. `united-states_worklist.json` and `pruned_non_distilleries.json` are separate Wikidata / name-based audits.

## 4. What TTB publishes (checked 29 Aug 2026)

Index page: https://www.ttb.gov/public-information/foia/list-of-permittees
Files on it (all `/system/files/2025-04/`): `FRL_Spirits_Producers_and_Bottlers_List.csv`,
`FRL_Wine_Producer_and_Blender_Permit_List.csv`, `FRL_Alcohol_Importer_Permit_List.csv`,
`FRL_Alcohol_Wholesaler_Permit_List.csv`, `FRL_Puerto_Rico_Basic_Permit_List.csv`,
`FRL_Basic_Permits_Issued_Since_the_Last_Publication.csv`, `FRL_All_Permits.json`.

- Spirits CSV: https://www.ttb.gov/system/files/2025-04/FRL_Spirits_Producers_and_Bottlers_List.csv. Ten columns, listed in section 2. No operations column.
- `FRL_All_Permits.json` (84,273 permits): same ten fields. Its own definition reads `Industry_Type - Type of TTB Basic Permit`. Values: Wholesaler 38,957, Importer 21,526, Wine Producer 18,120, Distilled Spirits Plant 5,670. No beverage/industrial split, no operations.
- No separate "beverage" vs "industrial" list exists on that page.
- TTB open data page: https://www.ttb.gov/data. Distilled spirits data there is monthly national statistics only ("Distilled Spirits Production and Operations Reports"). Nothing per plant.
- Beverage DSP requirements: https://www.ttb.gov/business-central/requirements-beverage-distilled-spirits-plant. Confirms operations are tracked on the DSP registration, not the basic permit ("adding processor to the operations", bond must cover "operations as a distiller, warehouseman, or processor"). The registration is not published.
- DSP beverage / industrial application pages: https://www.ttb.gov/applications/distilled-spirits-plant-dsp-beverage and https://www.ttb.gov/applications/distilled-spirits-plant-dsp-industrial. Application forms only, no lists.

There is no producers-only download. The "52.9% zero taxable removals" figure is an aggregate
from TTB statistical reports, and TTB's FOIA JSON says taxpayer-identifying data "is redacted
to prevent a disclosure pursuant to IRC 6103". Per-permit volume will never be published.

## 5. Recommendation

The file cannot support a "listed AND trading, producers only" filter on its own. A basic
permit proves the holder may produce, process or bottle spirits. It does not prove a still,
and it does not prove trading. Any merge from this file alone breaks `inclusion-rules.md`.

Cheapest defensible route, if the US gap is worth closing:

1. Do not bulk-merge the 4,213 unmatched permits.
2. Drop the obvious non-producers by name on the 4,213: winery / brewing / ethanol / fuel /
   university / bottling / blending / hospitality keywords with no distilling keyword.
   That removes 818. 2,228 carry a distilling keyword (`DISTIL`, `SPIRIT`, `WHISK`,
   `VODKA`, `MOONSHINE` and similar). 1,167 are ambiguous (`ARCTIC HARVEST LLC`,
   `MONDAY NIGHT VENTURES LLC`, `DIAGEO AMERICAS SUPPLY, INC.`).
3. Treat the 2,228 as a worklist, not a merge. Each row still needs the evidence the rule
   demands: a producer website or Google Places listing that shows a working distillery at
   that address. That is the same Google Places check the 1,316 existing `google-places`
   US rows went through. A permit row with no web footprint is "listed, not trading" and stays out.
4. Corporate multi-permit holders (Diageo 9, Sazerac 10, Brown-Forman 6) need a manual
   look. Several are warehouses or bottling halls and would need `entity_role` or exclusion.

Rough size: 2,228 web checks. At Google Places rates that is a few dollars, but it is a
day or two of review, and the US is already the map's largest country at 1,898 pins. Suggest
it goes in the QUEUE behind the Irish and Canadian audits unless a client asks for US coverage.

One small fix worth making regardless: `phase1_fetch_ttb.py` should keep `Prem_County`
and `New_Permit_Flag` rather than drop them, and stop synthesising `status` and `issue_date`.

Sources used: the five ttb.gov URLs above, plus local files `scripts/phase1_*.py`,
`data/enriched/enrichment_report.txt`, `data/enriched/enrichment_report_phase2.txt`,
`data/enriched/matched_high_confidence.csv`, `data/enriched/matched_review.csv`,
`docs/data-quality/inclusion-rules.md`, `docs/data-quality/entity-roles.md`.
