# Canada audit — 16 August 2026

Findings from reading `public/data/distilleries.geojson` directly while building the
Canadian whisky ownership map in the Stillbound Knowledge vault. Machine-readable
companion: `data/audit/canada_worklist.json` (144 rows).

Canada holds **245 features** with `country: "Canada"`.

## Defect 1 — 143 Canadian rows carry `region: "usa"`

Only 102 of the 245 carry `region: "canada"`. The other 143 have Canadian
addresses and Canadian coordinates but are tagged to the USA region. Affected
rows include Forty Creek (Grimsby, ON), Okanagan Spirits (Kelowna, BC),
Macaloney's Island Distillery (Victoria, BC), The Liberty Distillery
(Vancouver, BC) and Victoria Distillers (Sidney, BC).

**Impact.** `scripts/export_outreach_universe.py` tiers off `country`, so the
outreach universe is unaffected. Anything keyed on `region` is: region pages,
region filters, and any GTM cohort split that follows the map's own region
convention rather than country. A Canadian cohort drawn on `region` gets 102
rows and silently loses 58% of the country into the US tier.

**Fix.** Mechanical — Canadian address and Canadian coordinates imply
`region: "canada"`. Not applied here: this repo had uncommitted work on
`data/spirit-categories` at the time of the audit, and a 143-row data edit
should not land on top of someone else's in-flight branch.

## Defect 2 — Crown Royal Distillery has the wrong website

`Crown Royal Distillery` (Gimli, MB) carries `website: "http://www.theforks.com/"`.
The Forks is a public market in Winnipeg, roughly 90 km away. It is not the
distillery, and it is not owned by Diageo.

## Defect 3 — coverage is craft-shaped, not industry-shaped

This is a completeness gap rather than a data error, but it is the one that
matters most for targeting.

Only **7 of 245** Canadian rows carry an explicit whisk(e)y signal in name,
description or website. That is expected — the dataset has no spirit-category
field and most rows are named "<Placename> Distillery". The problem is *which*
sites are missing.

Absent from the Canadian set entirely:

- **Black Velvet Distilling, Lethbridge AB** — reported as the second-largest-selling
  Canadian whisky in the world (Heaven Hill, acquired from Constellation 2019)
- **The Diageo Valleyfield plant, QC**, under its own name — the nearest row is
  "Distillerie 3 Lacs"
- Still Waters / Stalk & Barrel, ON
- Dillon's, ON
- Last Mountain, SK
- Two Brewers / Yukon Spirits, YT

Meanwhile the set carries dozens of craft gin, vodka and rum producers.

Province split of the 245: QC 57 · ON 47 · BC 46 · AB 41 · NS 14 · SK 13 ·
NB 11 · NL 2 · **MB 1** · unresolved 13. Manitoba is the province containing
Gimli, one of the largest whisky distilleries in the country, and it has a
single row.

**Read.** A Canadian whisky target list drawn straight from this file would
miss the biggest brands in the category and prospect gin distillers instead.
Coverage needs an industrial-plant pass before Canada is used for GTM.

## Related

- Vault: `07 Network and adoption/Canadian Whisky Ownership Map.md` — the nine
  industrial plants and who owns each
- Vault: `00 Home/Canada Market Entry and GTM Plan.md` — why these defects block
  the ops-intelligence cascade run for Canada
- `docs/gtm/README.md` in the `stillbound` repo — the outreach universe caveats
  this extends
