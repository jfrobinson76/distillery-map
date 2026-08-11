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
| **Producer** | One or more producers, or a member body, publish actual stock. National total inferred |
| **Dark** | No published figure. Order-of-magnitude only, openly labelled |

---

# Part 1. Global standing stock, August 2026

Best estimate: **60.4 million casks and barrels**, presented publicly as approximately 60
million. Source-bounded scenarios run from 54.7 to 67.7 million, rounded publicly to 55 to
68. The lower case is the mechanical sum of every regional low at once, not a statistical
confidence interval. Almost certainly the largest volume of whiskey ever maturing at one
time.

Live at `distillerymap.org/whiskey-aging-inventory`. Figures are generated from
`src/lib/aging-inventory.ts`; the table below is a snapshot for reading, not the source
of truth. If the two disagree, the module wins and this table needs updating.

| Region | Central | Range | Grade | Source |
|---|---|---|---|---|
| United States | 25m | 23 to 27m | Derived | DISCUS national inventory, KDA |
| Scotland | 22m | 21 to 23m | Counted | Scotch Whisky Association |
| Ireland | 4.5m | 4 to 5m | Estimate | LYQD Supply Report 2026; corroborated by Drinks Ireland 3.1m (2020) rolled forward and a producer bottom-up (Part 4I) |
| Canada | 4.3m | 3.9 to 5.2m | Producer | Crown Royal, Hiram Walker, Alberta Distillers, Black Velvet (Part 4F) |
| Japan | 2.3m | 1.3 to 4m | Producer | NTA throughput model; Ōmi cellar ~600k casks (Part 4E) |
| China | 0.75m | 0.6 to 1m | Producer | Bairun 2025 AR; CADA 2023 survey |
| India | 0.5m | 0.3 to 0.9m | Producer | Piccadily Agro FY26 disclosure; Paul John trade reporting; IMWA (Part 4G) |
| Continental Europe | 0.4m | 0.25 to 0.55m | Producer | DYC 2019 trade figure; High Coast, St. Kilian counts; INAO France flow (Part 4H) |
| Taiwan | 0.15m | 0.1 to 0.25m | Dark | Withdrawal × residence model; capacity never counted (Part 4H) |
| South Africa | 0.15m | 0.1 to 0.2m | Producer | James Sedgwick, 2018 trade reporting, post-2023 corroboration (Part 4H) |
| Australia and Tasmania | 0.1m | 0.04 to 0.2m | Producer | Lark, ASX reporting |
| England and Wales | 0.05m | 0.05 to 0.07m | Counted | English Whisky Guild |
| Rest of world | 0.15m | 0.1 to 0.3m | Dark | None published |

**Two countries, the United States and Scotland, hold about 78% of it.** Everything else
on the map is a rounding error or a guess.

## Derivations, shown

**United States, 25m barrels.** DISCUS reports American whiskey inventory of approximately
**1.5 billion proof gallons** at end-2024, tripled since 2012. A 53-gallon barrel filled at
the 125-proof legal maximum holds 66.25 proof gallons; allowing for lower fill proofs and
alcohol lost to evaporation gives a working band of 55 to 66 proof gallons per barrel.
1,500m / 66.25 = 22.6m. 1,500m / 55 = 27.3m. Central 25m.

**US tier changed to "Official aggregate, converted", 11 Aug 2026.** The US sat in
"Officially counted" while its own basis line read "converted from a national aggregate".
DISCUS publishes proof gallons, not a cask count, and the conversion carries an 18% band
(55–66 proof gallons per filled barrel). Grading that as counted is Rule 3 applied to
everyone except ourselves, on the page whose entire credibility rests on the tiers being
honest. Flagged independently three times on the same day. New tier added between
"counted" and "private-report estimate"; Scotland and England & Wales keep "counted"
because the SWA and the English Whisky Guild publish actual cask figures.

**Tiering rule, to write onto the page in the November edition.** A tier describes the
*dominant input*, not the best input. "Published partial stock" is a claim about what
exists in the world; "official aggregate, converted" is a claim about what we did to it.
Where an entry has both, the tier follows whichever carries the majority of the figure
and the width of the range.

Applying it, for November, not now:
- **Japan is probably mis-tiered.** Ōmi is 600k of 2.3m, roughly a quarter. The other
  three-quarters is the NTA conversion, and that conversion is what carries the 1.3–4m
  range. So "published partial stock" is being set by the minority contributor. Japan
  likely belongs in "official aggregate, converted", with Ōmi demoted to a corroborating
  floor in the basis line rather than the tier justification.
- **Canada then stands up cleanly.** Its 3.9m producer floor genuinely is the majority of
  4.3m, so "published partial stock" is correct there on the same rule.

Deferred deliberately: retiering Japan the same day as the US would be two evidence-class
changes in one pass, and the rule is worth stating publicly at the same time it is applied.

**US years of supply, 14.6.** Same DISCUS release: 1.5bn proof gallons of stock against
58m domestic sales plus 45m exports = 103m proof gallons a year. 1,500 / 103 = 14.6 years.
This is arithmetic on their own published figures, not our modelling.

⚠️ **Unverified, 11 Aug 2026.** We have not confirmed that the 58m domestic-sales figure
counts only American whiskey rather than all whiskey sold in the US including imported
Scotch and Irish. If imports are in there the denominator is too large, so 14.6 would be
an understatement and the true figure higher. The error, if any, runs conservative — but
pin the DISCUS split before quoting 14.6 in anything adversarial.

**Bottle equivalent, ~27bn.** 60.4m casks at a deliberately conservative 450 bottles each.
The SWA's own ratio (22m casks = 12bn bottles) implies 545; we blended that down against
smaller US barrel yields. Illustration only.

**Lower scenario, 54.7m.** This is 23 US + 21 Scotland + 4 Ireland + 3.9 Canada +
1.3 Japan + 0.6 China + 0.3 India + 0.25 continental Europe + 0.1 Taiwan + 0.1 South
Africa + 0.04 Australia + 0.05 England and Wales + 0.1 rest of world = **54.74m**.
Relative to the 60.35m central sum, 2m comes from the US proof-gallon conversion, 1m
from SWA's rounded "some 22m", 1m from Japan, 0.5m from Ireland and 0.4m from using only
Canada's published floor. All other downward allowances together are about 0.8m. It is
a conservative simultaneous-low case, not a claim that each downside is correlated.

**Canada, 4.3m barrels.** The published floor is now four sites: Crown Royal/Gimli 1.5m
(company page), Hiram Walker/Pike Creek more than 1.6m (2016 Trillium profile, 2017 site
visit, later ambassador profile), Alberta Distillers 447k (company page, current) and
Black Velvet/Lethbridge ~340k (Heaven Hill editorial, 2019) = **3.9m**. Central 4.3m adds
an itemised ~0.6m allowance for Diageo's Valleyfield site, the Sazerac system (Canadian
Mist, Old Montreal) and the long tail, shaded down because a withdrawal-times-residence
model built on US consumption (~16.9m 9-litre cases), domestic sales and StatCan's dead
1946–1996 bonded-stock series centres lower, at 3.2m. Range 3.9m, the published sum, to
5.2m, where both methods top out. Full derivation, arithmetic and weaknesses in Part 4F.
Quoted warehouse capacities (Alberta's 500k maximum) are never counted as filled stock.

**Ireland, 4.5m casks.** The headline is LYQD's commissioned supply study (Oct 2025).
No longer single-source: Drinks Ireland published **over 3.1m casks maturing** in its
2010–2020 report (2021), and rolling that forward on production-minus-withdrawals
arithmetic (~790k casks filled/yr at the 2019 production rate against ~500–550k
emptied) lands at ~4.1m by end-2025. A producer bottom-up — Irish Distillers 1.7m
(2021, company blender), Great Northern 500k (company site), Bushmills >500k (trade,
2026), Waterford >70k (receivership sale) = 2.77m published, plus an itemised ~1.05m
allowance — brackets 3.8–4.2m. Both independent lines centre slightly *below* 4.5m.
Range 4–5m held. Full derivation, arithmetic and weaknesses in Part 4I.

**China, 0.75m casks.** Bairun's exchange-filed 2025 annual report says Laizhou had filled
nearly 600,000 maturation casks at year-end. China Daily reported Laizhou at roughly 80%
of domestic whisky production and oak-barrel supply. 0.6m / 0.80 = **0.75m**. Range 0.6m,
the filed producer floor, to 1m. This is deliberately not the sum of every map marker.

**India, 0.5m barrels.** The counted anchor is now NSE-listed Piccadily Agro, which told
investors in April 2026 it holds ~85,000 barrels at Indri; Paul John is trade-reported at
~33,500 casks in Goa. A producer bottom-up across the 20+ malt distilleries lands at
~235k malt casks (range 195–300k), bracketing IMWA's ambiguous "300000+ Barrels" tile —
which may be stock or capacity, since its flagship member uses the same convention for
capacity. Central 0.5m = ~0.3m domestically maturing malt + ~0.15m allowance for matured
grain whisky and drift, rounded up. Range 0.3m to 0.9m. Full derivation in Part 4G.
Revenue share is not barrel share, and sales are not stock.

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
American figure. It is one state and it counts all spirits, not just whiskey.

Pinned 11 Aug 2026. KDA, "The Bourbon State: Challenges Continue Amid Record Barrel
Inventory & Skyrocketing Taxes", 8 Oct 2025: **16.1m barrels of bourbon + ~1m barrels of
other spirits = 17.1m total**, from inventories reported as of 1 Jan 2025 by distilleries
and warehousing companies to the **Kentucky Department of Revenue**.
`https://kybourbon.com/industry-news/the-bourbon-state-challenges-continue-amid-record-barrel-inventory-skyrocketing-taxes/`

So 17.1m is not a wrong number. It is a correct state number quoted as a national one.
That is the sharper correction and it is now fully sourced.

**Retracted in the same pass: "roughly two-thirds of the US national total."** It appeared
here and in the module caveat, and it does not hold. It divides an all-spirits state figure
(17.1m) by a whiskey-only national figure (25m). Those measure different populations, so
the ratio is not real. Compare like with like or not at all. Never restore this line.

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
- ~~No company-level cask split for Irish Distillers or anyone else is published
  anywhere. Do not assert one.~~ **Corrected 10 Aug 2026 (Part 4I):** company-level
  figures do exist — Irish Distillers 1.7m casks (blender, 2021), Great Northern 500k
  (company site), Bushmills >500k (trade, 2026), Waterford >70k (receivership). What
  remains true is that no *complete* company-by-company split is published.

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

## What survived the first correction, and what the association sweep changed

The first correction held the estimate at 900k because the inventory argument never
actually depended on feedstock. That was weak reasoning dressed as evidence. The broader
source sweep then found a stronger anchor: the Indian Malt Whisky Association publishes
**300,000+ barrels**, 20+ distilleries and 15m litres of annual capacity. Its named
members include Amrut, John, Radico Khaitan, Piccadily Agro, Diageo India and Alcobrew and
account for more than 75% of national malt-whisky revenue.

That makes 300,000 a credible published floor, but not a census. IMWA does not define the
scope of the barrel number, and revenue share cannot be converted into barrel share. The
live estimate is therefore now **0.5m, range 0.3m to 0.9m**, rather than 0.9m, range 0.4m
to 2m. The reasoning that still holds:

1. **The bulk of an Indian blend is extra neutral alcohol**, a near-pure 96% column spirit
   that is not cask-matured. Molasses versus grain is a question about what the spirit is
   distilled *from*, not whether it sits in wood.
2. **The malt that gives these blends character is frequently imported from Scotland,
   already aged**, and therefore already counted inside Scotland's 22m.
3. **A tropical angel's share of 8 to 12% a year** against Scotland's 2% turns whatever is
   laid down in India over in two or three years rather than twelve.

Result: India holds an estimated **0.8% of world maturing stock while outselling everyone
on earth**. That gap is the most counter-intuitive fact in the whole dataset and it became
the fourth evidence rule.

The legal boundary also needed correction. India does have a compulsory FSSAI definition,
but it is much broader than the EU definition: whisky can include neutral grain spirit,
rectified grain spirit or neutral spirit of agricultural origin. It does **not** require
every product called whisky to mature. A product labelled "matured" must spend at least one
year in oak or other suitable wood, including wooden chips. IMWA's separate voluntary
Indian malt standard is narrower: grain, single distillery, copper pot stills, and at least
three years in oak below 700 litres. IMWA is pursuing GI recognition; that is an objective,
not present GI status.

## 🔴 Two opposite traps, both live

- **Do not say Indian whisky is "molasses-based."** Out of date, and an Indian distiller
  will say so.
- **Do not say India has no whisky definition or no maturation rule.** It has a broad
  statutory definition and a one-year rule where "matured" is claimed; the IMWA malt
  standard is voluntary and much stricter.
- **Do not repeat the widely-shared infographic line that "over half of India's alcohol
  sales are local single-malt whiskies."** Also wrong, in the other direction. Officer's
  Choice and Imperial Blue are blends, not single malts.

Either error loses the room. The safe framing is neutral spirit not being cask-matured.

---

# Part 4A. China: the map audited, not summed

The supplied "China's Distilleries Map" is an Oak & Barley / China-Britain Business
Council lead map from 2022. It is useful historical evidence of which projects were being
discussed then. It is **not an inventory dataset**: it mixes operating, trial, planned and
unverified sites, includes two Taiwanese distilleries, uses names that do not always match
current English names, and predates the industry's largest stock build.

## National and producer anchors

- The China Alcoholic Drinks Association Whisky Committee's 2023 survey counted **42
  legal entities**, including two in Taiwan: 26 operating, one in trial, eight being built
  and seven planned. Mainland producers held **450,000 oak casks**, up 50% year on year,
  containing 60,000 to 65,000 kilolitres. Approximately 55,000 kL was two years old or
  younger. This is the best national benchmark, but it is now stale.
- Bairun's Shenzhen Stock Exchange-filed 2025 annual report says Laizhou filled its
  500,000th maturation cask on 15 June 2025 and held **nearly 600,000 filled casks** at
  year-end. Its one-million-cask figure is management capacity, not inventory.
- China Daily reported Laizhou at roughly 80% of China's whisky production and oak-barrel
  supply and Panda Brew at nearly 2,000 casks in May 2025. That supports the 0.75m central
  derivation, but it is not a new census.
- Qiandao Jinjiu is a separate boutique operation from Angus Dundee's Chun'an project. It
  filled its first whisky cask on 12 January 2025 and reported **more than 200 casks** by
  October. Its 100,000-litre / roughly 900-cask figure is annual capacity, not stock.

## Every name on the supplied map

| Map label | Normalised identity / status | Inventory treatment |
|---|---|---|
| Goalong, Hunan | Operating producer | No filled count; quoted rack capacity excluded |
| Tianyoude, Qinghai | Operating producer | No filled count |
| World Roasted, Hunan | Operating producer | No filled count |
| Defulai, Henan | Not verified beyond the map | Lead only |
| Mengtai, Inner Mongolia | Trial production reported June 2023 | No filled count |
| Leaven Fu, Liaoning | Not verified beyond the map | Lead only |
| Jishangbao, Shandong | Possibly Gisbelle/Jisbelle; name mismatch unresolved | Do not merge without proof |
| Yuzhijin, Shandong | Producer corroborated by standards work | No filled count |
| Jiangji, Chongqing | Jiangxiaobai/Jiangji is documented as baijiu | Excluded absent whisky evidence |
| The Chuan, Sichuan | Pernod Ricard; operating | Private-cask offers are not total stock |
| Ruins/Quins, Sichuan | Name and status unresolved | Lead only |
| Laizhou, Sichuan | Operating; Bairun listed-company disclosure | Nearly 600,000 filled casks, end-2025 |
| Panda Brew, Guizhou | Operating | Nearly 2,000 casks, May 2025 |
| Chun'an by Angus Dundee, Zhejiang | First cask reported December 2025 | Vision/capacity excluded |
| Long Whisky, Shandong | Not verified beyond the map | Lead only |
| Tsingtao, Shandong | Whisky production reported | No filled count |
| Wuliangchuan, Anhui | Unresolved; possible baijiu confusion | Lead only |
| Weigu, Zhejiang | Not verified beyond the map | Lead only |
| Longwei, Zhejiang | Not verified beyond the map | Lead only |
| Entellus, map says Yunnan | Producer lineage found; map location appears stale | No filled count |
| Eryuan by Diageo, Yunnan | Current name YunTuo; opened November 2024 | No filled count |
| Nine Rivers, Fujian | First casks July 2025 | 3.5m-LPA design capacity excluded |
| Dexi, Fujian | Grace Wine Holdings project; production reported 2024 | No filled count |
| Nantou, Taiwan | Taiwanese, not mainland Chinese | Kept only in Taiwan allowance |
| King Car / Kavalan, Taiwan | Taiwanese | 300,000 is capacity, not stock |
| Daiking Louis, Fujian | Operating producer | No filled count |
| Paihuan/Baihuan, Fujian | Producer lead | No filled count |

Post-map: Qiandao Jinjiu, YunTuo's opening, Nine Rivers' first casks, and Laizhou's scale
show why a visual directory needs dated status fields. CADA already counted more entities
in 2023 than the 2022 map, and recent writers describe many more projects. Distillery count
is not cask count.

China also supplies the cleanest forward-supply story outside the US. Most of CADA's 2023
barrel-aged liquid was two years old or younger, while investment and first fills continued
through 2025. China's new recommended national standard, GB/T 11856.1-2025, took effect on
1 February 2026. It requires two years in wood for whisky new make and three years in oak
for single malt, with casks no larger than 700 litres. That standard defines the category;
it does not turn announced capacity into current stock.

---

# Part 4B. Who can prove what

The expanded source sweep did not uncover another published global barrel total. It did
clarify how each source class should be used.

| Source class | What it can establish | Treatment here |
|---|---|---|
| Regulator, tax authority, national trade body | Physical stock, bonded volume, legal scope | Count or derive when scope and units reproduce |
| Listed-company filing or producer actual | Filled stock at named sites | Published floor; infer national remainder visibly |
| GI, technical file or statutory standard | What legally qualifies and where it must mature | Inclusion boundary, never a count |
| University or industry research institute | Process constraints, archival routes, expert validation | Method and interview target, not a count |
| Writer, historian or book | Leads, context, interviews, archival citations | Follow the citation; do not elevate author reputation into a number |
| Accounting firm, consultancy or VC report | Value, capacity, surveys, investment risk | Use only if sample, date, units and duplicate controls are disclosed |
| Cask exchange, broker or wholesaler | Casks on its own platform or under management | Interested-party evidence; never sum listings without title/custody checks |
| Cooperage | New and repaired barrel flow | Supply-chain context only; output is not aging inventory |
| API, GitHub dataset or Wikipedia | Products, auctions, distilleries and source discovery | Discovery and denominators; never terminal inventory evidence |

**Writers and books.** Gary Quinn's *Irish Whiskey* is a concise product and travel guide,
not an inventory study. Noah Rothbaum's and Jim Murray's whisky bibles are product-universe
and tasting sources. Edward B. McGuire is much stronger for excise history, while Davin de
Kergommeaux is a high-value Canadian expert contact. Fionnán O'Connor is the strongest
archival gateway found: his 2025 TU Dublin PhD drew on distillery day books, excise reports,
government sessions, trade material and private letters. The supplied TU Dublin PDF is
only a one-page project synopsis; the repository record identifies the completed thesis
and its DOI. None of these authors publishes a current global cask count.

**Schools and institutes.** Heriot-Watt's International Centre for Brewing and Distilling
researches raw materials, fermentation, distillation and sustainability. The Scotch Whisky
Research Institute is the member-funded industry RTO and explicitly includes optimised
maturation. Teagasc and TU Dublin are researching Irish whiskey biomarkers and GI
authentication. These are excellent peer-review and expert-interview targets; none exposes
a public warehouse-stock series.

**Accounting firms and cask sellers.** The KPMG Ireland papers are worth reading for market
structure and risk, but one cask-investment paper uses Whiskey & Wealth Club's own P&L and
wholesaler return data. That is disclosed interested-party analysis, not independent global
inventory evidence. The same rule applies to LYQD. A cask can appear under a distillery, a
warehouse keeper, a broker, an exchange listing and a beneficial owner without becoming
five casks. Count the physical filled vessel once; keep title, custody and listing separate.

**Digital data.** Whiskystats is not a junk site; it is a large commercial catalogue of
products, retail prices, auctions and ratings. WHISKY:EDITION is a smaller documented
review API. WhiskeyProject is an old recommendation dataset built from roughly 370
whiskies and scraped reviews. Whisky Hunter indexes auction data from 28 sites. All can
enrich product or market layers. None has a field for the world standing stock of spirit
in wood. Wikipedia remains a useful reference router—its production section led to legal
and association sources—but each underlying citation must be checked one by one.

---

# Part 4C. GI and legal status set the denominator

A barrel can contain spirit that a producer calls whisky locally but that could not be
sold as whisky under another jurisdiction's rule. The map therefore records the governing
boundary separately from the number.

| Region | Status and minimum relevant to this estimate |
|---|---|
| Scotland | Registered GI; at least three years in Scotland, oak casks no larger than 700L |
| Ireland | Registered GI; production and at least three years' maturation on the island of Ireland, wooden casks no larger than 700L |
| EU whisky generally | Statutory category; at least three years in wooden casks no larger than 700L |
| United States | Federal standards; bourbon must enter new charred oak but has no general minimum age; "straight" requires at least two years |
| Canada | Canadian Whisky / Canadian Rye protected; federal rule requires at least three years in small wood in Canada |
| Japan | JSLMA voluntary labelling standard, not a statutory GI; three years in Japan in wood no larger than 700L |
| India | Broad FSSAI whisky category; one year only when "matured" is claimed. IMWA's three-year malt rule is voluntary; GI filing is an objective |
| China | GB/T 11856.1-2025 recommended national standard, effective February 2026; two years for whisky new make, three for single malt, maximum 700L |
| Taiwan | No domestic whisky GI/minimum located; official rules require documentary support for age and geographical claims |
| Australia | Statutory excise definition requires at least two years in wood; no national whisky GI found |
| South Africa | National rule requires three years in wood no larger than 700L |
| England | General UK whisky rule applies; English Whisky GI remains in consultation |
| Wales | Single Malt Welsh Whisky registered as a UK GI in July 2023 |
| Continental EU | EU three-year category applies; individual whisky GIs must be checked in the official registers |

GI status is not a quality score and it is not evidence of filled barrels. It answers the
prior question: **which spirit are we trying to count?**

---

# Part 4D. Historical stock records and the earlier correction cycle

The best historical comparison found is not folklore. Michael Connolly's 2025
data-led history reconstructs Irish and Scottish bonded stocks from Commissioners of
Inland Revenue and Customs & Excise annual reports. For 1870-1922, Scottish bonded stock
reached roughly **six times annual production** while Ireland rarely exceeded **three
times**. Demand fell around the turn of the twentieth century, producing oversupply, low
sales and consolidation. In Scotland, DCL acquired grain distilleries partly to close
excess capacity and support prices. The mechanism—production laid down against expected
future demand, followed by weaker demand—is recognisably the modern correction story.

The records existed at cask level. The Spirits Act 1880 required each warehoused cask to
carry its mark, number, capacity, contents and year. Current HMRC W1 warehouse returns
still collect numbers of casks and litres, but no public UK aggregate was located. That
makes an HMRC data request or FOI route more promising than another web search.

The modern US series is the clearest measurable repeat. DISCUS reports American-whiskey
inventory rising from approximately 475m proof gallons in 2012 to 1,458m in 2024—about
3.1x—while 2024 domestic sales were about 57.6m proof gallons and exports about 45m. The
current 14.6 years-of-supply calculation is not a prediction that every barrel will wait
14.6 years; it is the warning light that stock accumulation outstripped the present sales
flow.

For Ireland, the Irish Whiskey Association currently says **more than 3.5m barrels** are
maturing, but the page does not date the count. That is a valuable official floor and an
independent check on LYQD's newer approximately 4.5m estimate, not a reason to add the two.
The 1875 Dublin whiskey fire's reported loss of 1,900 barrels is useful history, not a
denominator for today's market.

---

# Part 4E. Japan flow-to-stock derivation — 9 Aug 2026

The Japan entry moves from 1.5m (0.8–2.5m, dark) to **2.3m casks, range 1.3–4.0m,
grade producer**. This section shows the whole derivation, including the model that
failed, because the failure is the most important finding.

## What the NTA actually publishes

Japan's National Tax Agency publishes two long whisky series in the annual 酒のしおり
(Sake no Shiori) statistical compendium, both in thousands of kilolitres, whisky
converted to 40% abv equivalent:

**Whisky 製成数量 (production), table 6, file `0012-1.xls`, FY series 1970–2023:**

| FY | 1970 | 1975 | 1980 | 1985 | 1989 | 1995 | 2000 | 2005 | 2010 | 2015 | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 千kL @40% | 139 | 242 | 351 | 252 | 182 | 110 | 122 | 62 | 80 | 111 | 153 | 135 | 127 | 146 | 157 |

**Whisky 課税数量 (taxable removals, domestic 国税局分 only, excluding customs/imports),
table 8, file `0013-3.xls`, same span:**

| FY | 1970 | 1975 | 1980 | 1985 | 1989 | 1995 | 2000 | 2005 | 2010 | 2015 | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 千kL | 130 | 228 | 332 | 252 | 168 | 110 | 100 | 67 | 81 | 120 | 165 | 132 | 131 | 154 | 173 |

The 統計年報 (NTA Annual Statistics Report) for FY2024 (April 2024 – March 2025,
table 8-3, `08_suryo.xlsx`) adds the freshest year: gross whisky 製成 **248,692 kL**
@40%, of which **91,658 kL** was re-designated to other uses (用途変更等 — chiefly
whisky transferred as ingredient into RTD/liqueur production), leaving net production
**157,041 kL**; domestic taxable removals **171,326 kL** (table 8-1); **73** whisky
manufacturing sites declared production.

## The model that fails, and why it had to be killed

The intended derivation was cumulative production minus cumulative shipments over a
trailing window ≈ stock under maturation. **That model is invalid in Japan**, for a
reason the tables themselves prove:

1. **The same FY2024 report publishes whisky 手持数量 (volume on hand at licensed
   manufacturers) at end-March 2025: 53,124 kL @40%.** That is four months of
   throughput. One Suntory site alone (below) holds casks totalling well over
   100,000 kL of liquid. Whatever 手持数量 counts, it is not the maturing warehouse.
2. **酒のしおり note 5 says it outright:** 原料用酒類（ウイスキー原酒…を含む）として
   製成された数量は除いている — quantities produced as raw-material liquor,
   *explicitly including whisky new-make (ウイスキー原酒)*, are excluded from the
   production series.
3. **Production tracks removals almost 1:1 through boom and bust** (351 vs 332 at the
   1980 peak; 62 vs 67 at the 2005 trough). Distillation did not move like that —
   distilleries were mothballed and closed (Karuizawa, Hanyu) in the bust. Output
   that shadows sales is the signature of a quantity measured at bottling.

So Japanese whisky is declared 製成 when it is blended and bottled, at the **end** of
maturation. Maturing spirit is un-declared work-in-progress and appears in no NTA
aggregate. Cumulative production minus shipments measures finished-goods inventory
(which the NTA already publishes: the 53,124 kL), not the warehouse. The largest hole
on the map is a hole by construction, not by neglect.

What the official series *does* pin down, hard, is **throughput**: how much whisky
alcohol leaves the category's production process each year. That supports a different
model.

## Method A: withdrawal × residence time

All figures in kL at 40% abv equivalent unless stated; 1 kL @40% = 400 litres of pure
alcohol (LPA).

**Step 1 — total whisky alcohol packaged, FY2024.** Gross 製成 248,692 kL @40% =
**99.5m LPA**. Gross, not net, because the 91,658 kL re-designated into RTD/highball
production is also real liquid that left the whisky-making process.

**Step 2 — deduct alcohol that never saw a Japanese cask.** Two deductions, both
assumptions, stated plainly:

- *Neutral/raw-spirit filler.* Japan's liquor-tax whisky category legally admits
  blends where malt/grain whisky is as little as 10% of the alcohol; the economy
  shelf and RTD bases use that headroom. The JSLMA's April 2021 "Japanese Whisky"
  standard changed labelling only, not the tax category, so filler is still inside
  the 製成 number. Assumed filler share of gross alcohol: **15% / 30% / 45%**
  (high-stock / central / low-stock case).
- *Imported bulk whisky.* Matured Scotch and Canadian whisky imported in bulk and
  blended in Japan is inside 製成 but matured abroad. Trade reporting (WhiskyInvest
  Direct, March 2020, off SWA data): roughly three-fifths of Scotch shipped to Japan
  travels in bulk; 2019 bulk blended + bulk single grain ≈ 25.6m bottle-equivalents
  ≈ 18,000 kL @40%. Japan Customs stopped splitting bulk from bottled in 2017, so
  the current figure is not knowable precisely. Assumed total bulk (all origins):
  **15 / 25 / 35 千kL** @40%.

Domestic-matured withdrawals W = 248.7 × (1 − filler) − bulk:

| Case | Arithmetic | W (千kL @40%) | W (m LPA) |
|---|---|---|---|
| Low-stock | 248.7 × 0.55 − 35 | 101.8 | 40.7 |
| Central | 248.7 × 0.70 − 25 | 149.1 | 59.6 |
| High-stock | 248.7 × 0.85 − 15 | 196.4 | 78.6 |

**Step 3 — multiply by average residence time.** In steady state, stock = annual
withdrawal × volume-weighted average age at disgorgement. The volume market is NAS
blends and highball liquid at roughly 3–5 years; the premium tail is long but thin.
Assumed **3.5 / 5 / 7 years** (paired with the matching case).

**Step 4 — convert to casks.** Assumed cask population: mixed barrels (180–200L),
hogsheads (~230L), puncheons and sherry butts (~480L, which Suntory uses heavily);
average ~230L filled at 63%, held at ~55–60% through life, angel's share 2–4%/yr in
Honshu's climate (cooler in Hokkaido). Working figure **110–140 LPA per cask** — the
spread also absorbs evaporation, since a cask stays one cask while its contents
shrink.

| Case | Stock (m LPA) | LPA/cask | Casks |
|---|---|---|---|
| Low | 40.7 × 3.5 = 142 | 140 | **1.0m** |
| Central | 59.6 × 5 = 298 | 125 | **2.4m** |
| High | 78.6 × 7 = 550 | 110 | **5.0m** |

Steady-state is the wrong shape for Japan twice over, in opposite directions: laydown
has run far ahead of withdrawals since ~2015 (big-house expansion plus the craft
boom pushes stock *above* the steady-state figure), while today's withdrawals draw on
the lean 1995–2010 laydown years (the documented age-statement shortages — Hibiki 17
and Hakushu 12 suspended in 2018 — push it *below*). The two biases are left to
offset; the honest cost is a wide range, not a false centre.

## Method B: producer bottom-up

- **Suntory, Ōmi Aging Cellar (Higashi-Ōmi, Shiga): ~600,000 casks stored** on one
  site — Japanese trade reporting (約60万樽が貯蔵されている), corroborated by Nikkei
  coverage of repeated expansions (¥5bn in 2015, ¥6bn new warehouse in 2019, further
  building in 2020-22; a contractor's records show a warehouse numbered 81). This is
  reported *stored* stock, not capacity, so it may be counted.
- Suntory also warehouses at Yamazaki, Hakushu (historically one of the largest malt
  sites on earth) and Chita. No total is published; a 1.0–1.6m company-wide band is
  an inference from Ōmi's share, not a source.
- Nikka (Yoichi, Miyagikyo, Tochigi aging plant): nothing published. Scaled at
  roughly a third of Suntory's domestic whisky business: 0.3–0.6m.
- Kirin (Fuji Gotemba, one large integrated site): nothing published. 0.15–0.35m.
- Craft (120+ licensed distilleries by 2025, most laying down since 2016–2023 at
  30–100 kL LPA a year): cumulative ~0.15–0.4m casks.

Sum: **1.6–2.9m casks**, central ~2.2m. Only the first 0.6m of this is reported; the
rest is scaled inference and says so.

## Reconciliation and the number

Method A central 2.4m; Method B central 2.2m. **Central 2.3m casks.** Low **1.3m** —
Method A's mechanical low is 1.0m, but the bottom-up floor (Ōmi 0.6m plus minimal
allowances for Yamazaki, Hakushu, Chita, Nikka, Kirin and craft) will not go below
about 1.3m. High **4.0m** — Method A's 5.0m stacks three extremes at once and Method B
cannot support it; 4.0m already assumes the filler share is small, bulk imports are
small, and residence runs long.

**Independent cross-check.** Japan's implied distillation run-rate (~40–70m LPA/yr)
is roughly an eighth to a tenth of Scotland's (~450–550m LPA in recent years). 2.3m
casks is roughly a tenth of Scotland's counted 22m. Two markets with broadly similar
maturation profiles landing at matching stock-to-flow ratios is weak confirmation,
but it is confirmation the 1.5m guess never had.

## Complications: corrected for, and not

Handled: imported bulk (deducted, as an assumption); neutral-spirit filler (deducted,
as an assumption); exports (inside gross 製成, since bottling precedes export — no
separate correction needed); RTD/highball transfers (kept, via gross rather than net
製成); angel's share (inside the LPA-per-cask band); the pre-2021 labelling question
(labelling changed, tax category did not — which is exactly why the filler deduction
exists); the craft boom (Method B, and the laydown-bias note).

Not handled, and not handleable from published data: actual new-make laydown per year
(published nowhere); the true filler share (the load-bearing assumption); the true
average age; Suntory/Nikka/Kirin totals (all inferred from one reported site); current
bulk import volume (customs stopped splitting bulk from bottled in 2017).

## Grade decision

Producer, not estimate and not counted. One producer site's actual filled stock is
publicly reported (Ōmi, ~600k) and the national total is an inferred allowance
disciplined by official throughput aggregates — which is the definition of the
producer grade, and the same shape as Canada's entry. It is *not* "estimate" grade:
that grade means a named commercial report, and no such report exists for Japan. The
inferred share here (about three-quarters of the central figure) is larger than
Canada's (about a third); the caveat says so.

## 🔴 A correction that came out of this work

The previous Japan caveat cited "a Suntory maturation site abandoned in 2026 [that]
would alone have held 500,000 barrels" as if it evidenced Japanese stock. That site
was **Kingswell, East Ayrshire, Scotland** — a scrapped £150m Scotch maturation
facility (Suntory Global Spirits, March 2026), and capacity besides, not filled
stock. It was never part of Japan's inventory and is removed from the entry. The
in-Japan anchor that replaces it, Ōmi at ~600,000 stored casks, is both real and
larger than the misattributed figure. Logged in Part 9.

---

# Part 4F. Canada derivation — 9 Aug 2026

The Canada entry moves from 4.5m (3.1–5.5m, producer) to **4.3m casks, range 3.9–5.2m,
grade producer**. The headline barely moves; what changes is the quality underneath it.
The published floor rises from 3.1m to 3.9m on two company disclosures that were not in
the evidence base, the unmeasured allowance shrinks from 1.4m un-itemised to ~0.6m
itemised, and the whole entry gains what it never had: an official (if historical)
government stock series and a full throughput model.

## What official Canada actually publishes

**Statistics Canada Table 16-10-0091 (formerly CANSIM 303-0019), "Production, bottling
or stocks of beverages", monthly 1946–2007, archived.** Survey source: Canada Revenue
Agency — this is administrative excise data, not a survey of firms. Dataset page:
`https://open.canada.ca/data/en/dataset/6198e838-b634-4aee-8fe8-ac929bd6200f`; CSV:
`https://www150.statcan.gc.ca/n1/tbl/csv/16100091-eng.zip`. Four series; the one that
matters is **"Stocks of liquor in distilleries and bond warehouse"**, in millions of
litres of absolute alcohol (LAA), end of period:

| Dec of | 1950 | 1960 | 1970 | 1977 | 1980 | 1985 | 1990 | 1993 | 1995 | May 1996 |
|---|---|---|---|---|---|---|---|---|---|---|
| m LAA | 208 | 362 | 833 | 1,096 | 1,079 | 926 | 589 | 659 | 440 | 362 (final) |

The series is **terminated May 1996** — Canada has published no national spirits-stock
figure for thirty years. Three honesty notes: (1) it covers *all* spirits in excise bond,
including rum, brandy and imported goods held in bond, so it is an upper bound on whisky;
(2) there is an unexplained step down between Feb 1995 (628m) and Mar 1995 (398m), and
again into Jan 1996 — a reporting-coverage break, so the mid-90s level is 360–440m LAA,
not a precise point; (3) the companion "production of distilleries alcohol (ethyl)"
series becomes useless for whisky after ~2004 because fuel-ethanol plants flood it
(monthly values jump from ~32m to ~93m LAA in 2005).

What the dead series still proves: Canadian maturing stock ran ~1.1bn LAA at the late-70s
peak (≈ 8m barrels-equivalent — Canada was then the world's largest whisky category, and
the 1980s glut is documented history), and ~360–440m LAA (≈ 2.8–3.4m barrels-equivalent
at 130 LAA/cask) by the mid-1990s. A modern national figure in the 3.9–5.2m-barrel range
(≈ 500–620m LAA) requires stock to have grown 15–40% since 1996. Directionally consistent
with Crown Royal's US volume roughly doubling since the mid-2000s and the industry-wide
laydown of 2015–2022, but not provable from any current official source. CRA's current
Excise Duty Statistical Tables report duty assessed in dollars by fiscal year — money,
which house rule 1 forbids converting — and no stock quantity.

## Method A: withdrawal × residence

Canadian whisky must age at least three years in small wood in Canada
(`https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.%2C_c._870/section-B.02.023.html`),
which anchors minimum residence. All figures in litres of absolute alcohol (LAA).

**Step 1 — US withdrawals.** The US is the market: the Trade Commissioner Service states
the US takes ~90% of Canada's beverage-alcohol exports
(`https://www.tradecommissioner.gc.ca/en/market-industry-info/search-industry/alcoholic-beverages.html`),
and Forbes (Feb 2021) reports 18.69m 9-litre cases exported to the US in 2020
(`https://www.forbes.com/sites/joemicallef/2021/02/20/there-is-a-lot-more-to-canadian-whisky-then-you-realized/`).
Beverage Information Group / DISCUS-adjacent reporting puts US Canadian-whisky volume at
**17.4m 9-litre cases in 2022, −3.1% in 2023 ≈ 16.9m cases**
(`https://bevinfogroup.com/2024/03/28/canadian-whisky-trends-2024-sales-brands-whiskey/`);
NABCA control-state data show a further ~2.6% decline in 2024. Using 2023: 16.9m × 9L =
152.1m litres at 40% = **60.8m LAA**. Consumption is used instead of trade data
deliberately: Canadian whisky moves to the US in a mix of bottled goods and high-proof
bulk, and the customs litre counts are not comparable across that mix, but every litre
consumed as Canadian whisky was matured in Canada regardless of shipping form. One
deduction: Canadian food-and-drug rules allow up to one-eleventh (9.09%) of a Canadian
whisky blend to be non-whisky flavouring (spirits or wine); volume brands use some of
this headroom, premium brands use none. Deduct 0% / 5% / 9%: **60.8 / 57.8 / 55.3m LAA**
(high- / central / low-stock case).

**Step 2 — domestic withdrawals.** StatCan's Control and sale of alcoholic beverages,
FY2023/24: total spirits sales **184.9m litres**
(`https://www150.statcan.gc.ca/n1/daily-quotidien/250307/dq250307b-eng.htm`), whisky
~25–30% of spirits volume (46–55m litres; secondary reporting puts whisky at 46.7m litres
in 2024). Canadian whisky's share of domestic whisky sales against imported Scotch,
bourbon and Irish: assumed **55–65%**. Result: 26–35m litres at 40% =
**10.3 / 12 / 14.1m LAA**.

**Step 3 — other exports.** If the US is ~90% of exports, the rest of the world is ~10/90
of the US figure ≈ 6.8m LAA. Assumed **4 / 6 / 8m LAA**.

**Step 4 — total withdrawals and stock.** W = **69.6 / 75.8 / 82.9m LAA** ≈ 70/76/83.
Residence: legal floor 3 years; the volume brands (Black Velvet, Canadian Mist, Rich &
Rare) run 3–5; Canadian Club and Crown Royal blends run longer; and Canada's documented
surplus of well-aged stock (the bulk 8–15-year whisky sold to US non-distiller producers
through the 2010s) stretches the volume-weighted mean. Assumed **4 / 5.5 / 7 years**.
Stock = 280 / 418 / 581m LAA.

**Step 5 — casks.** Canadian practice: ~200L ex-bourbon barrels re-used across multiple
fills, entry strength often above US practice, long residence and prairie-climate
evaporation. Assumed **145 / 130 / 115 LAA per cask** (the lean figure pairs with the
long-residence case, since older stock has evaporated more).

| Case | Arithmetic | Casks |
|---|---|---|
| Low | 280 / 145 | **1.9m** |
| Central | 418 / 130 | **3.2m** |
| High | 581 / 115 | **5.1m** |

## Method B: producer bottom-up

Published, reported filled stock — not capacity:

- **Crown Royal, Gimli, Manitoba: 1.5m barrels across 51 warehouses.** Company page,
  undated, accessed Aug 2026: `https://www.crownroyal.com/story/our-home`. Cross-check:
  Crown Royal sells ~9m 9-litre cases a year ≈ 32m LAA of withdrawals; 1.5m barrels ≈
  195m LAA implies ~6 years' residence — internally consistent for its blend ages.
- **Hiram Walker & Sons, Windsor/Lakeshore (Pike Creek), Ontario: 1.6m barrels.** Three
  independent statements: Trillium Network manufacturing profile, Sept 2016 ("holds 1.6
  million barrels of spirits in its 14 maturing warehouses",
  `https://trilliummfg.ca/profile/hiram-walker-sons/`); Toronto Whisky Society site
  visit, Mar 2017 (1.6m across 16 warehouses,
  `https://torontowhiskysociety.ca/2017/03/28/tws-visits-hiram-walker-distillery-part-2/`);
  and a later brand-ambassador profile ("more than 1.6m at any given time",
  `https://candradrinks.com/dave-mitton-meet-the-expert/`). Vintage 2016–2019, and
  "barrels of spirits" includes some maturing rum (Lamb's), not whisky alone.
- **Alberta Distillers, Calgary: 447,000 barrels, 23 warehouses.** 🆕 The company's own
  current site: "447k Barrels", "23 Warehouses", 19m OLA annual distillation
  (`https://www.albertadistillers.com/sustainability/our-distillery`, accessed Aug 2026).
  The separately quoted 500,000-barrel maximum (company anniversary site adl75.ca) is
  capacity and is not counted.
- **Black Velvet, Lethbridge, Alberta: ~340,000 barrels, three warehouses.** 🆕 Heaven
  Hill's own editorial, 13 Aug 2019: "placed in one of the three Black Velvet Distilling
  Company Warehouses among approximately 340,000 other barrels"
  (`https://heavenhill.com/news-and-notes/what-is-black-velvet-canadian-whisky/`).

**Published sum: 1.5 + 1.6 + 0.447 + 0.34 = 3.887 ≈ 3.9m barrels.**

Unreported sites, itemised allowance (all inference, no counts published):

- Diageo Valleyfield, Québec — distills, ages and bottles Crown Royal (Diageo 2021
  release); second-largest unreported hole: 0.15–0.5m, central 0.3m.
- Sazerac system — Canadian Mist, Collingwood (nine warehouses, ~3m US gal/yr) plus Old
  Montreal Distillery, against a US portfolio of roughly 4–5m cases (Rich & Rare,
  Canadian LTD, Seagram's VO, Five Star, Canadian Mist): 0.15–0.4m, central 0.2m. Held
  down because part of Sazerac's liquid is bought in bulk from Alberta Distillers and
  Hiram Walker and is therefore already inside their reported barns — the double-count
  risk runs through this whole allowance.
- Forty Creek (Campari), Highwood, Shelter Point, Macaloney's, Two Brewers and ~200
  craft distilleries: 0.05–0.3m, central 0.1m.

Allowance 0.35–1.2m, central **0.6m**. Method B total: low 3.9m (published sum alone,
with the minimal allowance offsetting possible staleness in the 2016–2019 figures),
central **4.5m**, high 5.1m.

## Reconciliation and the number

Method A central (3.2m) sits *below* Method B's published floor (3.9m) — the same
failure direction Japan showed: a steady-state flow model underestimates a market whose
stock reflects decades of higher laydown and long-tailed aging. Reported filled stock
wins where they conflict; the deficit is read as evidence that true mean residence runs
nearer 7 years than 5.5 (76m LAA × 7 / 130 = 4.1m), which is exactly what Canada's
well-documented aged-stock surplus implies. **Central 4.3m** — Method B's 4.5m shaded
down toward Method A, because two of the four published figures are 2016–2019 vintage,
one mixes rum into "barrels of spirits", and Gimli's 1.5m is brand-page copy rather than
a filing. **Low 3.9m** — the published sum; the flow model's mechanical 1.9m low is
overridden by reported stock, as Japan's was. **High 5.2m** — both methods top out at
5.1m independently; 5.2m adds a token margin for simultaneous understatement, and the
old 5.5m high is cut because neither method reaches it.

Implied national stock at the central: 4.3m × 130 ≈ 560m LAA — 25–40% above the last
official reading (1995–96, 360–440m LAA), carried by Crown Royal's growth and the
2015–2022 laydown. Stated as an implication, not a fact.

## Weaknesses, admitted

1. **Half the floor is stale.** Hiram Walker's 1.6m dates to 2016–2019 and includes
   maturing rum; Black Velvet's 340k is 2019. Either could be 10–20% different today,
   in either direction.
2. **The flow model disagrees with the floor.** Method A's central is 0.7m below the
   published sum. The reconciliation explains the gap (long residence, category
   decline) but cannot prove it; if Gimli or Hiram Walker's figures are marketing
   generosity, the truth sits lower than 4.3m.
3. **No current official aggregate exists at all.** The only government stock series
   died in 1996, its last years have a visible coverage break, and it never separated
   whisky from other bonded spirits. Everything since is producer copy and modelling.
4. Smaller: the domestic Canadian-whisky share (55–65%) and the 9.09% additive
   deduction are assumptions; the Sazerac allowance carries live double-count risk
   against bulk whisky aging in counted warehouses.

## Grade decision

Producer, unchanged and now more solidly so: four sites with published filled stock
covering ~90% of the central figure, an itemised inferred allowance for the rest, and a
flow model plus a dead official series as discipline. Not "counted" — no national body
counts anything; not "estimate" — no named commercial report exists for Canada.

---

# Part 4G. India derivation — 9 Aug 2026

The India entry stays at **0.5m casks, range 0.3–0.9m, grade producer**. The headline
does not move; what changes is what holds it up. The floor gains its first anchor that
does not rest on an association stat tile — a listed company telling its investors a
barrel count — and the IMWA figure itself gains a scope warning it should always have
carried.

## What the IMWA figure actually is

The Indian Malt Whisky Association site (`https://indianmaltwhisky.org/`, accessed
9 Aug 2026) presents six stat tiles, quoted verbatim: **"20+" Distilleries · "300000+"
Barrels · "15+" Capacity (Million ltrs. per year) · "100+" Expressions · "300+" Awards ·
"80+" Export to Countries**. The barrel tile's label is one word, "Barrels" — no verb, no
date, no scope. The association was incorporated 8 July 2024 and launched publicly on
20 March 2025 (just-drinks; The Print/ANI); the figures have not visibly been updated
since. Six named members — Amrut, John Distilleries, Radico Khaitan, Piccadily Agro,
Diageo India, Alcobrew — are said to account for more than 75% of Indian malt-whisky
*revenue*.

**The new caution:** Piccadily's own 2024 investor presentation uses the identical
stat-tile convention for warehouse **capacity** — "India's largest independent malt
warehousing capacity: 45,000+ Barrels with holding capacity of 10+ Mn liters of spirit"
(≈222L per barrel). And Piccadily's capacity (100,000) demonstrably exceeds its filled
stock (~85,000). So the IMWA tile has three possible readings — member filled stock,
national malt total, or member barrel capacity — and the site chooses none of them.
Treating 300,000 as a hard published stock floor, as the previous entry did, overstated
its quality.

## Listed-company disclosures — the new floor

**Piccadily Agro (NSE: PICCADIL, BSE: 530305), Indri, Haryana.** Q4 FY26 results
(board meeting 28 Apr 2026, earnings call 29 Apr 2026, via ScanX/MarketsMojo coverage):
the company **"currently holds approximately 85,000 barrels and plans to increase this
to 100,000 barrels in the current year"**; **83,800 barrels were procured in FY26**;
warehouse capacity is being scaled from 45,000 to 100,000 barrels by March 2027; malt
distillation capacity rose from 12 to 30 KLPD during 2025. This is an investor-facing
statement by a listed company, the strongest single India number available.

**Radico Khaitan (NSE: RADICO, BSE: 532497), Rampur, UP.** No barrel count published
anywhere. The company states Rampur has "one of the largest malt spirit maturation
facilities with a capacity of 2.6 million litres per annum" (company site; Feb 2026
investor presentation: Rampur 104.4m litres total capacity, of which 2.6m is malt).
That is an annual **flow**, not stock, and is not converted into a barrel count — it is
used only to discipline an inference below.

**United Spirits / Diageo India (Godawan, Alwar; Epitome Reserve)** and **Allied
Blenders (Iconiq)**: nothing quantitative published on casks or maturation capacity.

**Private producers with trade-reported numbers:**
- **Paul John / John Distilleries, Goa:** "up to 30,000 casks are maturing in a total
  of five warehouses" plus ~3,500 casks in underground cellars — Whisky Advocate,
  17 Nov 2025. Production capacity doubled from 1.5m to 3m litres of alcohol a year in
  2024 (The Drinks Business / The Spirits Business, Aug 2024).
- **Amrut, Bengaluru:** no current count. A 2013 interview reported 4,000 barrels
  (Business Standard); distillation capacity rose from 0.9m to ~1.4m litres a year from
  April 2025 (Ambrosia, Apr 2025).

**Counted + trade-reported floor: 85,000 + 33,500 = 118,500 casks across two of the
20+ distilleries.** Small, but it is the first India floor independent of the IMWA tile.

## Method A: withdrawal × residence

**Step 1 — withdrawals.** CIABC data: Indian-origin single malts sold 345,000 9-litre
cases domestically in 2023 (53% of the ~675,000-case single-malt market — the year they
first outsold Scotch single malts in India), ~400,000 in 2024, and **500,000 in 2025**
(Business Standard, 26 Jul 2026). 500,000 × 9L = 4.5m litres bottled at ~44% average
ABV ≈ **2.0m LPA**. Exports (Amrut and Paul John are export-led; IMWA claims 80+
countries): assumed +0.3 / +0.6 / +1.0m LPA. Domestically matured malt blended into
premium IMFL: assumed +0.3 / +0.7 / +1.5m LPA. W = **2.6 / 3.3 / 4.5m LPA**
(low- / central / high-stock case).

**Step 2 — residence.** IMWA's voluntary standard sets a three-year minimum; core
ranges run 3–7 years old (Paul John's core span is stated as "3 to 7 year old");
tropical angel's share is ~8%/yr in Goa (Whisky Advocate: "an astounding 8% average"
vs Scotland's 2%) and commonly quoted at 10–12% inland. Paul John's own line — "one
year in India is equivalent to four years" — is the mechanism that keeps residence
short. Assumed **3 / 4 / 5.5 years**.

**Step 3 — casks.** ~200–222L barrels (Piccadily's own ratio: 45,000 barrels ≈ 10m
litres) filled at ~62.5% ≈ 125 LPA at fill, falling fast at 8–12%/yr evaporation.
Working mid-life figure **105 / 95 / 85 LPA per cask** (leaner casks pair with the
long-residence case).

| Case | Arithmetic | Casks |
|---|---|---|
| Low | 2.6m × 3 = 7.8m LPA ÷ 105 | **74k** |
| Central | 3.3m × 4 = 13.2m LPA ÷ 95 | **139k** |
| High | 4.5m × 5.5 = 24.8m LPA ÷ 85 | **291k** |

Steady state centres at ~140k — barely above the two-site counted floor and far below
the bottom-up. **Same failure direction as Japan and Canada**, and here it is provable:
the category is growing 25–75% a year, and Piccadily alone procured 83,800 barrels in
FY26 while the entire country's single-malt withdrawals were ~500,000 cases ≈ 22–25k
cask-yields. Laydown is running perhaps three to four times disgorgement. A steady-state
model measures the past, not the warehouse; per the Canada precedent, reported stock
wins.

## Method A′: laydown-side check

IMWA's capacity tile: 15+ million litres a year. Members' stated nameplates reconcile —
Piccadily 30 KLPD ≈ 9–10m L/yr (at ~330 operating days), Paul John 3m, Rampur 2.6m,
Amrut 1.4m ≈ 16m across four members' *current* (post-expansion) figures. At 60–80%
utilisation that fills roughly 45–60k barrels a year at ~200L, against ~20–25k
cask-yields disgorged: net stock growth of ~25–40k casks a year. Integrating the ramp
(capacity was perhaps a third of today's before 2019–2021) supports a standing malt
stock in the **200–350k band by mid-2026**. Consistent with reading the IMWA tile as
stock; also consistent with it being capacity that fills are rapidly catching.

## Method B: producer bottom-up

| Producer | Casks | Basis |
|---|---|---|
| Piccadily (Indri) | **~85k** | Counted — listed-company investor disclosure, Apr 2026 |
| Paul John (Goa) | **~33.5k** | Trade-reported, Nov 2025 |
| Rampur (Radico) | 37–62k, central 50k | Inferred: 2.6m L/yr maturation intake × 3–5 yr ÷ ~210L |
| Amrut | 17–26k, central 20k | Inferred: 0.9m L/yr × 4–6 yr ÷ ~210L |
| Diageo India, Alcobrew, non-members (Mohan Meakin, Khoday's, Kamet/Peak Spirits, craft) | 25–75k, central 45k | Allowance, nothing published |

Sum: low ~195k, central **~235k**, high ~300k domestically maturing malt casks. Only
118.5k of that is counted or reported; the rest is flow inference and says so. The IMWA
tile (300k+) sits at the very top of this range — read it either as a stock claim
slightly ahead of what member disclosures can support, or as a capacity figure in the
Piccadily convention. Either way, domestic malt sits at **0.2–0.35m casks**.

## Reconciliation and the number

- **Malt: central ~0.3m.** Bottom-up central 235k, shaded up because every dated anchor
  is pre-mid-2026 in a market adding ~25–40k casks net a year, and because the Rampur
  and Amrut inferences deliberately ignore pre-2019 cumulative laydown (Rampur has
  matured malt for its blends since the 1990s).
- **Non-malt matured whisky: allowance 0.05–0.3m, central ~0.15m.** Matured Indian
  grain whisky inside premium IMFL (any product labelled "matured" triggers FSSAI's
  one-year rule) plus experimental stock. Nothing published by anyone; this is the
  weakest line in the entry.
- **Central 0.5m** = 0.3 + 0.15, rounded up within the honesty band for snapshot drift.
  A central of 0.45m would also be defensible; 0.5m is kept because the counted anchors
  are all pre-mid-2026 lower bounds in the fastest-growing laydown market on the map.
- **Low 0.3m.** The strict counted-plus-minimal-inference floor is ~0.25m (118.5k
  counted + minimal inferences + 0.05m allowance). 0.3m is kept as the low because it
  only requires the IMWA tile to be directionally right about stock *or* fills to have
  largely caught the capacity it may describe — and every flow anchor says they have.
- **High 0.9m.** Requires the IMWA tile to be member-only stock with a substantial
  non-member malt tail *and* an unreported matured-grain inventory near 0.3m. Nothing
  found supports more.

Sales-to-stock, restated with the new anchors: India moves ~141m cases of whisky a year
and holds ~0.8% of the world's maturing casks, because the bulk of a blend is un-casked
neutral spirit, the imported Scotch malt component is already counted in Scotland's 22m,
and what India does mature turns over in 2–4 years at 8–12%/yr evaporation.

## Weaknesses, admitted

1. **The IMWA tile's scope is unknown.** One word, "Barrels" — and the flagship
   member's own materials use that convention for capacity. The 300k "published floor"
   in the previous entry was weaker than it looked; the floor now rests on Piccadily
   and Paul John instead.
2. **"Holds approximately 85,000 barrels" is earnings-call language via financial-news
   aggregators.** "Holds" may include procured-but-unfilled barrels (83,800 were bought
   in FY26 during a capacity ramp), and the primary transcript has not been checked.
   At 12 KLPD pre-2025, cumulative fills since Indri's ~2017–18 laydown support a
   filled count near 85k, but do not prove it.
3. **The grain-whisky allowance (~0.15m central) has no anchor at all.** No Indian
   producer publishes matured grain stock. 0.05–0.3m is judgment.
4. **Unit ambiguity throughout.** Indian disclosures mix litres of spirit, LPA and
   KLPD nameplate; conversions assumed ~200–222L casks and ~330 operating days.
5. **The flow model is structurally invalid here** (steady state in a 25–75%/yr growth
   market) and is used only as a lower-bound discipline, per the Canada precedent.

## Grade decision

Producer, now properly earned rather than borrowed from an association tile: one listed
company disclosing a held-barrel count to investors, a second site trade-reported, member
fill-rates published, and a national total that is an inferred allowance disciplined by a
throughput model — the same shape as Canada (Part 4F) and Japan (Part 4E).

## 🔴 Standing traps, reaffirmed from Part 4

Do not say Indian whisky is molasses-based (the big three are grain-ENA based; molasses
persists in the value tier). Do not say India has no whisky definition or maturation rule
(broad FSSAI definition; one-year rule where "matured" is claimed). Do not quote the IMWA
barrel tile as a census. Sales are not stock.

---

# Part 4H. Continental Europe, Taiwan, South Africa — 9 Aug 2026

Three entries firmed up in one pass, ~30 web lookups. The headline changes: Continental
Europe moves from 0.3m (0.2–0.5m, dark) to **0.4m casks, range 0.25–0.55m, grade
producer** — the upgrade is driven by one previously-missed anchor, Spain's DYC, plus
two producers who publish actual counted stock. Taiwan keeps its 0.15m central but the
range tightens to **0.1–0.25m** and the basis changes from "inferred from warehouse
footprint" to a stated withdrawal × residence model; grade stays **dark**, honestly.
South Africa's number does not move — **0.15m, 0.1–0.2m, producer** — but the 2018
single-source figure is now corroborated by a post-Heineken-merger profile, which is
worth more than a number change.

## Continental Europe: the bottom-up that was missing

No European country and no EU body publishes a whisky maturing-stock total. What exists
is producer disclosure, one official French flow series, and allowances. Summed:

**Spain — DYC, ~170,000 casks, the missed elephant.** Trade press (Alimarket, 29 Mar
2019) describes Beam Suntory's DYC plant at Palazuelos de Eresma, Segovia as having
"seis alambiques y 170.000 barricas de envejecimiento" — six stills and 170,000 aging
casks (`https://www.alimarket.es/alimentacion/noticia/295757/beam-suntory-eleva-su-capacidad-en-espana-e-inicia-la-exportacion-de--dyc--a-latinoamerica`).
Cross-checks: El Español's site report (8 Dec 2024,
`https://www.elespanol.com/reportajes/20241208/destilerias-dyc-cuna-whisky-espana-toman-bebida-barata-cata-ciegas-no-diferencian-macallan/906409730_0.html`)
gives 9–11m bottles a year and ~1m LAA/yr of malt spirit alone; Wikipedia records 20m
litres/yr capacity in the 1980s, since running at a fraction
(`https://en.wikipedia.org/wiki/Destiler%C3%ADas_y_Crianza_del_Whisky_S.A.`).
Sanity: 10m bottles × 0.7L × 40% ≈ 2.8m LAA/yr of withdrawals; at 3.5–5 years'
volume-weighted residence that needs 10–14m LAA in wood ≈ 90–130k × ~110-LAA ex-bourbon
barrels before counting the older premium stock — 170k filled casks is consistent, not
inflated. Honesty notes: the figure is 2019, single-outlet, and "barricas de
envejecimiento" could be read as the cellars' cask complement rather than an audited
stock count. Taken at 165k central, 120–180k.

**France — official flow, modelled stock, ~100,000 casks.** The INAO's Commission
Nationale note on the Whisky Français GI application (séance of 7 Jun 2023,
`https://extranet.inao.gouv.fr/fichier/COMNAT-EDV-20230607-Note-Whisky-Fran%C3%A7ais.pdf`)
is the best official document any European country has: ~100 active distilleries plus
~10 éleveurs-affineurs; **20,000 hl of pure alcohol of French whisky produced in 2020**
(vs ~500 hl in 2000, 14,000 hl in 2019); **>4,500 hl AP commercialised in 2022**; only
about half the distilleries yet hold 3-year-old spirit; the four largest produce ~1,800
hl AP each. The Fédération du Whisky de France (65 member companies; ~2m bottles sold
2024, 250k exported — `https://distilnews.fr/federation-whisky-france-10-ans-indication-geographique/`)
represents "la quasi-totalité" of production. Stock model, production-integral form
(France is stock-building — output is ~4× sales, so withdrawal × residence would be
structurally wrong here, the mirror of the India Part 4G case):
cumulative production 2010–2025 ≈ 126,500 hl (linear ramp 3,000→20,000 hl to 2020)
plus 2021–25 at ~20,000 hl/yr ±20% ≈ 100,000 hl → ~226,500 hl central (range
150,000–250,000). Minus cumulative withdrawals ~30–40,000 hl (sales ramp 1,000→6,000
hl/yr) and evaporation ~25–35,000 hl (2–4%/yr on young stock). Stock ≈ **8.5 / 16 / 20m
LAA**. At 110–150 LAA per cask (French practice mixes 190–225L ex-bourbon with 300–400L
wine and cognac wood): 57k / 123k / 182k. Central shaded to **100k (60–170k)** because
not every distilled hectolitre is held as whisky and some producers have cut laydown.

**Sweden — one published count, one bankruptcy estate, ~45,000 casks.** High Coast
publishes actual stock: "more than 20,000 casks are maturing in the warehouses" —
company press release, 8 Apr 2026, which also announces production cut from 200,000 to
~70,000 LPA/yr with warehouses full
(`https://www.highcoastwhisky.se/pressmeddelande/high-coast-distillery-adapts-for-continued-expansion`).
Mackmyra filed for bankruptcy 19 Aug 2024
(`https://www.svt.se/nyheter/lokalt/gavleborg/mackmyra-whisky-ansoker-om-konkurs`;
`https://spiritsnews.se/mackmyra-i-konkurs/`); press coverage quoted ~4,500 reserved
customer 30L casks in store, and the 2023 annual report
(`https://mb.cision.com/Main/411/3963446/2741000.pdf`) records >24,000 personal casks
sold since 2002 and a 49 MSEK write-down of the maturing stock — money, which rule 1
forbids converting, so Mackmyra's own full-size stock enters as a 10–25k allowance.
Smögen, Hven, Agitator, Norrtelje and the rest: 5–15k. Sweden **45k (35–60k)**, noting
much of it is 30–100L casks, which inflates cask counts relative to litres.

**Germany — one counted producer, a long micro tail, ~35,000 casks.** St. Kilian, the
largest German whisky distillery, stores ~10,500 casks in 21 converted ammunition
bunkers (~600 casks each) at Hainhaus plus ~1,030 mostly-30L customer casks on site;
2024 production 70,000 LPA against a 2021 peak of 280,000 LPA
(`https://fosm.de/st-kilian-destillerie-2024/`; German press put the bunker count at
10,679 casks as of Feb 2025). The Verband Deutscher Whiskybrenner counts 50+ member
craft distilleries (`https://www.deutsche-whiskybrenner.de/`); total German whisky
producers run into the hundreds, nearly all fruit-brandy-scale. Tail allowance 15–35k
(Slyrs, Finch, Hercynian in the low thousands each; micros in the dozens). Germany
**35k (25–50k)**.

**Denmark — flow-modelled, ~22,000 casks.** Stauning: Diageo/Distill Ventures-funded
expansion to 24 stills and 750,000 LPA capacity
(`https://www.masterofmalt.com/distilleries/stauning/`;
`https://stauningwhisky.com/pages/distillery`), scaled back ~25% of staff after
Diageo's exit (`https://www.thespiritsbusiness.com/2025/04/stauning-cuts-jobs-as-diageo-exits/`).
No cask count published anywhere we could find. At an assumed 300–500k LPA/yr actual
2018–2024, stock ≈ 2m LAA ≈ 15–25k casks; Thy, Fary Lochan, Nyborg, Copenhagen and the
rest add 3–7k. Denmark **22k (15–30k)**.

**Netherlands — back-calculated from an evaporation disclosure, ~7,000 casks.**
Zuidam/Millstone's profile states warehouse evaporation of 4–6%/yr, "approximately 125
litres per day" (`https://www.whisky.com/whisky-database/distilleries/details/zuidam.html`).
125 L/day × 365 ≈ 45,600 L/yr; at 4–6% that implies ~760–1,140k litres in wood ≈
3,800–5,700 × 200L casks. Undated database figure, so held loosely. NL incl. Kampen
and others: **7k (4–10k)**.

**Rest of the continent — allowance, ~30,000 casks.** Austria's and Switzerland's
micro clusters, Finland (Kyrö, Teerenpeli), Italy (Puni), Belgium (Owl), Czechia
(Gold Cock), plus everything unnamed: **30k (20–50k)**. Pure judgment, said plainly.

**Sum:** central 165+100+35+45+22+7+30 = **404k ≈ 0.4m casks**. Low: 120+60+25+35+15+4+20
= 279k ≈ **0.25m**. High: 180+170+50+60+30+10+50 = 550k ≈ **0.55m**.

### Grade decision — Europe

**Producer.** The definition requires one or more producers publishing actual filled
stock with the national total an inferred allowance: DYC (170k, trade-reported), High
Coast (20k+, company-published, 2026) and St. Kilian (~10.5k, counted, 2024–25) clear
that bar, and the French component sits on an official INAO flow series. The weakness,
admitted: **~40% of the central number hangs on one 2019 Spanish trade figure** that
has never been re-reported and might describe cellar complement rather than filled
stock. If DYC were half full, Europe's central drops to ~0.32m — inside the stated range.

## Taiwan: a model instead of a shrug

**What exists.** Kavalan publishes capacity, not stock: third maturation warehouse
completed 2024, taking storage capacity to 300,000+ casks; production >10m bottles/yr
(`https://en.wikipedia.org/wiki/Kavalan_Distillery`). Whisky.com's database adds that
the 2024 warehouse roughly doubled the space of the first two combined
(`https://www.whisky.com/whisky-database/distilleries/details/kavalan-yuan-shan-distillery.html`)
— which implies warehouses 1–2 hold ~100k and were near full when the build was
justified. TTL's Nantou/Omar distillery was visit-reported at **4,500 casks on site**
in racked warehouses, 180–225L bourbon and sherry wood, 6–7%/yr angel's share, typical
4–5-year maturation (`https://www.whiskygeeks.sg/2017/12/19/taiwanese-whisky-omar-distillery/`;
`http://www.whisky-distillery.net/www.whisky-distilleries.net/Asia/Seiten/Nantou.html`).
No official Taiwanese stock series exists; TTL's public reporting is financial.

**Withdrawal × residence (Kavalan).** Withdrawals: 10m+ bottles × 0.7L at 40–46%
average strength = **2.8–3.2m LAA/yr**. Residence: subtropical maturation, core range
4–8 years, taken at **4 / 5 / 6**. Stock = 11.2 / 14.5 / 19.2m LAA. LAA per cask:
Kavalan's mix runs 200L ex-bourbon through 225–300L wine barriques to 500L sherry
butts, but subtropical evaporation of ~10%/yr strips mid-maturation casks hard —
**130 / 110 / 95 LAA** (high per-cask pairs with the low-stock case):

| Case | Arithmetic | Casks |
|---|---|---|
| Low | 11.2m / 130 | **86k** |
| Central | 14.5m / 110 | **132k** |
| High | 19.2m / 95 | **202k** |

Capacity cross-check, never counted: 132k central is ~45% of the 300k+ post-2024
capacity, and consistent with warehouses 1–2 (~100k) being full by 2023. Add Nantou
(4.5k floor in 2017, grown since: 5 / 10 / 15k) and the micro tail (Holy Distillery
and others, 1–3k): **91k / 144k / 220k → 0.15m central, range 0.1–0.25m.** The prior
0.3m high assumed Kavalan could be at capacity; the model says it is not.

### Grade decision — Taiwan

**Dark, still.** The only published filled-stock figure in the country is a 2017 blog
visit report covering ~3% of the estimate; the dominant producer publishes capacity
only. Producer grade on that basis would be exactly the association-tile mistake India
Part 4G corrected. What improved is the basis — a stated model with arithmetic instead
of "inferred from warehouse footprint" — not the evidence class. Weaknesses: the
bottle-count is a "10,000,000+" infobox figure of uncertain vintage; average residence
and per-cask LAA are assumptions; Nantou's growth since 2017 is a guess.

## South Africa: same number, better dated

**The anchor, re-dated.** The 150,000-cask James Sedgwick figure traces to a dated
site visit: 20 Nov 2018, "Five warehouses are at all times holding 150 000 casks with
maturing whisky", production 10m LAA/yr, angel's share ~5%/yr, then Distell-owned
(`https://whiskyadventurer.com/the-james-sedgwick-distillery/`). The post-merger
corroboration: Maltspedia's current profile describes **"seven large racked warehouses
holding over 150,000 casks"** under Heineken Beverages ownership, 9m litres/yr
(`https://maltspedia.com/distilleries/james-sedgwick-distillery/`). Distell was folded
into Heineken Beverages in 2023 (the profile dates the operational merger 2024). So the
figure now appears on both sides of the ownership change, with the warehouse count
rising 5 → 7 — consistent with stock held or grown, not run down.

**Throughput tension, admitted rather than resolved.** 10m LAA/yr of production
against 150k casks (~16–20m LAA) implies very short average residence. The likely
resolution is that Sedgwick historically distilled grain spirit for Distell blends
sold young or unaged, so whisky-cask residence and total distillation are not the same
series — but no source splits them.

**The craft tail.** Boplaas, Drayman's, Incendo and the rest are real but small; no
stock disclosure was found for any of them (Boplaas was searched for and not found —
said plainly). Allowance ≤10k casks.

**Number: unchanged. 0.15m central, 0.1–0.2m, producer.** What changed is honesty:
"eight years stale, single source" becomes "a 2018 dated count corroborated by an
undated post-2023 profile, neither company-published."

### Grade decision — South Africa

**Producer, kept.** One site's trade-reported stock covers ~100% of the estimate —
the same shape that earns the grade elsewhere. Weaknesses: the corroborating source
is an unbylined aggregator; Heineken Beverages has published no stock figure of its
own; the round 150,000 may simply be the same talking-point recycled for a decade.
This remains the entry we would most like to be corrected on.

## Part 1 effects

Continental Europe +0.1m central lifts the world total from 60.25m to **60.35m ≈
60.4m**; publicly still "approximately 60 million". Low scenario: Europe's low rises
0.2 → 0.25m, so the mechanical low sum moves 54.69 → **54.74m**, still rounding to
54.7. High: Europe +0.05m and Taiwan −0.05m cancel; 67.7m stands.

---

# Part 4I. Ireland corroboration — 10 Aug 2026

The Ireland entry stays at **4.5m casks, range 4–5m, grade estimate**. The number does
not move; what changes is what stands behind it. Until now the figure hung entirely on
one privately commissioned study (LYQD's Irish Whiskey Supply Report 2026, analyst
Martin Purvis, completed Oct 2025, published 21 May 2026 — see Part 3). This pass built
two independent corroboration lines — the industry body's own published count rolled
forward, and a producer bottom-up that did not exist in the evidence base — plus the
same withdrawal-times-residence discipline model used for Japan and Canada. **All three
land within ~10% of 4.5m, and all three centre slightly below it.** The single-source
risk is resolved; the residual risk is that the truth sits nearer 4.1m than 4.5m.

## What official Ireland actually publishes

**Nothing that counts stock.** The Revenue Commissioners administer the Irish Whiskey
GI verification scheme — they physically verify that Irish whiskey matures on the
island (`https://www.revenue.ie/en/companies-and-charities/documents/excise/whiskey-verification-checks.pdf`)
— but publish no bonded-stock quantity series, only excise receipts in euro (money,
which house rule 1 forbids converting). The CSO publishes export *values* (the €890m
2019 figure in the industry's own report is sourced "Central Statistics Office") —
money again, not stock. The pre-independence Inland Revenue bonded-stock series covered
in Part 4D died with the 1922 split. So, like Canada since 1996, modern Ireland has no
official stock series at all; the census-like sources are the industry body and the
commissioned study, and everything else is producer copy and modelling.

## The industry-body anchor: Drinks Ireland's 3.1m, end-2020

**Drinks Ireland | Irish Whiskey (the Irish Whiskey Association, inside Ibec),
"Irish Whiskey 2010–2020" report, published 2021**
(`https://www.ibec.ie/drinksireland/-/media/documents/drinks-ireland-new-website/publications/2021/10-year-report.pdf`):

- "**Has over 3.1 million casks being matured on the island of Ireland**" (industry
  stat panel, p.16); repeated as "it is estimated that there are currently over 3.1
  million casks in maturation on the island" (p.17).
- Method stated: "based on data provided by member companies and on responses or
  publicly-available data from the small number of companies not in association
  membership" — a member census with a gap-fill, the same evidence class as the SWA's
  Scottish count, if less audited.
- Same report, same basis: **over 100 million litres of pure alcohol distilled in
  2019** and **~270,000 used American oak barrels imported in 2019** (the barrel
  imports are noted as a sanity check only, never converted to stock — rule 2), and
  12m 9-litre cases of rolling annual sales by January 2020.

Later published points that bound the curve:

- **Sales:** the association's Irish Whiskey Global Trade Report, announced Dec 2025,
  reports a **record 16.15m 9-litre cases sold in 2024** (US 5.47m; Ireland domestic
  707k) — RTÉ, 9 Dec 2025
  (`https://www.rte.ie/news/business/2025/1209/1547978-whiskey-case-sales/`).
  Export value €1bn in 2024, down ~5% to ~€930m in 2025 (trade reporting, Jan 2026) —
  money, context only.
- **The downcycle:** the association itself said ~**90% of distilleries had paused or
  cut production by May 2025**; named pauses include Midleton, Tullamore, Roe & Co,
  Dublin Liberties (Irish Times, 16 May 2025,
  `https://www.irishtimes.com/business/2025/05/16/irish-whiskey-is-undergoing-a-market-correction-a-temporary-blip-a-little-pause/`),
  with Slane halted for 2026 (Forbes, 30 May 2026). Waterford and Powerscourt are in
  receivership. This caps the growth curve after mid-2025 at roughly flat.
- 2018 warehouse-crunch reporting (industry "needs an absolute minimum of 600,000
  additional timber barrels" of warehousing —
  `https://www.thejournal.ie/whiskey-warehouses-ireland-2-3879433-Mar2018/`) and the
  Vault Storage/Moyvore 200,000-cask facility are **capacity stories and are not
  counted** (rule 2).

**The growth test.** 3.1m (end-2020) → 4.5m (Oct 2025) requires net additions of
~280k casks/yr for five years. Check against flows: >100m LPA distilled a year at
~127 LPA per 200L cask filled at ~63.5% = **~790k casks filled/yr** at the 2019 rate;
withdrawals of 16.15m cases = 145.4m litres at 40% = **58.1m LPA**, and a cask
disgorged after five-to-seven temperate years at ~2%/yr evaporation yields ~105–115
LPA, so **~500–550k casks emptied/yr**. Net ≈ **+240–290k casks/yr** while production
held near the 2019 level — which it did until the 2024–25 cuts. The two published
endpoints and the flow arithmetic reproduce each other almost exactly. The 4.5m is not
just asserted; it is the number the industry's own 2020 count grows into.

## Method A: withdrawal × residence (discipline model)

Same construction as Japan (4E) and Canada (4F). All figures in litres of pure alcohol
(LPA ≡ LAA).

- **Withdrawals.** 16.15m cases (2024, association-published) × 9L × 40% = 58.1m LPA;
  2025 volumes softened. W = **54 / 58 / 60m LPA** (low/central/high stock case).
- **Residence.** Legal floor 3 years (Irish Whiskey Act 1980, GI technical file).
  Jameson-scale blends run ~4–6; premiumisation and the documented aged-stock surplus
  stretch the volume-weighted mean. R = **5 / 6.5 / 8 years**.
- **Stock.** 270 / 377 / 480m LPA.
- **Per cask.** 200L ex-bourbon dominates (270k US barrels imported in 2019 alone),
  some hogsheads and butts; entry ~63%, temperate losses ~2%/yr. **135 / 122 / 110
  LPA per cask** (lean pairs with long residence).

| Case | Arithmetic | Casks |
|---|---|---|
| Low | 270 / 135 | **2.0m** |
| Central | 377 / 122 | **3.1m** |
| High | 480 / 110 | **4.4m** |

As in Japan and Canada, the steady-state model under-counts a market that laid down
for growth: Ireland built 140 MLPA of capacity against ~55–60 MLPA of sales (Part 3).
The ~1.2m-cask gap between the model's central and the reported stock **is the
oversupply everyone is reporting** — the same excess the 90%-paused downcycle is now
working off. The model's deficit and the trade narrative corroborate each other.

## Method B: accumulation from the 2020 anchor

Start from the association's >3.1m (end-2020) and roll forward fills minus
disgorgements:

- **2021–2023:** production held near the 2019 rate (90–110m LPA; capacity was still
  rising toward 140 MLPA) → 710–870k casks filled/yr. Sales rose 12m → 16.15m cases →
  ~470–550k casks emptied/yr. Net **+200k to +350k/yr** → +0.6m to +1.05m over three
  years.
- **2024–2025:** cuts spread until ~90% of distilleries had paused or reduced by May
  2025, including Midleton, the largest filler. Net **0 to +300k over the two years
  combined**.

End-2025 stock: **3.7m / ~4.1m / 4.45m** (low/central/high). LYQD's 4.5m sits at the
top of this corridor but inside it.

## Method C: producer bottom-up

This did not exist in the evidence base at all — Part 3 recorded "no company-level
cask split for Irish Distillers or anyone else is published anywhere." That was wrong.
Published or reported filled stock — not capacity:

- **Irish Distillers (Midleton + Dungourney, Pernod Ricard): 1.7m casks.** Company
  blender Dave McCabe, quoted 20 Jul 2021: "1.7 million casks of whiskey sitting in
  storage"
  (`https://thewhiskeywash.com/whiskey-styles/irish-whiskey/how-the-blenders-of-irish-distillers-manage-1-7-million-irish-whiskey-barrels/`);
  Midleton Very Rare marketing repeats "1.7 million casks". 2025 bicentenary
  write-ups say "over 2 million"
  (`https://thesinglemaltshop.com/2025/04/17/midleton-distillery-at-200/`), but that
  figure derives from ~162 warehouses × 16,000+ casks each = ~2.6m, which is
  **capacity arithmetic, not a count** (rule 2). Floor 1.7m (2021); today plausibly
  1.9–2.2m given Midleton filled hard through 2023.
- **Great Northern Distillery, Dundalk: 500k casks.** The company's own site states
  "500k casks in bond", 20m litres/yr production (`https://www.gndireland.com/`,
  accessed Aug 2026). GND is a contract distiller supplying 400+ labels — the casks
  its clients own sit inside this figure and **must not be counted again** under the
  client brands.
- **Bushmills (Proximo), Co. Antrim: >500,000 casks maturing.** Trade reporting
  around the £62.9m, 26-warehouse phase-two expansion, Mar 2026
  (`https://www.thespiritsbusiness.com/2026/03/bushmills-plans-63m-warehouse-expansion/`;
  also Irish News). The ~20,000-cask-per-warehouse figures in the same coverage are
  capacity and are not counted.
- **Waterford (in receivership): >70,000 casks.** "Over 70,000 casks will be
  available to purchase on the platform, the equivalent of 17 million whiskey
  bottles" — receivers' Prestige Casks platform, Waterford News & Star, 16 Mar 2026
  (`https://www.waterford-news.ie/news/new-platform-launched-for-bulk-sale-of-waterford-whisky_arid-91300.html`).

**Published sum: 1.7 + 0.5 + 0.5 + 0.07 = 2.77m casks** (~62% of the central).

Unreported sites, itemised allowance (inference, no counts published):

- Tullamore D.E.W. (William Grant grain-to-glass campus, on-site maturation):
  0.2–0.4m, central 0.3m.
- Cooley/Kilbeggan (Suntory Global Spirits): 0.15–0.35m, central 0.25m.
- West Cork Distillers, one of the largest independents: 0.1–0.2m, central 0.15m.
- The ~35-distillery long tail (Teeling, Slane, Dingle, Clonakilty, Hinch, Lough
  Gill, Boann, Connacht, Ahascragh, Powerscourt receivership stock…) plus
  independent bonders: 0.2–0.5m, central 0.35m. Held down because much of the long
  tail's liquid was distilled at GND and may sit in GND's counted barns.

Allowance 0.65–1.45m, central **1.05m**. Method C totals: low **3.4m** (published sum
plus minimum allowance), central **3.8m on Midleton-at-1.7m, ~4.2m on
Midleton-at-2.1m**, high **4.9m**.

One tension, noted not resolved: the Midleton bicentenary talking point that its casks
exceed "the combined total of all other whiskey casks maturing in Ireland, North or
South". At a 4.5m island total that requires Midleton >2.25m; at Midleton 1.7m it
would cap the island at 3.4m. Either the talking point is stale or Midleton has grown
well past 1.7m. This is the single biggest swing in the bottom-up.

## Reconciliation and the number

| Line | Low | Central | High | Independence |
|---|---|---|---|---|
| LYQD commissioned study (Oct 2025) | — | **4.5m** | — | The number under test |
| Drinks Ireland 3.1m (2020) + accumulation | 3.7m | **~4.1m** | 4.45m | Independent of LYQD |
| Producer bottom-up | 3.4m | **3.8–4.2m** | 4.9m | Independent of both |
| Withdrawal × residence (steady state) | 2.0m | 3.1m | 4.4m | Discipline floor |

**Corroborated.** Two lines that share no inputs with LYQD land within ~10% of 4.5m,
and every range contains it. **Central stays 4.5m** — the commissioned study remains
the only census-style attempt and the corroboration corridor tops out where it sits.
**Range stays 4–5m**: the low is defended by the 2020 anchor plus undeniably positive
net laydown through 2021–23 (to be under 4m in 2025 would require net adds below
180k/yr through the heaviest laydown years, when the flow arithmetic says 240–290k);
the high is where the bottom-up tops out. The 2024–26 production cuts mean 4.5m is a
plateau figure, not a growth path — do not roll it forward.

## Weaknesses, admitted

1. **Both independent lines centre below 4.5m** (~4.1m and ~3.8–4.2m). If Irish
   Distillers still holds nearer its 2021-published 1.7m than the ~2m+ that recent
   capacity-flavoured copy implies, the truth sits nearer 4.1m.
2. **The 2020 anchor is an association estimate**, member-supplied and unaudited —
   "over 3.1 million" with no decimal places. It is a report figure with a stated
   method, not a tile (the Part 4G distinction), but it is not a filing.
3. **Half the producer floor is soft.** Midleton's 1.7m is 2021-vintage brand copy;
   Bushmills' 500k is trade-reported, not company-published. GND's 500k mixes
   client-owned casks (double-count controlled by never counting client brands
   separately).
4. Smaller: residence (5/6.5/8) and per-cask LPA (110–135) are assumptions; the
   2021–23 production level (90–110m LPA) interpolates between the published 2019
   figure and the 140 MLPA capacity; LYQD is a cask exchange with a commercial
   interest in the figure (Part 3's incentive note stands).

## Grade decision

Estimate, unchanged — but no longer single-source. The headline still rests on the
commissioned study, so the grade cannot rise to producer (the published producer floor
covers only ~62% of the central, against Canada's ~90%), and "counted" is out of the
question with no official series. What changed: the entry now cites an industry-body
count, a producer floor and a flow model that all bracket the same number. The caveat
should say corroborated, and say the direction of residual risk is down.

---

# Part 5. What this dataset does and does not count

**The full distillery count is not a whiskey count.** The current build contains **6,197
locations**; the public-facing shorthand is 6,200. The current working estimate is that
**2,000+ produce whiskey**, but that is an enrichment claim, not a field in the source
geojson and not a denominator used in the aging-stock total.

The dataset has **no spirit-category field**. Properties are name, source, region, country,
description, address, slug, website. Nothing records what a site produces. So the 6,197
includes German fruit distillers, French cognac houses and Italian grappa makers.

- Exactly **2,616** current rows sit in the IE / UK / US / CA jurisdiction proxy: US 1,779,
  UK 534, Ireland 57 and Canada 245, plus one row recorded with country "Scotland"
- exactly **200** mention whisk(e)y, bourbon or rye in the name or description; that is a
  conservative text-match floor, not a producer count
- the approximately 2,000+ working number sits between those bounds and needs a category
  field or website-level classification before it becomes auditable

The defensible public phrasing today is "6,200 distilleries mapped, an estimated 2,000+
making whiskey." It must remain labelled estimated until the category enrichment lands.

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
- Irish Whiskey Association / Drinks Ireland, undated 3.5m+ maturing-barrel floor:
  `https://www.ibec.ie/drinksireland/irish-whiskey/campaigns/depth-and-diversity/10-facts-about-irish-whiskey`
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

## Canada
- Crown Royal, current company page: 1.5m barrels at Gimli across 51 warehouses:
  `https://www.crownroyal.com/story/our-home`
- Toronto Whisky Society 2017 Hiram Walker visit: 1.6m barrels in 16 Pike Creek warehouses:
  `https://torontowhiskysociety.ca/2017/03/28/tws-visits-hiram-walker-distillery-part-2/`
- Dave Mitton profile: Hiram Walker aging more than 1.6m barrels at any time and draining
  and filling 1,300 a day: `https://candradrinks.com/dave-mitton-meet-the-expert/`
- Trillium Network manufacturing profile, Sept 2016: Hiram Walker "holds 1.6 million
  barrels of spirits in its 14 maturing warehouses":
  `https://trilliummfg.ca/profile/hiram-walker-sons/`
- Alberta Distillers company page: 447k barrels, 23 warehouses, 19m OLA annual
  distillation: `https://www.albertadistillers.com/sustainability/our-distillery`
- Heaven Hill editorial, 13 Aug 2019: ~340,000 barrels in three Black Velvet warehouses,
  Lethbridge: `https://heavenhill.com/news-and-notes/what-is-black-velvet-canadian-whisky/`
- Statistics Canada Table 16-10-0091 (CANSIM 303-0019), stocks of liquor in distilleries
  and bond warehouse, monthly 1946–1996 (terminated), CRA administrative data:
  `https://open.canada.ca/data/en/dataset/6198e838-b634-4aee-8fe8-ac929bd6200f`
- StatCan Daily, Control and sale of alcoholic beverages FY2023/24, spirits 184.9m litres:
  `https://www150.statcan.gc.ca/n1/daily-quotidien/250307/dq250307b-eng.htm`
- Beverage Information Group: US Canadian whisky 17.4m 9L cases 2022, −3.1% 2023:
  `https://bevinfogroup.com/2024/03/28/canadian-whisky-trends-2024-sales-brands-whiskey/`
- Forbes, Feb 2021: 18.69m 9L cases exported to the US in 2020:
  `https://www.forbes.com/sites/joemicallef/2021/02/20/there-is-a-lot-more-to-canadian-whisky-then-you-realized/`
- Trade Commissioner Service: US takes ~90% of Canadian beverage-alcohol exports:
  `https://www.tradecommissioner.gc.ca/en/market-industry-info/search-industry/alcoholic-beverages.html`
- Corby history and ownership: `https://corby.ca/en/about-corby/history/`
- Diageo confirms Valleyfield distills, barrel-ages and bottles Crown Royal; no stock count:
  `https://www.diageo.com/en/news-and-media/press-releases/2021/diageo-s-valleyfield-distillery-to-become-carbon-neutral-by-2025`
- Spirits Canada, national association and members: `https://spiritscanada.ca/`
- Canadian three-year legal rule: `https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.%2C_c._870/section-B.02.023.html`

## India
- Indian Malt Whisky Association, stat tiles ("300000+ Barrels", "20+" distilleries,
  "15+" million litres/yr capacity — label gives no scope), member list and voluntary
  definition: `https://indianmaltwhisky.org/`
- IMWA incorporation (8 Jul 2024) and public launch (20 Mar 2025):
  `https://www.just-drinks.com/news/indian-malt-whisky-trade-body/` and
  `https://theprint.in/ani-press-releases/indian-malt-whisky-association-imwa-formed-to-redefine-indias-global-standing-in-premium-malt-whiskies/2557167/`
- Piccadily Agro Q4 FY26 (board 28 Apr 2026): "holds approximately 85,000 barrels",
  83,800 barrels procured in FY26, capacity 45,000→100,000 by Mar 2027, malt 12→30 KLPD:
  `https://scanx.trade/stock-market-news/companies/piccadily-agro-industries-reports-record-inr1-143-crores-revenue-in-fy26-targets-60-70-growth/39248202`
- Piccadily Agro Investor Presentation 2024: "45,000+ Barrels with holding capacity of
  10+ Mn liters of spirit" — capacity phrased as a barrels tile:
  `https://www.picagro.com/themes/custom/investor/images/Investor%20Presentation%202024.pdf`
- Radico Khaitan, Rampur malt maturation facility capacity 2.6m litres per annum:
  `https://radicokhaitan.com/key-verticals/manufacturing/rampur-distillery/`
- Paul John: "up to 30,000 casks... in five warehouses" + ~3,500 underground; 8%/yr
  angel's share in Goa (Whisky Advocate, 17 Nov 2025):
  `https://whiskyadvocate.com/paul-john-indian-single-malt-whisky-explained`
- Paul John capacity doubled 1.5m→3m litres of alcohol/yr (Aug 2024):
  `https://www.thedrinksbusiness.com/2024/08/paul-john-doubles-indian-whisky-production/`
- Amrut capacity 0.9m→~1.4m litres/yr from Apr 2025 (Ambrosia):
  `https://www.ambrosiaindia.com/2025/04/amrut-distilleries-expanding-capacity-and-eyeing-partnership/`
- CIABC single-malt volumes: 345k Indian-origin cases 2023 (53% of ~675k), 500k in 2025:
  `https://www.business-standard.com/amp/industry/news/indian-single-malts-beat-global-brands-capture-53-sales-in-2023-report-124010800414_1.html` and
  `https://www.business-standard.com/industry/news/indian-single-malt-sales-hit-500k-in-2025-local-firms-dominate-ciabc-126072600137_1.html`
- FSSAI Alcoholic Beverages Regulations, Version V, current broad whisky and "matured"
  rules: `https://fssai.gov.in/upload/uploadfiles/files/Comp_Alcoholic_Beverages_V_04_12_2025.pdf`
- The Whiskey Wash, Indian whisky overview:
  `https://thewhiskeywash.com/world/everything-you-wanted-to-know-about-indian-whisky/`
- Brand composition: Wikipedia entries for Royal Stag, Imperial Blue, McDowell's No.1
- USDA FAS, India grain-based ethanol shift:
  `https://www.fas.usda.gov/data/india-india-accelerates-initiatives-enhance-grain-based-ethanol-production`
- Case volumes: The Spirits Business Brand Champions 2024, via ranked infographic
  (2023 data period)

## China
- China Alcoholic Drinks Association Whisky Committee 2023 survey as reported at its
  March 2024 release: 42 entities including two Taiwan, 26 operating, 450,000 oak casks and
  60,000-65,000 kL barrel-aged stock:
  `https://finance.sina.com.cn/wm/2024-03-27/doc-inaptzhm9531316.shtml`
- Bairun 2025 annual report filed with Shenzhen Stock Exchange: Laizhou nearly 600,000
  filled maturation casks at year-end; one million is management capacity:
  `https://disc.static.szse.cn/disc/disk03/finalpage/2026-04-29/d2a6a20d-faa4-43eb-b652-417f8d039339.PDF`
- China Daily / ECNS, May 2025: Laizhou over 400,000 then and roughly 80% of production and
  oak-barrel supply; Panda Brew nearly 2,000:
  `https://www.ecns.cn/m/business/2025-05-07/detail-iherfyrs7206861.shtml`
- Qiandao Jinjiu, first cask January 2025 and more than 200 by October; capacity kept
  separate: `https://insidethecask.com/2025/10/05/guest-blog-a-new-chapter-of-chinese-whisky-begins-at-qiandao-jinjiu/`
- Supplied-map source, Oak & Barley, May 2022:
  `https://oakandbarley.cn/wp-content/uploads/2022/05/Oak-and-Barley-Map-of-Chinese-Whisky-Distilleries-May-2022.pdf`
- Current Chinese standard status, GB/T 11856.1-2025:
  `https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=5A02AEC4C8449B456C4FAC80654DB23E`
- Diageo YunTuo opening: `https://www.diageo.com/en/news-and-media/press-releases/2024/diageo-unveils-the-yuntuo-single-malt-whisky-distillery-in-china`
- Pernod Ricard The Chuan opening: `https://www.pernod-ricard-china.com/en/media-content.html?id=1641972668269`
- Daiking Louis official site: `https://daikingwhiskies.com/`

## Australia and Japan
- Lark Distilling 2025 Annual Report, 2.5m litres under maturation at 30 June 2025:
  `https://announcements.asx.com.au/asxpdf/20250821/pdf/06n42j4mfplv73.pdf`
- Australian Distillers Association: `https://www.australiandistillers.org.au/`
- Australian two-year excise definition:
  `https://www.ato.gov.au/api/public/content/0-409f844f-0db1-4ec6-8b23-f87b6b696f1a`
- Japan Spirits & Liqueurs Makers Association official voluntary standard:
  `https://www.yoshu.or.jp/files/libs/552/202303291555304944.pdf`
- Japanese Whisky International Council, an expert/cultural body rather than a national
  stock publisher: `https://jwic-in.org/en/`
- NTA 酒のしおり 2025 edition (index of all statistical tables):
  `https://www.nta.go.jp/taxes/sake/shiori-gaikyo/shiori/2025/index.htm`
- NTA whisky production series 1970–2023 (製成数量の推移, 40% abv equivalent):
  `https://www.nta.go.jp/taxes/sake/shiori-gaikyo/shiori/2025/excel/0012-1.xls`
- NTA whisky domestic taxable removals 1970–2023 (課税数量の推移・国税局分):
  `https://www.nta.go.jp/taxes/sake/shiori-gaikyo/shiori/2025/excel/0013-3.xls`
- NTA Annual Statistics Report FY2024, production + volume-on-hand table (8-3), the
  table that proves 手持数量 excludes the maturing warehouse:
  `https://www.nta.go.jp/publication/statistics/kokuzeicho/sake2024/xls/08_suryo.xlsx`
- NTA Annual Statistics Report FY2024, liquor-tax overview table (8-1):
  `https://www.nta.go.jp/publication/statistics/kokuzeicho/sake2024/xls/08_sokatsu_kazeijokyo.xlsx`
- Ōmi Aging Cellar ~600,000 stored casks, Japanese whisky-trade blog:
  `https://sakedori.com/s/whiskycat1494/blog/75462.html`
- Nikkei, Suntory ¥6bn Ōmi warehouse expansion (2019; further coverage 2015, 2020):
  `https://www.nikkei.com/article/DGXMZO48216770V00C19A8TJ2000/`
- WhiskyInvestDirect, bulk Scotch flows to Japan off SWA data (March 2020):
  `https://www.whiskyinvestdirect.com/whisky-news/scotch-whisky-japan-070320201`
- The Spirits Business, Suntory scraps Kingswell (East Ayrshire) 500,000-barrel
  maturation site — the figure previously misattributed to Japan:
  `https://www.thespiritsbusiness.com/2026/03/suntory-scraps-plans-for-150m-whisky-site/`
- Nomunication Japanese Alcohol Data Library (JSLMA taxed volumes, licensing series):
  `https://www.nomunication.jp/data/`

## GI and category boundaries
- Scotch Whisky registered GI and technical file:
  `https://www.gov.uk/protected-food-drink-names/scotch-whisky`
- Irish spirit GIs, technical file and verified-operator register:
  `https://www.gov.ie/en/department-of-agriculture-food-and-the-marine/publications/geographical-indications-spirit-drinks/`
- EU Regulation 2019/787, general three-year / 700L whisky definition:
  `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0787`
- US TTB distilled-spirits FAQ: `https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/distilled-spirits-faqs`
- Welsh registered GI: `https://www.gov.uk/protected-food-drink-names/single-malt-welsh-whisky`
- English Whisky GI application, still in consultation:
  `https://www.gov.uk/guidance/protected-spirit-drinks-names-applications`
- Taiwan age/GI labelling rules: `https://www.nta.gov.tw/Eng/singlehtml/2736`
- South African annotated Liquor Products regulations:
  `https://www.nda.gov.za/images/Branches/AgricProducHealthFoodSafety/food-safety-and-quality-assurance/liquor-products/guideline-documents/regulations_annotated.pdf`

## Writers, scholarship, schools and historical records
- Fionnán O'Connor, one-page TU Dublin project synopsis supplied by John:
  `https://www.tudublin.ie/media/website/explore/schools/culinary-arts-and-food-technology/documents/Fionn%C3%83n-O'Connor.pdf`
- Completed 2025 PhD record and abstract, DOI 10.21427/btvb-z470:
  `https://arrow.tudublin.ie/tfschcafdoc/7/`
- Heriot-Watt International Centre for Brewing and Distilling research:
  `https://icbd.site.hw.ac.uk/research/`
- Scotch Whisky Research Institute: `https://www.swri.co.uk/`
- Teagasc / TU Dublin whiskey-flavour and GI-authentication research:
  `https://teagasc.ie/about/research--innovation/research-publications/tresearch-articles/fundamentals-of-whiskey-flavour-php/`
- Michael Connolly, *The Diverging Paths of the Irish and Scotch Whiskey Industries from
  the Act of Union to Irish Independence*, Business and Industrial History 34 (2025):
  `https://journals.gla.ac.uk/bih/article/download/599/261/1812`
- Spirits Act 1880, warehoused-cask marking requirements:
  `https://www.irishstatutebook.ie/eli/1880/act/24/enacted/en/print.html`
- Edward B. McGuire, *Irish Whiskey: A History of Distilling, the Spirit Trade, and Excise
  Controls in Ireland*, National Library of Ireland catalogue:
  `https://catalogue.nli.ie/Record/vtls000120010`

## Market reports, cask intermediaries and digital datasets
- KPMG Ireland, *Understanding the Whiskey Market*: disclosed use of Whiskey & Wealth Club
  data and cask-investment risk: `https://assets.kpmg.com/content/dam/kpmg/ie/pdf/2024/08/ie-understanding-the-whiskey-market-2.pdf`
- Whiskystats data API: `https://www.whiskystats.com/whisky-data-api`
- WHISKY:EDITION developer API: `https://thewhiskyedition.com/developer`
- WhiskeyProject recommendation API: `https://github.com/WhiskeyProject/whiskey-api`
- Whisky Hunter auction-data index: `https://github.com/api-evangelist/whisky-hunter`
- Wikipedia's whisky-production references were used as a discovery queue, not as terminal
  evidence: `https://en.wikipedia.org/wiki/Whisky#Production`

## Future direct-survey feasibility
- Guinndex primary project account: 3,000+ pub calls, 2,052 answered and 1,000+ verified
  prices: `https://guinndex.ai/press`
- ElevenLabs batch-calling documentation:
  `https://elevenlabs.io/docs/eleven-agents/phone-numbers/batch-calls`
- ElevenLabs AI and recording disclosure requirements:
  `https://elevenlabs.io/docs/eleven-agents/legal/disclosure-requirement`
- European Commission, AI Act interaction-transparency obligations applying from 2 August
  2026: `https://digital-strategy.ec.europa.eu/en/news/commission-publishes-guidelines-transparency-obligations-providers-and-deployers-certain-ai-systems`
- US FCC ruling treating AI-generated voices as artificial or prerecorded voices under the
  TCPA: `https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf`
- UK ICO distinction between genuine market research and direct marketing:
  `https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/direct-marketing-guidance/identify-direct-marketing/`

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
- [ ] **Future Dark-region sprint — pause here for now.** Go one level deeper on the four
      remaining regions with no published stock anchor: **Japan, continental Europe,
      Taiwan and Rest of world**. For Japan, review producer sustainability reports,
      planning documents and anniversary material from Suntory, Nikka, Kirin and
      Chichibu, then ask JSLMA/JWIC directly. For continental Europe, work country by
      country through national associations, GI registers and leading producers rather
      than applying one regional multiplier. For Taiwan, seek filled-cask disclosures
      from King Car/Kavalan and TTL/Nantou and keep capacity separate from inventory. For
      Rest of world, begin with Africa outside South Africa and Latin America, record the
      coverage boundary explicitly and resist turning unmapped production into zero.
      Every result must preserve the same date, unit, scope, provenance and duplicate-
      control fields used elsewhere in this document; do not extrapolate from capacity.
- [ ] Canada. Ask Spirits Canada and Davin de Kergommeaux to validate the 3.9m published
      floor (Part 4F), re-date the 2016–2019 Hiram Walker and Black Velvet figures, and
      estimate current filled stock at Valleyfield, Canadian Mist/Collingwood, Old
      Montreal and the independent long tail. Ask whether any successor to StatCan's
      terminated bonded-stock series (16-10-0091) exists inside CRA.
- [ ] China. Obtain the CADA 2023 report itself and request its next survey, scope rules
      and duplicate controls. Reconcile the nearly 600k Laizhou filing with CADA's 450k
      national 2023 count before treating 0.75m as anything stronger than Producer.
- [ ] Ireland history. Obtain the full O'Connor thesis or contact the author; use his
      excise-report and distillery-day-book citations to extend the historical stock series.
- [ ] Expert review. Ask SWRI, Heriot-Watt ICBD and Teagasc/TU Dublin for a method review,
      not unpublished commercial stock. Ask Gary Quinn, Fionnán O'Connor and other writers
      for primary-source leads, not estimates from memory.
- [ ] Association sweep. Contact the associations already checked—SWA, Drinks Ireland/IWA,
      DISCUS/KDA, Spirits Canada, JSLMA, CADA, IMWA, Australian Distillers, English Whisky
      Guild, Fédération du Whisky de France and Nordic Whisky Collaboration—and record
      explicit "no national stock series" responses where applicable.
- [ ] Public data. Keep the evidence ledger in this repository first. A separate public
      GitHub dataset becomes useful only after each row has machine-readable scope, date,
      unit, source URL, confidence and duplicate key; publishing a second half-structured
      repository now would create another source of drift.

## Future process map: Global Whisky Inventory Census

**Design only; paused.** Do not enrich telephone numbers, configure an agent or initiate
calls until the target territories, legal basis, privacy notice, budget and pilot are
explicitly approved. As of 2026-08-02, Distillery Map contains 6,197 locations, 5,690
website fields and no telephone-number field.

```text
6,197 mapped locations
        ↓
Classify likely whisky producers and resolve duplicate/closed locations
        ↓
Enrich and verify public business contacts, with source and checked date
        ↓
Pass a country-level legal, AI-disclosure, recording and calling-hours gate
        ↓
Run a disclosed 100-location validation pilot against some known inventories
        ↓
Ask the structured census questions and send an email verification link
        ↓
Human-review transcripts, outliers, units, ownership and parent-company duplicates
        ↓
Grade verified responses as Producer evidence; model non-response, never as zero
        ↓
Publish aggregate totals, coverage and methodology; schedule dated refresh batches
```

The opening must identify Distillery Map, the non-commercial research purpose and the
caller as an AI system, disclose recording/vendor processing where applicable, and offer
an immediate opt-out. Do not impersonate a customer or use research to promote LYQD or
another product. Association endorsement or an advance opt-in email is preferable where
available.

The shortest useful questionnaire is:

1. Is this location currently filling whisky or whiskey into wood?
2. How many **filled whisky casks are physically maturing now**, as of what date? Accept
   an exact figure or a clearly defined band; record cask/barrel size or unit.
3. Does the answer include third-party/customer-owned stock, stock held elsewhere, or
   spirits other than whisky? Capacity and planned production are excluded.
4. Which producer group and warehouse locations does the number cover, so the same casks
   are not counted again?
5. May Distillery Map publish the exact figure, the band, or only an aggregated response,
   and who can verify it by email?

Pilot review should measure contact accuracy, answer and completion rates, respondent
understanding, extraction accuracy, verification rate and disagreement with known public
figures. A broad rollout should proceed country by country, with native-speaker review and
association introductions. Every high-value response and every extreme outlier requires
human confirmation. A refusal or unanswered call is missing evidence, not evidence of no
stock.

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
| 2026-08-02 | India standing stock, second correction | 0.9m, range 0.4 to 2m | 0.5m, range 0.3 to 0.9m | IMWA publishes a 300,000+ barrel floor; association evidence is stronger than the earlier sales model |
| 2026-08-02 | India legal boundary | "no compulsory definition or maturation rule" | broad FSSAI definition; one year if "matured" is claimed; stricter IMWA rule voluntary | The earlier statement confused a broad rule with no rule |
| 2026-08-02 | Canada standing stock | 3m, range 2 to 4.5m | 4.5m, range 3.1 to 5.5m | Crown Royal 1.5m plus public Hiram Walker 1.6m establishes a 3.1m floor before other producers |
| 2026-08-02 | China | inside 0.15m Rest of world allowance | separate 0.75m, range 0.6 to 1m | Bairun filed nearly 600,000 filled casks; 2022 map could not reveal the subsequent build |
| 2026-08-02 | Australia | 0.06m, range 0.04 to 0.1m | 0.1m, range 0.04 to 0.2m | Updated Lark disclosure to 2.5m litres and widened fragmented-industry allowance |
| 2026-08-02 | Operator count caveat | undercount only | 6,197 mapped; 2,000+ whiskey is estimated | Dataset has no spirit-category field. Jurisdiction proxy 2,616; keyword floor 200 |
| 2026-08-02 | Tasmania | 26,000 barrel equivalents | ~12,000 at 200L | Source conversion does not reproduce |
| 2026-08-09 | Japan standing stock | 1.5m, range 0.8 to 2.5m, dark | 2.3m, range 1.3 to 4m, producer | Withdrawal-times-residence model on NTA throughput aggregates, reconciled with Ōmi ~600k stored casks. Full derivation in Part 4E |
| 2026-08-09 | Japan caveat, Suntory "abandoned 500,000-barrel maturation site" | implied Japanese stock | removed | The scrapped 2026 site was Kingswell, East Ayrshire, Scotland — Scotch maturation, and capacity not filled stock. Never part of Japan's inventory |
| 2026-08-09 | Global totals | 59.7m, scenarios 53.4 to 66.5 | 60.5m, scenarios 53.9 to 68.0 | Mechanical consequence of the Japan re-derivation |
| 2026-08-09 | Canada standing stock | 4.5m, range 3.1 to 5.5m | 4.3m, range 3.9 to 5.2m | Published floor rises to 3.9m on Alberta Distillers 447k (company page) and Black Velvet ~340k (Heaven Hill, 2019); withdrawal-times-residence model centres at 3.2m and caps the high; StatCan's terminated 1946–1996 bonded-stock series added as historical anchor. Full derivation in Part 4F |
| 2026-08-09 | Global totals | 60.5m, scenarios 53.9 to 68.0 | 60.3m, scenarios 54.7 to 67.7 | Mechanical consequence of the Canada re-derivation |
| 2026-08-09 | India basis | IMWA "300,000+ barrels" read as a published stock floor | 0.5m, 0.3–0.9m unchanged; floor re-based on Piccadily Agro ~85k held barrels (listed-company disclosure, Apr 2026) plus Paul John ~33.5k (trade, Nov 2025); IMWA tile flagged as scope-ambiguous — its flagship member uses the same "Barrels" tile convention for warehouse capacity | Full derivation in Part 4G. Totals unmoved |
| 2026-08-09 | Continental Europe | 0.3m, range 0.2 to 0.5m, dark | 0.4m, range 0.25 to 0.55m, producer | DYC's Segovia plant trade-reported at 170,000 aging casks (Alimarket, 2019) was missing entirely; High Coast publishes 20,000+ casks (Apr 2026), St. Kilian ~10,500 counted; France re-derived from the INAO's official flow series. Full derivation in Part 4H |
| 2026-08-09 | Taiwan | 0.15m, range 0.1 to 0.3m, "inferred from warehouse footprint" | 0.15m, range 0.1 to 0.25m, dark, withdrawal-times-residence model | Model on Kavalan's 10m+ bottles/yr at 4–6 years' subtropical residence centres at ~144k national; 300k capacity cross-checked, never counted. High trimmed — capacity-full was never plausible. Part 4H |
| 2026-08-09 | South Africa asOf | 2018, single source | 2018 count corroborated by post-2023 Heineken Beverages-era profile (seven warehouses, >150,000 casks); number and grade unchanged | Neither source is company-published; recycled talking-point risk flagged. Part 4H |
| 2026-08-09 | Global totals | 60.3m, scenarios 54.7 to 67.7 | 60.4m, scenarios 54.7 to 67.7 | Mechanical consequence of the Europe re-derivation |
| 2026-08-10 | Ireland basis | 4.5m, 4–5m, estimate, resting solely on the LYQD commissioned study | Numbers and tier unchanged; now corroborated by two independent lines — Drinks Ireland's published >3.1m casks maturing (2020) rolled forward to ~4.1m on flow arithmetic, and a new producer bottom-up (Irish Distillers 1.7m, GND 500k, Bushmills >500k, Waterford >70k = 2.77m published floor, bracketing 3.8–4.2m). Both centre slightly below 4.5m; residual risk is downward. sourceUrl added. Part 3's "no company-level split exists" corrected | Full derivation in Part 4I. Totals unmoved |

---

# Part 10. How this was produced, and how to rerun it

Written so the exercise can be repeated rather than reconstructed. The figures below will
move. The method should not.

## Starting inputs

The first pass came from a Manus wide-research run, delivered as files in `~/Downloads/`:

- `Global Whiskey Aging Inventory Estimates (2024-2026).md` — the headline estimates
- `Whiskey Aging Inventory_ Disclosure-Source Map and Evidence Rules.md` — **the most
  valuable of the set.** The evidence-tier framework came from here and was kept
- `Entity Cards - Whiskey Maturing-Inventory Disclosure Screen.md` — corporate disclosure screen
- `research_whiskey_aging_inventory.csv` — per-country findings with confidence grades
- `research_whiskey_inventory_disclosures.csv` — Diageo, Pernod, Brown-Forman, Suntory
- `kentucky_bourbon_cycle_data.csv` — KDA stock-vs-flow series 2020 to 2024
- `distillery_pause_registry.csv`, `The Whiskey Correction_....txt` — pause/correction narrative
- `Review of LYQD Irish Whiskey Supply Report 2026 (1).md` — supplied later, during the
  Ireland cross-check
- Two rendered images: a Kentucky stock-vs-flow chart, and a first-cut world map

**If rerunning:** the tier framework and the corporate disclosure screen are reusable as-is.
The rendered map was not, for the reasons in Part 6.

## What the first pass got wrong, as a checklist

Every one of these is a generic failure mode, not a one-off. Check each on any rerun.

1. **A state quoted as a country.** Kentucky's 17.1m presented as "USA". Also counted all
   spirits, not just whiskey
2. **Mixed units on one visual.** Casks, barrels and litres plotted as if comparable
3. **A conversion that does not reproduce.** Tasmania's "26,000 barrel equivalents" from
   2.4m litres. Correct figure is ~12,000 at 200L. Always re-run the arithmetic yourself
4. **Markers not scaled.** 22m and 50k drawn the same size
5. **Capacity treated as inventory.** Kavalan's 300,000 barrels
6. **No total.** The single thing the exercise was for
7. **A weak source dressed as evidence.** The Tasmania figure traced to a Facebook post

## Method that worked

1. **Read every supplied file before building anything.** The tier framework was buried in
   the file that looked least like data
2. **Find the missing aggregate.** The largest gap was the US national figure. One web
   search on DISCUS inventory found 1.5bn proof gallons, which reshaped the whole map
3. **Convert only with the arithmetic shown**, and state the band rather than a point
4. **Test every headline figure against a second, independent quantity.** Ireland's 4.5m was
   tested against capacity (140 MLPA) and against published case volumes. Both agreed.
   The 16m failed both. This step is what caught the error
5. **Grade every figure and publish the grade.** The gaps became the reason for the post
6. **Build the map from data already in the repo.** `scripts/build-world-svg.mjs` bakes
   Natural Earth boundaries into inline SVG. No new dependency, no Mapbox call
7. **Look at the render.** Four defects were invisible in code and obvious on screen:
   clipped label, off-canvas label, colliding labels, dead ocean

## Searches that produced the key figures

- `DISCUS American whiskey inventory "proof gallons" record 2024 aging warehouses billion`
  gave the 1.5bn proof gallons and the 58m/45m sales-and-export split behind the 14.6 years
- `Indian whisky molasses extra neutral alcohol ENA definition not grain EU whisky standard`
  exposed the blend-composition issue, but initially led to the wrong claim that India had
  no compulsory definition. The later FSSAI check corrected it
- `"Royal Stag" OR "Imperial Blue" OR "McDowell's No 1" whisky made from grain spirit or
  molasses ENA blended Scotch malt` produced the brand-level composition that refuted the
  molasses claim
- `India ENA shift molasses to grain based alcohol ethanol blending programme` gave the
  feedstock shift context
- `Indian Malt Whisky Association barrels distilleries capacity` found the 300,000+ barrel
  floor and replaced the sales-derived 0.9m central estimate
- `Hiram Walker 1.6 million barrels Pike Creek` established that the remembered Canadian
  number was public and independently repeated
- Chinese-language searches for `2023中国威士忌行业发展调研报告 橡木桶保有量` and
  `百润股份 2025 年年度报告 六十万只 陈酿桶` found CADA's 2023 national benchmark
  and Laizhou's exchange-filed 2025 filled-cask disclosure
- `Stocks in Bonded Warehouses Ireland Scotland ratio annual production 1870 1922` found
  the Inland Revenue / Customs & Excise reconstruction behind the historical correction cycle

A search for TTB storage reports did **not** produce a usable national figure. DISCUS did.

## The challenge sequence, and what each one changed

John pushed back four times. Three of the four found something real. Recording them because
the pattern is the useful part: **every challenge that cited a specific external fact was
right, and the one that was a placement judgement was also right.**

| Challenge | Outcome |
|---|---|
| "I wanted a global number, not the correction story" | Reframed from narrative to a single defensible total with a range. Correct |
| "Your Indian numbers concerned me" + top-20 sales data | India raised 0.4m to 0.9m, range widened to 0.4-2m. The first pass had not accounted for 141m cases a year. Correct |
| "I find the molasses claim hard to believe" | Claim was out of date and partly wrong. Top three brands use grain spirit. Estimate held; the reasoning was rebuilt on neutral spirit not being cask-matured. Correct |
| "Why Stillbound, it was part of DistilleryMap" | Evidence base had been filed in the wrong repo. Moved here, slide subset left there. Correct |
| "Look at ALL official associations" | Found IMWA's 300,000+ India floor, Spirits Canada's source gap and CADA's 450,000 China benchmark. India moved down and China moved out of Rest of world. Correct |
| "Does Corby/Pernod speak to Canadian whisky?" | Hiram Walker's 1.6m is public. Canada gained a 3.1m published floor and a 4.5m central estimate. Correct |
| "Go through" the China map | The map proved to be a 2022 lead list, not a count. Audit separated Taiwan, plans and false positives; Bairun's later 600k filing became the anchor. Correct |
| Writers, schools and GI sources | Added a source-role hierarchy. They improve scope, history and expert validation but are not silently converted into casks. Correct |

**Lesson for the rerun:** when a figure is challenged, separate the *number* from the
*reason for it*. Twice the number survived and the reason did not. Defending the reason
because the number was right is the trap.

## Regenerating the outputs

```bash
node scripts/build-world-svg.mjs   # only if boundaries or projection change
npm run build                      # validate; no test suite in this repo
npm run dev                        # then, with a server up:
npm run share-card                 # writes public/share/whiskey-aging-inventory-1200.png
```

The share card renders `/whiskey-aging-inventory/share-card` through headless Chrome at 2x.
It is noindex and excluded from the sitemap. Change figures in `src/lib/aging-inventory.ts`
and every output follows: page, map, stat tiles, share card, and the page description.

## What to re-check on any rerun

Ordered by how likely it is to have moved.

1. **KDA annual report.** Kentucky inventory and production. Published early each year
2. **DISCUS inventory.** The US national figure, and the sales/export denominator behind
   the years-of-supply number. The correction was under way in 2025 to 2026, so this is
   the fastest-moving figure in the set
3. **SWA Facts and Figures.** Scotland has been stable at ~22m but confirm the vintage
4. **LYQD.** Whether a later Irish supply report exists, and whether the full 2026 report
   is obtainable. No longer the only Irish line (Part 4I: Drinks Ireland 2020 anchor +
   producer bottom-up), but still the only census-style attempt. Also re-check whether
   Irish Distillers has published a post-2021 cask count — the 1.7m-vs-2m+ question is
   the biggest swing in the Irish bottom-up
5. **Bairun and CADA.** Laizhou's annual filing moves quickly; compare it with the next
   national association survey and do not add them
6. **India.** Re-based 9 Aug 2026 (Part 4G): the floor is now Piccadily's listed-company
   ~85k held barrels plus Paul John's trade-reported ~33.5k. Re-check Piccadily's next
   earnings call (barrel count moves ~15k/yr) and whether the "holds" figure means
   filled. Still ask IMWA whether "300000+ Barrels" is stock or capacity, member or
   national — the tile answers none of it
7. **English Whisky Guild.** Fastest-growing category on the map from a tiny base
8. **Japan.** Re-derived 9 Aug 2026 (Part 4E): NTA throughput model plus the Ōmi anchor,
   now producer grade. The remaining gap is structural — new-make laydown is published
   nowhere, and the filler-spirit share is the load-bearing assumption. A Suntory, Nikka
   or JSLMA stock disclosure would still be the single biggest improvement available
9. **The distillery count.** Re-derive from the geojson. Never carry the previous number
