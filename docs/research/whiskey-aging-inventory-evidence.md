# Whiskey Aging Inventory: Evidence Base

Date started: 2026-08-02
Owner: John Robinson
Status: running capture. Add new entries at the top of each section.

**This is the canonical evidence base for `/whiskey-aging-inventory`.** The page and the
share card are generated from `src/lib/aging-inventory.ts`, which holds the live figures,
tiers and per-entry caveats. That module is the source of truth for *what the numbers are*.
This file is the source of truth for *why*: where each figure came from, the arithmetic
behind every derived number, what was corrected and when.

Keeping the working shown is the only way a later session, or a distiller in the comments,
can check us. Two figures in the first pass were wrong in ways that were invisible from the
conclusion alone.

If you change a number in `aging-inventory.ts`, add the reasoning here in the same session.
A figure whose derivation only exists in a chat transcript is a figure nobody can defend.

Rule for this file: **every number carries a provenance grade and the arithmetic that
produced it.** If a figure cannot be traced to a source or a shown calculation, it does
not belong here and it certainly does not belong on a slide.

### Provenance grades

| Grade | Meaning |
|---|---|
| **Counted** | A trade body, tax authority or regulator publishes a physical count |
| **Derived** | Converted from an official aggregate in another unit. Conversion shown |
| **Estimate** | Named private report with a stated method, no audited basis |
| **Producer** | A single company disclosing its own stock. No national total exists |
| **Dark** | No published figure. Order-of-magnitude only, openly labelled |

---

# Part 1. Global standing stock, August 2026

Best estimate: **approximately 58 million casks and barrels**, plausible range 52 to 65
million. Almost certainly the largest volume of whiskey ever maturing at one time.

Live at `distillerymap.org/whiskey-aging-inventory`. Figures are generated from
`src/lib/aging-inventory.ts`; the table below is a snapshot for reading, not the source
of truth. If the two disagree, the module wins and this table needs updating.

| Region | Central | Range | Grade | Source |
|---|---|---|---|---|
| United States | 25m | 23 to 27m | Derived | DISCUS national inventory, KDA |
| Scotland | 22m | 21 to 23m | Counted | Scotch Whisky Association |
| Ireland | 4.5m | 4 to 5m | Estimate | LYQD Irish Whiskey Supply Report 2026 |
| Canada | 3m | 2 to 4.5m | Producer | Crown Royal (Gimli), Diageo AR 2025 |
| Japan | 1.5m | 0.8 to 2.5m | Dark | None published |
| India | 0.9m | 0.4 to 2m | Dark | None published |
| Continental Europe | 0.3m | 0.2 to 0.5m | Dark | None published |
| Taiwan | 0.15m | 0.1 to 0.3m | Dark | None published |
| South Africa | 0.15m | 0.1 to 0.2m | Producer | James Sedgwick, 2018 trade reporting |
| Australia and Tasmania | 0.06m | 0.04 to 0.1m | Producer | Lark, ASX reporting |
| England and Wales | 0.05m | 0.05 to 0.07m | Counted | English Whisky Guild |
| Rest of world | 0.15m | 0.1 to 0.3m | Dark | None published |

**Two countries, the United States and Scotland, hold about 81% of it.** Everything else
on the map is a rounding error or a guess.

## Derivations, shown

**United States, 25m barrels.** DISCUS reports American whiskey inventory of approximately
**1.5 billion proof gallons** at end-2024, tripled since 2012. A 53-gallon barrel filled at
the 125-proof legal maximum holds 66.25 proof gallons; allowing for lower fill proofs and
alcohol lost to evaporation gives a working band of 55 to 66 proof gallons per barrel.
1,500m / 66.25 = 22.6m. 1,500m / 55 = 27.3m. Central 25m.

**US years of supply, 14.6.** Same DISCUS release: 1.5bn proof gallons of stock against
58m domestic sales plus 45m exports = 103m proof gallons a year. 1,500 / 103 = 14.6 years.
This is arithmetic on their own published figures, not our modelling.

**Bottle equivalent, ~26bn.** 58m casks at a deliberately conservative 450 bottles each.
The SWA's own ratio (22m casks = 12bn bottles) implies 545; we blended that down against
smaller US barrel yields. Illustration only.

---

# Part 2. The four evidence rules

These were derived from the failures below. They are the operative discipline for any
supply figure that reaches a customer.

**1. Money is not barrels.** Diageo reports $7.2bn of maturing whisk(e)y and Brown-Forman
$1.57bn of barrelled whiskey. Both audited, neither a cask count. Balance-sheet values
prove the scale of capital tied up in maturation and pin down warehouse geography. They do
not convert without a documented conversion and an aligned scope.

**2. Capacity is not inventory.** Kavalan's widely repeated 300,000 barrels is what its
warehouses hold, not what is in them. Capacity is a building. The same applies to cooperage
output: a barrel made this year is an input flow, not stock under maturation.

**3. A state is not a country.** Kentucky's 17.1m barrels is quoted everywhere as the
American figure. It is one state and it counts all spirits, not just whiskey. It is roughly
two-thirds of the US national total.

**4. Sales are not stock.** India is the case study. See Part 4.

---

# Part 3. Ireland: the 16M refutation

**Claim under test:** "16M barrels aging in Ireland", with "11M with Irish Distillers".
Carried as recall in a separate commercial working paper and earmarked for a slide, which
is how it came to be tested at all.

**Verdict: refuted, 2026-08-02.** Ireland holds approximately **4.5 million casks**.

## Provenance of the 4.5M

Not in the LYQD review we hold. That review (`~/Downloads/Review of LYQD Irish Whiskey
Supply Report 2026 (1).md`) contains **no standing-inventory figure at all**. It covers
capacity, CAGR, sales share, tariffs and the 2025 production pauses.

The 4.5M comes from LYQD's own public announcement of the report and from trade coverage
quoting it: Irish Examiner, and Irish Whiskey Magazine, both describing it as "nearly nine
years of global supply". Same source, different communication. Grade: Estimate.

## The arithmetic, tested against LYQD's own verified capacity figure

Irish production capacity is 140 MLPA (million litres of pure alcohol) per annum. That is
verified in the review.

*Testing 4.5M:*
- 4.5m casks at ~200L = ~900m litres of liquid
- at ~60% ABV cask strength = ~540m LPA
- LYQD calls that nearly nine years of global supply, implying ~60 MLPA of annual sales
- independent cross-check: Irish whiskey sells roughly 15m nine-litre cases a year;
  15m x 9L = 135m litres bottled at 40% = ~54m LPA
- 60 and 54 agree closely. **Consistent.**
- 60 MLPA of sales against 140 MLPA of capacity is the same overcapacity picture as the
  separately verified finding that 90% of distilleries paused or cut output in 2025

*Testing 16M:*
- 16m casks at ~200L and ~60% = ~1.9bn LPA
- against ~55 MLPA of sales that is **about 35 years of supply**
- accumulating it would need close to 14 years at full 140 MLPA capacity, during the
  decade when that capacity was still being built rather than saturated
- **Fails on its own arithmetic.**

## Where the 16M came from

Almost certainly Kentucky. The KDA reported **16.1 million barrels of aging bourbon** in
2024 and that number has been in trade press all year. The 11M may be the same conflation:
Kentucky's 2020 figure was approximately 11.0m.

This is worth remembering as a failure mode. Both numbers were plausible, memorable, and
attached to the right industry. Nothing about them looked wrong from the conclusion.

## Downstream consequences

- Any conclusion computed off a 5M-of-16M split inherits the error and must be re-derived.
- Open hypothesis, unverified, moderate confidence: Ireland went from four distilleries to
  more than forty in fifteen years, and those entrants have laid down stock against little
  or no mature sales. The long tail may therefore hold a **higher** share of casks than of
  sales. Testable against the full LYQD report.
- No company-level cask split for Irish Distillers or anyone else is published anywhere.
  Do not assert one.

## 🔴 Note the incentive

LYQD is a cask exchange. The review confirms it sells casks from Boann, Great Northern,
West Cork and Ahascragh, all long-tail independents and squarely inside the CaskIQ ICP.
That makes LYQD both an interested party in any Irish supply figure and a plausible data
partner. Treat the 4.5M as good-faith but commercially positioned.

---

# Part 4. India: a correction worth keeping

This one is recorded in full because the first version was wrong in a way that would have
been embarrassing in public, and because the failure mode generalises.

## What was claimed, and why it was wrong

**Claimed:** "Most Indian whisky is molasses-based spirit that never sees oak."

**Wrong.** The three biggest Indian brands use grain spirit:

| Brand | Cases/yr | Composition |
|---|---|---|
| McDowell's No. 1 | 31.4m | Grain spirit with a malt component |
| Royal Stag | 27.9m | Grain spirit plus imported Scotch malt. **Explicitly eliminated molasses neutral spirit** |
| Imperial Blue | 22.8m | Grain spirit plus Scotch malt, positioned *against* molasses blends |
| Officer's Choice | 23.4m | Value tier, where molasses ENA does still dominate |

That is 82m of the roughly 141m Indian cases inside the global top twenty. The majority of
Indian volume is not molasses-based. India's fuel-ethanol programme has also pushed
feedstock toward maize and rice: only about 40% of ethanol supply was sugarcane-based in
2023-24.

Molasses ENA remains common below roughly 800 rupees. As a blanket claim it is out of date.

## What survives, and why the number did not change

The estimate held at 900k casks because the inventory argument never actually depended on
feedstock. That was weak reasoning dressed as evidence. The argument that holds:

1. **The bulk of an Indian blend is extra neutral alcohol**, a near-pure 96% column spirit
   that is not cask-matured. Molasses versus grain is a question about what the spirit is
   distilled *from*, not whether it sits in wood.
2. **The malt that gives these blends character is frequently imported from Scotland,
   already aged**, and therefore already counted inside Scotland's 22m.
3. **A tropical angel's share of 8 to 12% a year** against Scotland's 2% turns whatever is
   laid down in India over in two or three years rather than twelve.

Result: India holds an estimated **1.6% of world maturing stock while outselling everyone
on earth**. That gap is the most counter-intuitive fact in the whole dataset and it became
the fourth evidence rule.

Supporting: there is no compulsory definition of whisky in India, and the Indian voluntary
standard does not require distillation from cereals or maturation. Very little Indian
whisky would qualify as whisky in the EU or UK.

## 🔴 Two opposite traps, both live

- **Do not say Indian whisky is "molasses-based."** Out of date, and an Indian distiller
  will say so.
- **Do not repeat the widely-shared infographic line that "over half of India's alcohol
  sales are local single-malt whiskies."** Also wrong, in the other direction. Officer's
  Choice and Imperial Blue are blends, not single malts.

Either error loses the room. The safe framing is neutral spirit not being cask-matured.

---

# Part 5. What this dataset does and does not count

**The full distillery count is not a whiskey count, and quoting it as one overstates by
roughly 2.5x.**

The dataset has **no spirit-category field**. Properties are name, source, region, country,
description, address, slug, website. Nothing records what a site produces. So the 6,400
includes German fruit distillers, French cognac houses and Italian grappa makers.

- Approximately **2,600** sit inside the stated IE / NI / UK / US / CA jurisdiction sequence
- of those, about 2,500 have a website on file
- only around **167** mention whisk(e)y, bourbon or rye in the name or description

The defensible number for any whiskey-specific claim is the jurisdiction figure, and even
that needs enrichment before US and Canadian rows count as anything.

Two further points:

1. **Never hardcode the total.** It is derived from the geojson at build time and moves with
   every dataset update. Any figure written into a document is a stale snapshot. Re-derive
   on the day it is used. This rule is already in `CLAUDE.md`.
2. The count also *excludes* bonders, blenders, brand-owners and independent bottlers, which
   pushes the other way for any "operators we could reach" framing. The overcount is the
   larger of the two errors and the easier one to miss.

---

# Part 6. Sources

## Ireland
- LYQD Irish Whiskey Supply Report 2026, Martin Purvis. Full report behind registration:
  `https://exchange.lyqd.io/lyqd-irish-whiskey-supply-report-2026/`
- LYQD blog, 90% of distilleries paused or cut output in 2025:
  `https://exchange.lyqd.io/2025/05/03/90-of-irish-distilleries-paused-or-cut-output-in-2025-most-are-back-but-changed/`
- LYQD blog, US faltering / India, Japan, Mexico, Poland:
  `https://exchange.lyqd.io/2025/05/03/the-us-is-faltering-india-japan-mexico-and-poland-are-the-new-frontier/`
- LYQD blog, tariffs and the North/South split:
  `https://exchange.lyqd.io/2025/05/03/15-is-bad-uncertainty-may-be-worse-and-the-north-south-split-adds-a-new-complication/`
- Irish Examiner and Irish Whiskey Magazine coverage quoting the 4.5m cask figure
- Local copy of the review: `~/Downloads/Review of LYQD Irish Whiskey Supply Report 2026 (1).md`

## United States
- DISCUS national inventory reporting: `https://distilledspirits.org/`
- Kentucky Distillers' Association economic impact reports, 2022, 2024, 2025, 2026:
  `https://kybourbon.com/`

## Scotland, England
- Scotch Whisky Association Facts and Figures:
  `https://www.scotch-whisky.org.uk/industry-insights/facts-figures/`
- English Whisky Guild: `https://www.englishwhiskyguild.com/`

## Corporate disclosure (context only, never converted to barrels)
- Diageo Annual Report 2025, maturing inventory $8,677m total, $7,232m whisk(e)y,
  $5,659m attributable to Scotch. Names Gimli and Valleyfield as Canadian sites
- Brown-Forman 2025 Integrated Annual Report, barrelled whiskey $1,567m at 30 Apr 2025
- Pernod Ricard FY24 consolidated statements, ageing inventories mainly whisky and cognac
  at 87% of work in progress
- Crown Royal, Gimli: 1.5m barrels across 51 warehouses (undated company site,
  accessed Aug 2026)

## India
- The Whiskey Wash, Indian whisky overview:
  `https://thewhiskeywash.com/world/everything-you-wanted-to-know-about-indian-whisky/`
- Brand composition: Wikipedia entries for Royal Stag, Imperial Blue, McDowell's No.1
- USDA FAS, India grain-based ethanol shift:
  `https://www.fas.usda.gov/data/india-india-accelerates-initiatives-enhance-grain-based-ethanol-production`
- Case volumes: The Spirits Business Brand Champions 2024, via ranked infographic
  (2023 data period)

## Prior working papers (Manus research, superseded by this file)
Held in `~/Downloads/`: `Global Whiskey Aging Inventory Estimates (2024-2026).md`,
`Whiskey Aging Inventory_ Disclosure-Source Map and Evidence Rules.md`,
`Entity Cards - Whiskey Maturing-Inventory Disclosure Screen.md`,
`research_whiskey_aging_inventory.csv`, `research_whiskey_inventory_disclosures.csv`,
`kentucky_bourbon_cycle_data.csv`, `distillery_pause_registry.csv`.

The evidence-tier framework in those papers is sound and was kept. Their rendered world map
was not: it labelled Kentucky as the USA, mixed casks, barrels and litres on one visual,
sized all markers equally, treated Kavalan's capacity as inventory, and had no global total.
A Tasmania conversion of "26,000 barrel equivalents" from 2.4m litres does not reproduce;
the correct figure is approximately 12,000 at 200L.

---

# Part 7. Where the work lives

**This repo**
- `src/lib/aging-inventory.ts`: the dataset. Figures, tiers, sources, per-entry caveats.
  **Source of truth for the numbers**
- `src/components/AgingInventoryMap.tsx`: the map. Mounds scale by **area**, not height
- `src/app/whiskey-aging-inventory/page.tsx`: the public page
- `src/app/whiskey-aging-inventory/share-card/page.tsx`: 1200x1200 social card.
  `npm run share-card` regenerates `public/share/whiskey-aging-inventory-1200.png`
- `scripts/build-world-svg.mjs`: bakes the world map out of the Natural Earth boundaries
  already in `data/boundaries`. No runtime dependency, no Mapbox call
- `docs/linkedin-aging-inventory-post.md`: draft post, unpublished
- this file: the evidence base
- Commits: `5e4186a` (build), `2bd134d` (India resize, share card), `f8c63a1` (India
  reasoning correction)

**Stillbound** (separate repo, commercial application of the same evidence)
- `docs/strategy/market-sizing-lyqd-v1.md`: sizing conclusions, corrected 2026-08-02 off
  the Ireland refutation in Part 3
- `docs/strategy/market-supply-evidence-v1.md`: the slide-facing subset. Numbers and
  do-not-say rules only. Points back here for the working
- branch `claude/lyqd-market-sizing-correction`

---

# Part 8. Open verification items

- [ ] Download the full Martin Purvis report from `exchange.lyqd.io`. Confirm the 4.5m
      directly in context and get the method: sample frame, cut-off date, duplicate
      controls, bulk versus finished casks.
- [ ] Test the reframe hypothesis: does the Irish long tail hold a higher share of casks
      than of sales? Needs the full report or an Irish Whiskey Association source.
- [ ] Source Irish Distillers' company-level sales share separately. Jameson at more than
      65% is verifiable; the parent company figure of approximately 70% is not.
- [ ] Global bonder, blender, brand-owner and independent-bottler counts. SWA and IWA
      membership rolls. Half-day sprint.
- [ ] Japan. The largest hole in the global dataset. Producer sustainability reports,
      construction planning documents, distillery anniversary material from Suntory,
      Nikka, Kirin, Chichibu. Do not extrapolate from capacity.
- [ ] Africa outside South Africa. Effectively unmapped. The single Sedgwick figure is
      from 2018 and single-sourced.

---

# Part 9. Correction log

| Date | Figure | Was | Now | Why |
|---|---|---|---|---|
| 2026-08-02 | Ireland standing stock | 16m barrels | 4.5m casks | Recall, not in any source. Fails arithmetic against 140 MLPA capacity. Likely Kentucky's 16.1m carried across |
| 2026-08-02 | Irish Distillers holding | 11m barrels | withdrawn | Derived from the 16m. No company-level split is published by anyone |
| 2026-08-02 | Irish inventory asymmetry | "does not hold up arithmetically" | withdrawn, re-testing | Computed off the invented 5m-of-16m split |
| 2026-08-02 | US national stock | 17.1m barrels | 25m barrels | 17.1m is Kentucky only, and counts all spirits not just whiskey |
| 2026-08-02 | India standing stock | 0.4m casks | 0.9m casks, range 0.4 to 2m | First pass did not account for 141m cases a year of bottled volume |
| 2026-08-02 | India reasoning | "most Indian whisky is molasses-based" | neutral-spirit argument | Top three brands use grain spirit. Feedstock was never the load-bearing point |
| 2026-08-02 | Operator count caveat | undercount only | overcount flagged | Dataset has no spirit-category field. ~2,600 in jurisdiction, not 6,400 |
| 2026-08-02 | Tasmania | 26,000 barrel equivalents | ~12,000 at 200L | Source conversion does not reproduce |
