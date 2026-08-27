# Irish coverage gap audit — findings and candidate queue

**Date:** 27 August 2026
**Brief:** `irish-gap-audit-brief-2026-08-27.md`
**Output:** a candidate queue for John to approve. `distilleries.geojson` is not
touched in this pass.

---

## Covering note

**Reference sources reconciled: four.** A fifth was attempted and is not publicly
available.

| Source | What it gave | Independent of the others? |
|---|---|---|
| Wikipedia, list of whiskey distilleries in Ireland | 47 operating, 22 closed | Cross-check only, per the brief |
| Irish Whiskey Magazine, `/listings` directory | 59 distilleries, incl. in-planning and under-construction | Yes — the widest net of the four |
| Irish Whiskey Way (the IWA's own `irishwhiskey360.com`, now redirected) | 28 visitor-open distilleries | Yes — but tourism-filtered, so it under-reports production sites |
| The Gin Guide, Irish directory | 16 tour-open gin distilleries + ~34 gin brands | Yes — and the only non-whiskey source |
| **Drinks Ireland / Irish Whiskey Association member list** | **nothing** | The IWA has 47 member companies but publishes no member directory. `ibec.ie/drinksireland/irish-whiskey` and its About page carry no list. Would need to be requested directly |

**Not attempted, and worth knowing:** Revenue's excise licence data and HMRC's
approved-warehousekeeper register. Both are public, and both are licence-holder
lists rather than distillery lists — they include retail and bonded-warehouse
licences, so they need heavy filtering before they say anything about stills.
They are the only sources that would give a genuinely complete denominator, and
they are the right next step if the queue below is judged too thin.

**Baseline.** 79 island-of-Ireland rows (64 `country: "Ireland"`, 15
`country: "United Kingdom"` inside an NI bounding box). That is post-PR #16,
which resolved the eight names in the brief's "confirmed absent" list — seven
added, and Teeling repaired rather than added, because it was already on the map
filed as `Jameson`. The brief's stated baseline of 72 was correct at the time it
was written.

**Raw gap.** The union of the four reference lists normalises to 68 names.
Twenty did not match the dataset on the first pass. Fourteen of those were
normalisation false positives, resolved by eye (below). **Six were genuinely
absent whiskey sites**, and the gin sweep found **two more**, for a raw gap of
**eight**.

**Of the eight: one is a recommended add, two need an owner's answer, and five
are rejected.** The gap is much smaller than the brief's eight-name probe
implied — but that is because the probe found the *operating* absences and this
sweep mostly found sites that do not exist yet.

**The honest headline: the Irish whiskey gap is now close to closed, and the gin
gap is unmeasured.** The Irish Gin Strategy 2022–2026 counts at least 37
distilleries on the island producing gin, around eight of them in Northern
Ireland. Three of our four sources are whiskey directories. A gin-first sweep is
the next real piece of work, not a bigger whiskey sweep.

---

## Candidate queue

| Name | Address | Lat | Lon | Website | Distils on site | Source URL | Confidence |
|---|---|---|---|---|---|---|---|
| Basalt Distillery | 14-16 Seneril Road, Bushmills, Co. Antrim, BT57 8TS | *unresolved* | *unresolved* | theginguide.com/basalt-distillery.html | **Y** — own iStill, established 2021 | https://www.theginguide.com/basalt-distillery.html ; https://find-and-update.company-information.service.gov.uk/company/NI672259 | **High** on the distillery, **low** on the pin — Nominatim cannot resolve Seneril Road or BT57 8TS. Needs a coordinate before it goes in |
| Glens of Antrim Distillery | 1 Gortaclee Road, Cushendall, Co. Antrim, BT44 0TE | 55.0756 | -6.0578 | glensofantrimdistillery.com | **Unknown** — sells Lír Irish Whiskey, but the site shows only marketing copy and no still | https://glensofantrimdistillery.com/ ; https://www.irishwhiskeymagazine.com/listings/distilleries/glens-of-antrim-distillery | **Medium.** Coordinates are street-level (Gortaclee Road), not door-level. IWM still says "will open in early 2023" |
| Frankie & Eileen's | Randalstown, Co. Antrim | *unresolved* | *unresolved* | — | **Unknown** — Gin Guide's Best in Ireland 2026, but describes a family "legacy of supplying brewing ingredients", which reads like a brand, not a still | https://www.theginguide.com/irish-gin.html | **Low.** Do not add without the producer confirming a still |

Three rows. That is the whole queue, and the shortness is the finding.

---

## Rejected, with reasons

**Pre-operational — planning permission, no still (4).** Irish Whiskey Magazine's
directory carries `in-planning` and `under-construction` as categories; our map
does not, so everything in those categories fails the "evidence of a still on
site" bar.

| Name | County | Status per source | Source |
|---|---|---|---|
| Curraghmore Distillery | Waterford | Planning permission granted to convert five 180-year-old farm buildings at Curraghmore Estate, Portlaw. "To be built" | irishwhiskeymagazine.com/listings/distilleries/curraghmore-distillery |
| Harvest Lodge Distillery | Dublin | Planning approved by Fingal County Council for Balbriggan. "Will be built". Brand: Scott's Irish Whiskey | irishwhiskeymagazine.com/listings/distilleries/harvest-lodge-distillery |
| Stewarts Mill Distillery | Roscommon | "Will be built" in Boyle | irishwhiskeymagazine.com/listings/distilleries/stewarts-mill-distillery |
| Gortinore Distillers & Co (Natterjack) | Waterford | Distillery "being built" in the ex-Flahavan's woollen mill on the River Mahon, "preparing to install 3 copper pot stills". The company's own site gives only **17 Dame Court, Dublin 2** — an office | natterjack.com ; irishwhiskeymagazine.com/listings/distilleries/gortinore-distillers-co |

**Unverifiable (1).** Irish Whitetail Distillery, Co. Donegal. IWM carries a
listing with no address and vague production language; `irishwhitetail.ie` does
not resolve. Nothing here can be traced to a source, so it does not go in the
queue.

**Already rejected in PR #16, restated so they are not re-probed (2).**
Killarney Brewing & Distilling — examinership failed July 2025, liquidator
appointed, operations ceased. Nephin — building finished 2018, no evidence
production ever began.

---

## Normalisation false positives, resolved by eye

The brief warned that name matching is the hard part. It was. Fourteen of the
twenty apparent misses were the same site under a different name, and an
automated diff would have queued every one of them as a new addition.

| Reference name | Actually in the dataset as | Why the match failed |
|---|---|---|
| Connacht Distillery | **Ballina Whiskey** | Renamed. Confirmed same site: both at Belleek, Ballina, Co. Mayo, F26 P932. The brief flagged this to confirm before adding either — confirmed, one site, no addition |
| Lough Gill | **Hawk's Rock Distillery** | Renamed April 2025, Sazerac-owned. Already carried in the description |
| Crolly | **Croithlí** | Irish-language name in the dataset, anglicised in the reference lists |
| McConnell's | **Belfast Distillery** | Trading name vs. company name. Aliased in PR #16 |
| Midleton | **Jameson Distillery Midleton** | Brand prefix |
| Old Bushmills | **Bushmills Distillery** | "Old" prefix |
| Tullamore | **Tullamore D.E.W. Distillery** | Brand suffix |
| Sliabh Liag | **Ardara Distillery** + **Sliabh Liag Distillers Bottling & Administration Centre** | Two pins, one operator. Already carries `operator: "Sliabh Liag Distillers"` |
| Blacks / Blacks of Kinsale | **Blacks Brewery & Distillery** | "Brewery" is not in the strip list, so normalisation kept it |
| Jameson Bow Street | **Jameson Distillery Bow St.** | Abbreviation |
| Killarney, Nephin | — | Genuinely absent, rejected on status rather than on name |
| Shortcross, An Dúlamán, Jawbox, Method & Madness, Minke, Drumshanbo, Xin | **Rademon Estate, Ardara, Echlinville, Midleton, Clonakilty, The Shed, Ahascragh** | Gin **brands** made at whiskey distilleries already on the map. No new pins |

The Walsh Whiskey / Royal Oak trap the brief called out did not fire: both are
already separate rows and neither normalises onto the other.

---

## Reverse check — what is in the dataset and should not be, or is wrong

**1. Daly's Distillery should come off the map.** This is the clearest finding of
the reverse pass.

- The dataset carries `Daly's Distillery`, `48 MacCurtain Street, Victorian
  Quarter, Cork, T23 F104`, `source: wikidata`.
- Daly's was a Cork Distilleries Company distillery that operated from about 1820
  and **ceased in 1869**. Wikipedia's closed list dates it 1807; either way it has
  not distilled in over 150 years.
- It was on John Street, not MacCurtain Street. So the pin is a defunct
  19th-century distillery at an address that was never its address, presented on a
  live tourism map as a working site.
- Source: https://en.wikipedia.org/wiki/Daly%27s_Distillery

**Recommendation: remove**, and log it in `pruned_non_distilleries.json` under the
existing pruning ledger.

**2. Two rows are not distilling sites and carry no `entity_role`.** Under the
convention, absence of the field asserts that spirits are distilled there. For
both of these, that assertion is false.

| Row | What it actually is | Proposed |
|---|---|---|
| `Irish Distillers Dungourney`, Ballynona North, Co. Cork | A maturation warehouse complex — eight warehouses at 16,800 casks each, €100m investment, first casks from Midleton in January 2014. No still | New value **`maturation_warehouse`**, plus `operator: "Irish Distillers"` |
| `Jameson Distillery Bow St.`, Dublin 7 | Visitor centre and museum. Has not distilled since 1971. The IWA's own directory lists it as "Jameson Experience Bow Street" | New value **`visitor_centre`**. `tasting_room` is the nearest existing value and is wrong — Bow St. is a full visitor experience, not a counter |

Both need a new `entity_role` value, which `entity-roles.md` says to add only when
none fits and to document in the same commit. **Neither is applied here** — the
brief says produce a candidate list, and adding a vocabulary value is a
convention change, not a data fix. Both are John's call.

Sources: https://www.nbco.localgov.ie/en/bcms/notice/dungourney-whiskey-maturation-warehouses-d125d126 ;
https://irishwhiskeyway.ie/distilleries/jameson-experience-bow-street/

**3. Waterford Distillery is correct and the cross-check source is stale.** Worth
recording because it is the reverse of what a reconciliation normally finds.
Wikipedia's closed list dates Waterford "Closed (2024)". It went into receivership
in November 2024, and the receivers agreed a €6m sale of the distillery, the brand
portfolio and the IP to **Tennessee Distilling Group in March 2026**, which has
said it will invest in the site. It stays on the map. An ownership line in the
description would stop the next audit re-raising it.
Source: https://www.irishtimes.com/business/2026/03/23/receivers-agree-sale-of-waterford-whisky-to-tennessee-distilling-group-for-6m/

**4. Eleven island rows have a blank `address`.** West Cork, Clonakilty,
Glendalough, Hawk's Rock, Boann, Tipperary, Wayward, plus the four the brief
already named — Echlinville, Hinch, Copeland, Limavady. Six also have a blank
`website`: Echlinville, Hinch, Copeland, Limavady, Two Stacks, Glendree. These
are not wrong, they are thin, and they are the reason a postcode-based NI/RoI
split cannot be done cleanly.

**5. Eighteen island rows carry coordinates at four decimal places or fewer** —
roughly 10 m precision at best, and in several cases the rounding is visible
(Ahascragh at `53.53, -8.34` is two decimal places, about 1 km). Bushmills,
Dingle, Waterford, West Cork, Clonakilty, Royal Oak, Powerscourt, Slane, Ballina,
Glendalough, Hawk's Rock, Boann, Echlinville, Hinch, Copeland, Two Stacks,
J.J. Corry, Ahascragh. Fine for a country page, poor for anyone navigating to one.

**6. No duplicate pins found.** The two closest pairs are both genuine: Teeling
and The Dublin Liberties sit 55 m apart on Newmarket and Mill Street, and Pearse
Lyons and Roe & Co sit 241 m apart on James's Street. Dublin 8 is simply dense.

**7. Five rows still carry `country: "Ireland"` with a BT postcode** — Belfast
Distillery, Rademon Estate, Scotts Irish, The Quiet Man, Titanic Distillers.
First filed 16 August in `UK-NI-WALES-AUDIT.md` and unchanged.

---

## Definitional questions for John

These are not defects. They are places where the map's inclusion rule does not
give an answer, and where a decision would make the next audit faster.

1. **Do in-planning and under-construction sites belong on the map?** Four of the
   eight raw candidates are in that class, and Irish Whiskey Magazine carries them
   as first-class listings. If yes, they need a role value (`in_planning`) so that
   nobody drives to Boyle expecting a tour. If no, the audit can stop re-finding
   them every pass.
2. **Do non-distilling brands belong?** `Two Stacks Irish Whiskey` is already on
   the map and does not distil; `The Muff Liquor Company` is not. Whichever way it
   goes, they should be treated the same. The `entity_role` machinery already
   supports keeping them with an honest label rather than deleting them.
3. **Gin brands made at another producer's distillery** — Jawbox, Shortcross,
   An Dúlamán, Minke, Method & Madness and roughly thirty more. These need no new
   pins under any reading, but if the map ever wants to be findable by brand, that
   is a search-index question, not a dataset question.

---

## What would move the number next

In order of value:

1. **A gin-first sweep.** At least 37 island distilleries make gin. Three of four
   sources here were whiskey directories, so the true gin coverage is unknown.
2. **Revenue and HMRC excise registers.** The only route to a real denominator.
   Needs filtering work, not scraping budget.
3. **Ask the Irish Whiskey Association for its member list.** 47 member companies,
   no public directory. One email.
4. **Backfill the eleven blank addresses**, which also unblocks a clean NI/RoI
   country split.
