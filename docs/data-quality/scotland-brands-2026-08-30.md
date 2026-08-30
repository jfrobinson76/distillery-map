# Scotland brand findability sweep, 30 Aug 2026

Research pass for the `brands` field, Scotland. Same evidence bar as the Ireland
pilot: one URL on the producer's or brand owner's own site per mapping, or it
does not ship. Geojson untouched; this doc is the sourced input.

## 1. Brands to add to existing pins

| Map slug | Site name | Brands to add | Class | Proof URL |
|---|---|---|---|---|
| tobermory-distillery | Tobermory Distillery | Ledaig | A | https://tobermorydistillery.com/collections/ledaig-whisky |
| bruichladdich-distillery | Bruichladdich Distillery | Port Charlotte, Octomore | A | https://www.bruichladdich.com/collections/port-charlotte and https://www.bruichladdich.com/collections/octomore |
| glengyle | Glengyle | Kilkerran | A | https://kilkerran.scot/ ("Kilkerran Single Malt is produced at the historic Campbeltown distillery, Glengyle") |
| knockdhu-distillery | Knockdhu Distillery | anCnoc | A | https://ancnoc.com/ (site is Knockdhu's own; "John Morrison built Knockdhu in 1894... the hill in our name") |
| dufftown-distillery | Dufftown distillery | The Singleton of Dufftown | A | https://malts.com/en-row/our-whisky-collection/the-singleton-of-dufftown ("distilled in the Dufftown distillery") |
| glendullan-distillery | Glendullan Distillery | The Singleton of Glendullan | A | https://www.malts.com/en-gb/single-malt-whisky-history/the-singleton-of-glendullan |
| glen-ord-distillery | Glen Ord Distillery | The Singleton of Glen Ord | A | https://www.malts.com/en-be/distilleries/the-singleton-of-glen-ord/ |
| tomatin-distillery | Tomatin Distillery | Cù Bòcan | A | https://tomatin.com/cu-bocan/ ("Distilled every winter at Tomatin Distillery") |
| edradour-distillery | Edradour Distillery | Ballechin | A | https://www.edradour.com/shop/whisky-ranges/ballechin ("the heavily peated distillation made at Edradour Distillery since 2003") |
| loch-lomond-distillery | Loch Lomond Distillery | Inchmurrin, Inchmoan | A | https://www.lochlomondwhiskies.com/products/inchmurrin-12-year-old-single-malt-whisky and https://www.lochlomondwhiskies.com/products/inchmoan-12-year-old-single-malt |
| lochranza-distillery | Lochranza Distillery | Machrie Moor | A | https://www.arranwhisky.com/shop-whiskies/arran-single-malts/174-machrie-moor-10-year-old-46-abv (produced at Lochranza) |
| isle-of-harris-distillery | Isle of Harris Distillery | The Hearach | A | https://www.harrisdistillery.com/products/the-hearach-single-malt-5 ("distilled, matured, and bottled right here in the island") |
| cameronbridge-distillery | Cameronbridge Distillery | Haig Club | A | https://www.haigclub.com/en/stories/the-haig-club-distillery-cameronbridge |
| strathisla-distillery | Strathisla Distillery | Chivas Regal | B | https://chivas.com/en-GB/the-story/strathisla ("Strathisla Distillery... is the home of Chivas") |
| aberfeldy-distillery | Aberfeldy Distillery | Dewar's | B | https://www.dewars.com/visit-us/ (the brand home is named "Dewar's Aberfeldy Distillery" across dewars.com) |
| ardmore-distillery | Ardmore Distillery | Teacher's | B | https://www.teacherswhisky.com/our-craft (Teacher's uses "peated single malt whisky from The Ardmore distillery" as "its fingerprint whisky") |
| glenburgie-distillery | Glenburgie Distillery | Ballantine's | B | https://www.ballantines.com/en/range/glenburgie-15-year-old/ (Ballantine's own range; Glenburgie is "the heart of the Ballantine's Blend") |
| blair-athol-distillery | Blair Athol Distillery | Bell's | B | https://www.malts.com/en/blair-athol (Blair Athol "produces the main malt component of Bell's Blended Scotch Whisky") |

Wording caveat for the country-page renderer: only Chivas Regal and Dewar's
carry a literal "home of" claim. Teacher's, Ballantine's and Bell's are
owner-proven production ties ("fingerprint whisky", "heart of the blend",
"main malt component"). Search keys are safe for all five; if a row renders
prose, match the owner's wording, not "home of".

## 2. Separate brand-home venues not on the map

| Name | Address | Lat | Lng | entity_role | Proof URL |
|---|---|---|---|---|---|
| Johnnie Walker Princes Street | 145 Princes Street, Edinburgh EH2 4BL, UK | 55.9501 | -3.2073 | brand_shop | https://www.johnniewalker.com/en-gb/visit-us-princes-street |

Notes. It is a full visitor experience: tours, tastings, two rooftop bars,
retail. The address is quoted from the owner's plan-your-visit page. The
existing "johnnie-walker" pin sits in Kilmarnock (55.6144, -4.5011), the
historic home town; it is not this venue.

The Macallan Estate visitor experience is at the distillery itself (Easter
Elchies, Aberlour AB38 9RX), the same site as the mapped pin
the-macallan-distillery. No separate pin needed.

## 3. Unproven, do not ship

- The Famous Grouse at Glenturret. Edrington sold the brand to William Grant &
  Sons in 2025; Glenturret is Lalique-owned. thefamousgrouse.com is age-gated
  with no visible claim, the old Famous Grouse Experience domain is dead, and
  theglenturret.com does not claim the blend. Re-check once the new owner
  publishes a position.
- Johnnie Walker at Cardhu. Diageo's own page says only "key component in
  Johnnie Walker blends", not home. JW is already findable via its own pin,
  and Diageo's stated brand home is Princes Street.
- White Horse at Lagavulin. Diageo pages tell the Peter Mackie history only.
  No current home claim.
- Whyte & Mackay at Dalmore. W&M owns Dalmore, but no owner page calls Dalmore
  the home of the W&M blend.
- Mossburn at Torabhaig. torabhaig.com calls Mossburn Distillers "Torabhaig's
  parent company and renowned independent bottler". A bottler, not a brand
  made there. Do not map.
- Naked Malt. No owner-site distillery home found. Skip.
- Ailsa Bay. Needs no brands entry: it has its own pin (ailsa-bay) beside
  girvan-distillery, and the Girvan description already notes the shared site.

## 4. Data-quality observations from this sweep (not actioned)

- knockdhu-distillery and ancnoc-distillery are duplicate pins for the same
  distillery, 800m apart, both pointing at ancnoc.com. Dedupe; keep Knockdhu
  with anCnoc as the brand.
- arran-distillery and lochranza-distillery are duplicates of the same
  Lochranza site (both arranwhisky.com). If both survive dedupe, Machrie Moor
  belongs on whichever remains.
- port-charlotte-distillery is the closed Lochindaal site (canmore.org.uk
  reference) and octomore is the farm; the drinkable Port Charlotte and
  Octomore brands belong on bruichladdich-distillery, not those pins.
- Knockdhu's stored website https://ancnoc.com/the-distillery/ now 404s; the
  root https://ancnoc.com/ works.
