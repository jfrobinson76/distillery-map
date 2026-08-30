# Scotland sweep, 30 August 2026

Trigger: Springbank was found missing on 29 August. Scotland had never been checked
against a list of working distilleries. This is that check, for Scotch whisky (malt and
grain) only. Gin-only sites are out of scope.

Bar: `inclusion-rules.md`. A pin needs a real address and spirit distilled there today.
Planned, under construction, mothballed with no reopening plan, or demolished sites fail.

## Headline numbers

| | Count |
|---|---|
| Reference list (Wikipedia active malt + grain, deduped) | 165 |
| On the map by name match | 152 |
| On the map under a different name (Leven, Orkney) | 2 |
| Missing | 11 |
| Missing and verified PASS with address + coordinates | 10 |
| Missing but FAIL (not distilling yet) | 1 (Ben Cumhaill) |

Reference: https://en.wikipedia.org/wiki/List_of_whisky_distilleries_in_Scotland (active
malt 158 names, active grain 8, Loch Lomond in both). The SWA quotes about 150 operating
distilleries, which lines up once the newest openings are counted. Every reference name was
substring-matched against ALL 6,146 features, not just `region=scotland`, with aliases
(Isle of X, The X, ANCNOC for Knockdhu, Arran for Lochranza, Burnobennie, etc).

Match method: `scratchpad/scotland-on-map.txt` (245 rows with `region=scotland`) plus a
full-name scan. Scottish rows found under other regions: Bonnington (`rest`), Machrihanish
(`ireland`). See flags below.

## Missing sites, verified

Coordinates: WD = Wikidata P625, OSM = OpenStreetMap object, OSM-PC = OSM postcode centroid
via Nominatim (good to ~200 m, refine when the row is built).

| # | Name | Region | Trading? | Address | Lat | Lng | Coord source | Website | Description | Operator | Proof URL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Brora Distillery | Highland | Yes, reopened May 2021 | 3 Clynelish Road, Brora KW9 6LR | 58.024908 | -3.868132 | WD Q744308 (OSM way 1298607768 agrees) | https://www.malts.com/en-gb/distilleries/brora | Highland malt, closed 1983, restored and refilled its first cask 19 May 2021. Appointment-only visits. Sits beside Clynelish, which is on the map. | Diageo | https://en.wikipedia.org/wiki/Brora_distillery |
| 2 | Glen Spey Distillery | Speyside | Yes | Glen Spey Distillery, Rothes, Aberlour AB38 7AY | 57.525611 | -3.210111 | Wikipedia infobox | none official (Diageo, Flora & Fauna range) | Speyside malt, founded 1878, blend workhorse for J&B. No visitor centre. | Diageo | https://en.wikipedia.org/wiki/Glen_Spey_distillery |
| 3 | Mannochmore Distillery | Speyside | Yes | Glenlossie Road, Elgin IV30 8GZ | 57.6003 | -3.31944 | WD Q362391 (OSM way 839410590 at 57.6008, -3.3130) | none official | Speyside malt, built 1971 next to Glenlossie (on map). Loch Dhu was made here. | Diageo | https://scotchwhisky.com/whiskypedia/1881/mannochmore/ |
| 4 | Girvan Distillery | Lowland (grain) | Yes | Grangestone Industrial Estate, Girvan KA26 9PT | 55.260853 | -4.8336 | WD Q1527141 (OSM relation 19824509 at 55.2712, -4.8292) | https://www.williamgrant.com | Grain distillery since 1963, one of Scotland's largest plants. The map's Ailsa Bay row already carries this address; Girvan is the grain plant and needs its own pin. | William Grant & Sons | https://en.wikipedia.org/wiki/Girvan_distillery |
| 5 | The Cabrach Distillery | Speyside | Yes, first cask Nov 2024 | Inverharroch Farm, Lower Cabrach, Huntly AB54 4EU | 57.3672 | -3.0291 | OSM-PC | https://www.thecabrach.com | Community-owned malt distillery and heritage centre. First legal spirit in the Cabrach for 170 years, distilled 25 Oct 2024. | The Cabrach Trust (CIC) | https://www.thespiritsbusiness.com/2024/10/whisky-production-begins-at-cabrach-distillery/ |
| 6 | Laggan Bay Distillery | Islay | Yes, first cask 2 Apr 2026 | Glenegedale, Isle of Islay PA42 7AS | 55.6859 | -6.2381 | OSM-PC | https://www.lagganbay.com | Islay's 11th distillery, beside the airport. Heavily peated malt, 1m LPA. Public opening at Feis Ile 2026. | Ian Macleod Distillers | https://www.thespiritsbusiness.com/2026/04/laggan-bay-opens-as-islays-11th-distillery/ |
| 7 | Stannergill Distillery | Highland (Caithness) | Yes, first spirit 10 Jul 2026 | Castletown Mill, Castletown, Thurso KW14 8UT | 58.5919 | -3.3810 | OSM-PC | https://stannergillwhisky.co.uk | Malt distillery in the restored 19th-century Castletown Mill on the NC500. 240,000 LPA. Shop, restaurant and tours open. | Dunnet Bay Distillers (Martin and Claire Murray) | https://www.thespiritsbusiness.com/2026/07/stannergill-distillery-starts-production/ |
| 8 | Kythe Distillery | Highland (Perthshire) | Yes, distilling since 2 Jul 2026 | Hills of Bendochy, Coupar Angus, Blairgowrie PH13 9HN | 56.5596 | -3.2926 | OSM way 213879961 (Hills of Bendochy farm) | https://kythedistillery.com | Old-style Highland malt: heritage barley, wooden washbacks, direct wood-fired wash still. About 50,000 LPA. | Kythe Distillery Co Ltd (McMillan, MacRaild, Chan) | https://www.masterofmalt.com/blog/post/kythe-distillery-has-begun-distilling/ |
| 9 | Balmaud Distillery | Highland (Aberdeenshire) | Yes, first whisky casks Feb 2025 | Mill of Balmaud Farm, King Edward, Banff AB45 3PN | 57.6016 | -2.4409 | OSM-PC | https://balmauddistillery.com | Single-estate farm distillery near Turriff. Whisky laid down; gin, vodka and rum made and bottled on site. Pre-booked visits from 2026. | Balmaud Distillery Company Ltd (Strachan family) | https://whiskymag.com/articles/traditional-farming-meets-modern-whisky-making-at-balmaud-distillery/ |
| 10 | Reivers Distillery | Lowland (Borders, grain + malt) | Yes, low profile | Block 1, Tweedbank Industrial Estate, Galashiels TD1 3RS | 55.6022 | -2.7589 | OSM-PC | https://mossburndistillers.com | Small experimental pot + column plant making rye and grain spirit and genever. Not open to visitors. Warehousing moved to Jedburgh Aug 2026, stills stay for now. | Mossburn Distillers (owner of Torabhaig) | https://www.rarewhisky101.com/distilleries/reivers-distillery |

FAIL, do not add:

| Name | Why | Recheck source |
|---|---|---|
| Ben Cumhaill Distillery, Auldgirth, Dumfries DG2 0RZ | Wikipedia lists it as active, but the owners' own progress blog (late Jul 2026) says stills were still being tested with water. No spirit run yet. Planning/under-construction rule applies. | https://progress.bencumhaill.co.uk/ |

Present under another name (fix the row, do not add):

| Reference name | Map row | Fix |
|---|---|---|
| Orkney | "Orkney Gin Distillery", 58 Albert St, website highlandparkwhisky.com | This is the OSM object for The Orkney Distillery, Ayre Road, Kirkwall KW15 1QX (58.9843, -2.9615). Now distils single malt as well as Kirkjuvagr gin. Rename, fix address, website https://www.orkneydistilling.com. Proof: https://www.orkney.com/news/orkney-distillery-whisky |
| Leven | "Diageo Global Supply Centre", Banbeath Rd, Leven KY8 5HD | Diageo's small Leven malt distillery sits inside this packaging plant. Rename to "Leven Distillery (Diageo)" and say so in the description, or mark `entity_role` if the still is deemed not the point of the pin. |

## Map rows that look wrong

Not verified deeply. One-line reason each. Removal still needs the evidence bar in
`inclusion-rules.md`.

Closed, demolished or museum sites carrying no `entity_role` (all from Wikidata/OSM import):

- Glenlochy (Fort William): closed 1983, now housing.
- Littlemill (Bowling): demolished 2004.
- Dallas Dhu (Forres): Historic Environment Scotland museum, no distilling since 1983.
- Lochside (Montrose): demolished 2005. No address on row.
- Millburn (Inverness): closed 1985, now a restaurant. No address.
- Imperial distillery: demolished 2013, Dalmunach built on the site. Duplicate of Dalmunach pin.
- Caledonian (242 Morrison St, Edinburgh): grain distillery closed 1988, now flats.
- Isla distillery (Perth), Kirkliston, Langholm, Lochrin, Kilbagie, Provanmill, Greenock: all long closed, most with no address.
- Port Charlotte distillery (33 Main St): closed 1929. Website is a Canmore heritage record.
- The Distillery at Coleburn: closed 1985, now warehousing/events. No address.
- Loch Ewe Distillery: closed 2019. No address.
- Lone Wolf Distillery: BrewDog shut the distillery in 2024. No address.

Brand or office rows with no address and no `entity_role`:

- Johnnie Walker: no address, pin near Kilmarnock. Brand, not a place.
- Gordon & MacPhail: bottler/retailer in Elgin. Needs address + `entity_role` or removal.
- Octomore: a farm name and Bruichladdich brand, not a distillery. No address.
- Pollo: no address, no website, unidentified. Remove unless someone can name it.
- Kimbland distillery: Wikidata row on Sanday, Orkney, no address or website. Unverified.
- William Grant and Sons (`region=uk`): pin in London, no address.
- Ian Macleod Distillers Ltd (Broxburn): head office, needs `entity_role`.
- Newbridge Bond (Benriach): bonded warehouse, needs `entity_role`.

Duplicates (same site, two pins):

- Eden Mill Distillery (no address) and Eden Mill St Andrews (Guardbridge). Keep Guardbridge.
- Speyburn-Glenlivet distillery and Speyburn Distillery.
- Arran Distillery and Lochranza Distillery.
- Knockdhu Distillery and ANCNOC Distillery.
- Distillery Café and Beinn an Tuirc Distillers (same Torrisdale address).

Wrong region or country tag:

- Bonnington (Edinburgh) is `region=rest`. Should be `scotland`.
- The Machrihanish Distillery (Campbeltown) is `region=ireland`. Should be `scotland`.
- England rows tagged `scotland`: The Lakes, Ad Gefrin, Wild Sheep, Daisy, Black Cat, WL Distillery, Yarm, Moonshiners Institute, Durham Distillery.

Needs a status check before it stays:

- Portintruan Distillery (Islay): on the map, but as of April 2026 it had only filed its
  premises licence and no first-cask report was found. If it has not distilled yet it fails
  the planning rule. Recheck: https://elixirdistillers.com/distilleries/

Non-distilling retail or hospitality rows with no `entity_role`: The Lost Distillery Company
Whisky Lounge, Distillers Market (Milngavie), The Distilling House at Aberdeen Airport,
Pràban na Linne (Eilean Iarmain shop), Rhidorroch Distillery Cafe.

Address backfill: about 30 `scotland` rows are real working distilleries with a blank
address (Glenfiddich, Glen Grant, Edradour, Scapa, Tamdhu, Tormore, Braeval, Glenburgie,
Balmenach, Benrinnes, Cragganmore, Inchgower, Knockando, Miltonduff, Glentauchers, Aultmore,
Pulteney, Royal Lochnagar, Dalmunach, Roseisle, Starlaw, Glen Scotia, Arbikie, Strathearn,
Deeside, Abhainn Dearg, Isle of Tiree, Benbecula, Kininvie, Strathmill). They pass the bar
but the pin is thin. Separate task.

## What this sweep did not do

- Did not touch the geojson or any script.
- Did not check gin-only sites, or Scottish rows against a gin directory.
- Did not verify the flagged rows above beyond a one-line reason.
- Postcode-centroid coordinates for rows 5, 6, 7, 9, 10 should be tightened from the
  operator's own map or satellite imagery when the rows are built.
