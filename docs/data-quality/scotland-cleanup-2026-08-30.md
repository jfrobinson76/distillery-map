# Scotland cleanup, 30 August 2026

Follow-up to `scotland-sweep-2026-08-30.md` section 4, the flag list. Every row below
was checked against a live source, not just the sweep's one-line note. Proof URLs are
in the JSON action file, not repeated here.

Action file: `scotland-cleanup-actions.json` (applied by the main session, not this doc).

## Headline counts

| Action | Count |
|---|---|
| Remove | 20 |
| Merge (duplicate folded into a keeper) | 4 |
| Update (address, region, name, entity_role) | 25 |
| Total actions in the JSON file | 49 |
| Rows coming off the map (remove + merge) | 24 |
| Needs John | 3 |
| No published address found (own site checked) | 24 (see class E) |

## A. Duplicate pairs

| Pair | Keep | Remove | Why |
|---|---|---|---|
| Knockdhu / ANCNOC | ancnoc-distillery | knockdhu-distillery | Same distillery near Knock, Huntly. Trades as anCnoc since the 1990s. Keeper gets `brands: ["anCnoc"]`. |
| Arran / Lochranza | arran-distillery | lochranza-distillery | Same site, Lochranza. Keeper gets `brands: ["Machrie Moor"]`. |
| Eden Mill | eden-mill-st-andrews | eden-mill-distillery | Guardbridge (Eden Campus) is the one working site. |
| Speyburn | speyburn-glenlivet-distillery | speyburn-distillery | Same site, Rothes. Keeper renamed "Speyburn Distillery", description fixed to Speyside. |
| Torrisdale | beinn-an-tuirc-distillers | distillery-cafe | Café is the distillery's own on-site café, not a separate place. |
| Port Charlotte / Octomore | (neither, both removed) | port-charlotte-distillery, octomore | Historic Port Charlotte (Lochindaal) closed 1929, now a Canmore record. Octomore is a farm-name Bruichladdich brand with no address of its own. Both brands already live under bruichladdich-distillery. |

## B. Closed, demolished or non-qualifying sites

| Row | Status | Action |
|---|---|---|
| Glenlochy | Demolished 1983, now flats. glenlochy.com is dead. | Remove |
| Littlemill | Demolished after 2004 fire, now housing. Brand revived at new Luss Distillery, different site. | Remove |
| Dallas Dhu | Historic Environment Scotland museum, no distilling since 1983, shop is not a producer's own retail. | Remove |
| Lochside | Demolished 2004-05, now housing. | Remove |
| Millburn | Closed 1985, site now part of a Premier Inn, no distilling. | Remove |
| Imperial | Demolished 2013. Duplicate of the real Dalmunach pin on the same site. | Remove |
| Dalmunach | Real, operating since 2015, was on the map with a blank address. | Update: address Carron, Aberlour, Moray AB38 7QP |
| Caledonian | 242 Morrison St is now flats. Website on file (smugglersspirits.co.uk) is an unrelated brand, no connection to this address. | Remove |
| The Distillery at Coleburn | Mothballed since 1985. Reopening announced Aug 2025 for 2027. Not distilling today, planning/rebuild stage. Recheck in 2027. | Remove |
| Loch Ewe | Closed 2017, owners gone, no live web presence. | Remove |
| Lone Wolf (BrewDog) | BrewDog closed its whole distilling arm Jan 2026. No rebrand found. | Remove |
| Kimbland | Real registered distillery, Sanday, Orkney, but mothballed since 2023 with an FSS "do not drink" warning Dec 2025, no reopening announced. | Remove |
| Isla distillery (Perth) | Old Isla (1851-1926) is gone. Same address now hosts The Perth Distillery Company, real operating gin producer since 2019. | Update: rename to "The Perth Distillery Company", website perthdistillery.co.uk |
| Langholm Distillery | Real, currently operating (gin, fortified wines, brandies), open Wed-Sun. Not the old closed 19th-century site. Address not found on its site. | Update: website only, address stays a "needs John" gap |
| Kirkliston, Lochrin, Kilbagie, Provanmill | Long-closed grain/malt distilleries, no modern successor, no address. | Remove all four |
| Greenock distillery | Old grain distillery long closed. Address now home to Titan Spirits Ltd, a real registered producer at that address. | Update: rename to "Titan Spirits" |

## C. Brand and office rows with no address

| Row | Action | Why |
|---|---|---|
| Johnnie Walker (Kilmarnock pin) | Remove | Bottling plant closed 2012, demolished 2013, site is now Kilmarnock College / HALO regeneration. The correct Diageo pin, johnnie-walker-princes-street (Edinburgh, brand_shop), is untouched. |
| Gordon & MacPhail | Update | Address George House, Boroughbriggs Road, Elgin, Moray IV30 1JY. entity_role head_office (their own offices, maturation and bottling site, and where retail/wholesale/export is run from). |
| Pollo | Remove | Old Highland distillery near Invergordon, closed 1931, ruins only, no current business. |
| William Grant and Sons | Update | Address The Old Court House, 7 Parkshot, Richmond, Surrey TW9 2RF. entity_role head_office. |
| Ian Macleod Distillers Ltd | Update | Fixed address formatting: Peter Russell House, 2 Young's Road, East Mains Industrial Estate, Broxburn, West Lothian EH52 5LY. entity_role head_office. |
| Newbridge Bond (Benriach) | Update | entity_role bottling_plant. Trade sources confirm bottling, packaging and warehousing happen there, not just storage. Address already correct. |

## D. Wrong region tags

| Row | Was | Now | Why |
|---|---|---|---|
| Bonnington | rest | scotland | Edinburgh (The Biscuit Factory, EH6 5NP). |
| The Machrihanish Distillery | ireland | scotland | Campbeltown, Argyll (PA28 6NT). |
| The Lakes Distillery | scotland | uk | Cockermouth, Cumbria, England. |
| Ad Gefrin Distillery | scotland | uk | Wooler, Northumberland, England. |
| Wild Sheep Distillery | scotland | uk | Keswick, Cumbria, England. |
| Daisy Distillery Ltd | scotland | uk | Saltburn-by-the-Sea, North Yorkshire, England. |
| Black Cat Distillery | scotland | uk | Penrith, Cumbria, England. |
| WL Distillery | scotland | uk | South Hetton, Durham, England. |
| Yarm Distillery Ltd | scotland | uk | Eaglescliffe, Stockton-on-Tees, England. |
| Moonshiners Institute | scotland | uk | Newcastle upon Tyne, England. |
| Durham Distillery | scotland | uk | Durham is an English city; no address on file to confirm further, but there is no place of this name in Scotland. |

## E. Blank addresses

The rule for this class was strict: fill only from the distillery's own website. Six
came back clean from an owner's own contact/visit page and are in the JSON:

| Distillery | Address | Source |
|---|---|---|
| Glen Grant | The Glen Grant Distillery, Rothes, Moray AB38 7BS | theglengrant.com contact page |
| Pulteney (Old Pulteney) | Pulteney Distillery, Huddart Street, Wick, Caithness KW1 5BA | oldpulteney.com contact page |
| Glen Scotia | 12 High Street, Campbeltown, Argyll PA28 6DS | glenscotia.com tours page |
| Arbikie | Arbikie Distillery, Lunan, Angus DD10 9TR | arbikie.com visit-us page |
| Abhainn Dearg | Carnish, Isle of Lewis, Outer Hebrides HS2 9EX | abhainndeargdistillery.co.uk (old domain now redirects here, website field updated too) |
| Benbecula | Gramsdale, Benbecula, Outer Hebrides HS7 5QP | benbeculadistillery.com |

Dalmunach's address is filled too, but that came out of class B (Imperial/Dalmunach), not this class.

The remaining 24 blank-address rows either have no address on their own site, or the
only address found came from a secondary source (Wikipedia, a reference wiki, a
Diageo brand microsite, Companies House). Per the rule, that is not good enough to
write into the file, so none of these are in the JSON. Candidate addresses are listed
here for reference only, unverified against an owner's own site:

Glenfiddich (Dufftown, Keith, Moray AB55 4DH), Edradour (Pitlochry PH16 5JP, and
reportedly closed to visitors since 2025 for staffing reasons, worth a check), Scapa
(St Ola, Kirkwall, Orkney KW15 1SE), Tamdhu (Knockando, Aberlour AB38 7RP), Tormore
(Advie, Grantown-on-Spey PH26 3LR), Braeval (Chapeltown, Ballindalloch AB37 9JS),
Glenburgie (By Alves, Forres IV36 2QY), Balmenach (Cromdale, Grantown-on-Spey
PH26 3PF), Benrinnes (Aberlour AB38 9NN), Cragganmore (Ballindalloch AB37 9AB),
Inchgower (Buckie, Moray AB56 4TR, two conflicting postcodes seen, needs a clean
check), Knockando (Aberlour AB38 7RP), Miltonduff (Elgin IV30 8TQ), Glentauchers
(Mulben, Keith AB55 6YL), Aultmore (Keith AB55 6QY), Royal Lochnagar (Crathie,
Ballater AB35 5TB), Roseisle (Elgin IV30 5YP, address looked geocoded rather than
published, low confidence), Starlaw (Bathgate EH47 7BW), Isle of Tiree (West Hynish
PA77 6UF), Kininvie (shares the Glenfiddich/Balvenie estate in Dufftown, no distinct
address exists), Strathmill (Keith AB55 5DQ). Strathearn has no address published
anywhere, including its own site and Wikipedia; leave blank.

**Deeside Distillery flag**: the website on file, deesidedistillery.net, is dead. The
company appears to have renamed to Lost Loch Spirits Ltd, trading from
lostlochspirits.com at the same unit in Aboyne. This looks like a business rename, not
just a missing address, so it is not in the JSON. See Needs John.

## Needs John

- **Deeside Distillery rename**: deesidedistillery.net is dead. Companies House shows
  the operator (originally "Deeside Distillery Ltd") now trades as Lost Loch Spirits
  Ltd from the same address (Deeside Activity Park, Dess, Aboyne AB34 5BD). This looks
  like a real rename, not a closure, but renaming the row is a bigger call than an
  address fill. https://www.lostlochspirits.com/
- **Portintruan Distillery (Islay)**: outside the five audit classes, but flagged by the
  sweep. As of this check its own site still says it is "readying to open" with no
  first-cask date published. It may already have distilled by the time this is read.
  Recheck before deciding to remove. https://portintruan.com
- **Langholm Distillery**: confirmed real and operating (gin, fortified wines,
  brandies; open Wed-Sun), website field updated in this pass, but no postal address
  could be found on the distillery's own site. Needs a direct address lookup
  (Companies House or a site visit) before the address field can be filled.
- **Dallas Dhu**: a strict read of the inclusion rules says remove (no still, museum
  shop is not a producer's own retail place). It is a well-known heritage attraction
  and the removal is worth a second look before it goes.
- **Kimbland Distillery**: real, registered, has an address, but mothballed since 2023
  with a December 2025 food-safety warning and no reopening announced. Recommended
  remove on "not distilling today," but it is a real site, not a historic ruin like
  the others in class B, so flagging the call rather than burying it in the table.
