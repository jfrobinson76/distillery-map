# Ownership: method, definitions, and what the numbers are

Built 18 Sep 2026. Everything here is recomputed from files in this folder and the crosswalk;
nothing is hand-typed onto a card.

## Definitions

- **Tied to a company**: a row in `data/company-crosswalk/company-crosswalk.csv` at
  `confidence` `high` or `verified`, registry `companies-house`.
- **Controller**: the top of the company's persons-with-significant-control chain on
  Companies House (`psc-parents.csv`, built by `scripts/build_psc_parents.py`, seven levels
  max). The chain stops at an individual (family-owned; the company is its own top), no PSC
  on record (listed plcs are exempt, so Diageo plc is its own top), or a parent registered
  outside the UK (Pernod Ricard SA, Distell, Brown-Forman Corporation, LLG Topco).
- **Group**: a controller with more than one distillery. **Independent**: a controller with
  exactly one. This is a count of *sites*, not of litres, capacity or revenue.
- **Scotch whisky distillery**: map region `scotland` and either the map description says
  malt/grain/whisky or the repo's category verdict (`data/categories/out_*.json`) includes
  whisky. 178 at 18 Sep; a few are bars or closed sites and the SWA's operating count is
  ~150, so treat the denominator as ±5.

## Why the first card was wrong

The first build (PR #33, 20:41) said **79% independent** across 312 UK distilleries. Two
errors, both caught by asking "what about Loch Lomond?":

1. **One company per site.** Loch Lomond Distillery Co Ltd and Glen Scotia Distillery Co
   Ltd are both Loch Lomond Group, five PSC levels up. A register-company count called them
   independent. Fixed by the PSC roll-up: UK-wide share fell to 71%.
2. **Two industries in one denominator.** England and Wales in the map are the gin belt,
   98-100% independent by nature. Scotland's whisky distilleries are a different industry.
   Cut by category, the UK number described neither.

## Results at 18 Sep 2026, 21:30 (recompute before use)

| Universe | Matched | Group-run | Independent | Groups >1 site | Largest |
|---|---|---|---|---|---|
| UK, all spirits | 312 / 521 | 89 (29%) | 223 (71%) | 15 | Diageo 30 |
| **Scotch whisky** | **150 / 178** | **90 (60%)** | **60 (40%)** | **14** | **Diageo 34** |
| Scotch whisky, if the 28 unmatched are independent (they are all small, post-2005 sites) | 178 | 90 (51%) | 88 (49%) | 14 | Diageo 34 (19%) |

The defensible public line is the Scotch one: *about half of Scotland's whisky distilleries
are independent by count; fourteen groups run the other half; Diageo alone runs one in five.*

Controllers with more than one Scotch site (18 Sep): Diageo plc 34 · Pernod Ricard SA 12 ·
William Grant & Sons Holdings 6 · Emperador Holdings (Whyte & Mackay) 5 · International
Beverage Holdings (Inver House) 5 · Beam Suntory UK Holdings 4 · Bacardi UK 4 · Ian Macleod
4 · Brown-Forman 4 · Distell 3 · Kintail Trustees (Edrington) 3 · Isle of Arran 2 · Glen
Turner Co (La Martiniquaise) 2 · LLG Topco (Loch Lomond Group) 2.

## Known limits

- Counts, not capacity. Diageo's 34 sites make a far larger share of the spirit than 19%.
  Say "by number of distilleries" every time.
- The crosswalk review (Devin, in progress) will change a few rows; some name-search matches
  are still shells. Rebuild before posting.
- Wikidata rows for Diageo sites use Diageo plc directly; the PSC roll-up puts Diageo Scotland
  sites under the same top, so both land in one group.
- A PSC chain stopping at an individual can hide a family group that owns several distilleries
  through separate personal holdings. None found among Scotch sites; possible elsewhere.
