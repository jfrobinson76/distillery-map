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

Best estimate: **60.5 million casks and barrels**, presented publicly as approximately 60
million. Source-bounded scenarios run from 53.9 to 68.0 million, rounded publicly to 54 to
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
| Ireland | 4.5m | 4 to 5m | Estimate | LYQD Irish Whiskey Supply Report 2026 |
| Canada | 4.5m | 3.1 to 5.5m | Producer | Crown Royal; Hiram Walker/Pike Creek |
| Japan | 2.3m | 1.3 to 4m | Producer | NTA throughput model; Ōmi cellar ~600k casks (Part 4E) |
| China | 0.75m | 0.6 to 1m | Producer | Bairun 2025 AR; CADA 2023 survey |
| India | 0.5m | 0.3 to 0.9m | Producer | Indian Malt Whisky Association |
| Continental Europe | 0.3m | 0.2 to 0.5m | Dark | None published |
| Taiwan | 0.15m | 0.1 to 0.3m | Dark | None published |
| South Africa | 0.15m | 0.1 to 0.2m | Producer | James Sedgwick, 2018 trade reporting |
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

**US years of supply, 14.6.** Same DISCUS release: 1.5bn proof gallons of stock against
58m domestic sales plus 45m exports = 103m proof gallons a year. 1,500 / 103 = 14.6 years.
This is arithmetic on their own published figures, not our modelling.

**Bottle equivalent, ~27bn.** 59.7m casks at a deliberately conservative 450 bottles each.
The SWA's own ratio (22m casks = 12bn bottles) implies 545; we blended that down against
smaller US barrel yields. Illustration only.

**Lower scenario, 53.9m.** This is 23 US + 21 Scotland + 4 Ireland + 3.1 Canada +
1.3 Japan + 0.6 China + 0.3 India + 0.2 continental Europe + 0.1 Taiwan + 0.1 South
Africa + 0.04 Australia + 0.05 England and Wales + 0.1 rest of world = **53.89m**.
Relative to the 60.45m central sum, 2m comes from the US proof-gallon conversion, 1.4m
from using only Canada's published floor, 1m from SWA's rounded "some 22m", 1m from
Japan and 0.5m from Ireland. All other downward allowances together are about 0.7m. It is
a conservative simultaneous-low case, not a claim that each downside is correlated.

**Canada, 4.5m barrels.** The published floor is Crown Royal/Gimli at 1.5m plus Hiram
Walker/Pike Creek at more than 1.6m = **3.1m**. The Hiram Walker number is public, not an
internal figure: a 2017 distillery visit recorded 1.6m across 16 warehouses, and a later
profile of brand ambassador Dave Mitton states that the site ages more than 1.6m "at any
given time." Central 4.5m adds 1.4m for Diageo's Valleyfield site, Alberta Distillers and
the smaller producers. Range 3.1m, the hard floor, to 5.5m. Quoted Valleyfield and Alberta
warehouse capacities only bound that allowance; they are not counted as filled stock.

**China, 0.75m casks.** Bairun's exchange-filed 2025 annual report says Laizhou had filled
nearly 600,000 maturation casks at year-end. China Daily reported Laizhou at roughly 80%
of domestic whisky production and oak-barrel supply. 0.6m / 0.80 = **0.75m**. Range 0.6m,
the filed producer floor, to 1m. This is deliberately not the sum of every map marker.

**India, 0.5m barrels.** IMWA publishes **300,000+ barrels**, 20+ distilleries and 15m
litres a year of capacity. Its named members account for more than 75% of Indian
malt-whisky revenue, but IMWA does not say whether the barrel figure is member stock or a
national malt total. Central 0.5m treats 0.3m as a floor and adds 0.2m for non-members and
other domestically matured whisky. Range 0.3m to 0.9m. Revenue share is not barrel share.

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
- Corby history and ownership: `https://corby.ca/en/about-corby/history/`
- Diageo confirms Valleyfield distills, barrel-ages and bottles Crown Royal; no stock count:
  `https://www.diageo.com/en/news-and-media/press-releases/2021/diageo-s-valleyfield-distillery-to-become-carbon-neutral-by-2025`
- Spirits Canada, national association and members: `https://spiritscanada.ca/`
- Canadian three-year legal rule: `https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.%2C_c._870/section-B.02.023.html`

## India
- Indian Malt Whisky Association, 300,000+ barrels, 20+ distilleries, 15m-LPA capacity,
  member list and voluntary definition: `https://indianmaltwhisky.org/`
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
- [ ] Canada. Ask Spirits Canada and Davin de Kergommeaux to validate the 3.1m published
      floor and estimate current filled stock at Valleyfield, Alberta Distillers, Black
      Velvet/Lethbridge and the independent long tail.
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
   is obtainable. Still the only Irish number available
5. **Bairun and CADA.** Laizhou's annual filing moves quickly; compare it with the next
   national association survey and do not add them
6. **IMWA.** Clarify whether 300,000+ covers members or the whole Indian malt category
7. **English Whisky Guild.** Fastest-growing category on the map from a tiny base
8. **Japan.** Re-derived 9 Aug 2026 (Part 4E): NTA throughput model plus the Ōmi anchor,
   now producer grade. The remaining gap is structural — new-make laydown is published
   nowhere, and the filler-spirit share is the load-bearing assumption. A Suntory, Nikka
   or JSLMA stock disclosure would still be the single biggest improvement available
9. **The distillery count.** Re-derive from the geojson. Never carry the previous number
