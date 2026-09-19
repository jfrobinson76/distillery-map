# Ownership card — computed numbers

Edition: September 2026. Scotch whisky only. Built from `data/company-crosswalk/company-crosswalk.csv` (high/verified, Companies House), `data/ownership/psc-parents.csv` (ultimate controller), `data/categories/out_*.json`, and `public/data/distilleries.geojson`. `groups.json` is display names and colours only. Rebuild after pulling the crosswalk branch; do not copy these figures by hand onto the card.

## Claim on both slides

- **Half independent.**
- 176 Scotch whisky distilleries. Fifteen groups run 89. Diageo runs 32, one in five.
- By number of distilleries, not by litres.

| | |
|---|---:|
| Scotch whisky sites | 176 |
| Matched high/verified | 148 |
| Unmatched (drawn as independent) | 28 |
| Independent (controller has one site, plus unmatched) | 87 |
| Group-run | 89 |
| Groups >1 site | 15 |
| Diageo | 32 |

Independent means the ultimate controller in `psc-parents.csv` runs exactly one site in this universe. Unmatched Scotch sites are treated as independent dots — they are small, mostly post-2005 plants. Counts, not litres.

## Universe

Map region `scotland`, excluding Shetland (lat > 59.85), visitor (Johnnie Walker Princes Street), the Gordon & MacPhail bottler, Distillers Market, whisky lounges, and gin-named sites. A site is in if the map description says malt/grain/whisky or the category verdict includes whisky. Empty-description high-confidence sites are added only when their controller already has a whisky-signal site (the group-fill that restores Auchroisk, Dufftown, Allt-A-Bhainne, Kininvie, Lagg, Glen Turner).

Group-fill sites: Auchroisk distillery; Kininvie distillery; Dufftown distillery; Allt-A-Bhainne; Glen Turner Distillery; Lagg Distillery.

README on this branch dated the denominator 178 ±5. This rebuild is 176.

## Top eight operating groups (hubs on both slides)

| Group | Sites | Ultimate |
|---|---:|---|
| Diageo | 32 | Diageo (00023307) |
| Pernod Ricard | 13 | Pernod Ricard Sa (SC043917) |
| William Grant | 5 | William Grant & Sons Holdings Limited (15238251) |
| Whyte & Mackay | 5 | Emperador Holdings (Gb) Limited (09094033) |
| Inver House | 5 | International Beverage Holdings Limited (SC222095) |
| Bacardi | 4 | Bacardi U.K. Limited (00366786) |
| Ian Macleod | 4 | IAN MACLEOD DISTILLERS LIMITED (SC032696) |
| Suntory Global Spirits | 4 | Beam Suntory Uk Holdings Limited (05608446) |

### Diageo (32)

Diageo plc is PSC-exempt and is its own top; Wikidata rows and Diageo Scotland Limited both land here.

- Auchroisk distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Benrinnes Distillery — Diageo (00023307) → Diageo
- Blair Athol Distillery — Diageo (00023307) → Diageo
- Brora Distillery — Diageo (00023307) → Diageo
- Cameronbridge Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Caol Ila Distillery — Diageo (00023307) → Diageo
- Cardhu Distillery — Diageo (00023307) → Diageo
- Clynelish Distillery — Diageo (00023307) → Diageo
- Cragganmore Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Dailuaine — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Dalwhinnie Distillery — Diageo (00023307) → Diageo
- Dufftown distillery — Diageo (00023307) → Diageo
- Glen Elgin Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Glen Ord Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Glen Spey Distillery — Diageo (00023307) → Diageo
- Glendullan Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Glenkinchie Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Glenlossie — Diageo (00023307) → Diageo
- Inchgower Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Knockando Distillery — Diageo (00023307) → Diageo
- Lagavulin Distillery — Diageo (00023307) → Diageo
- Leven Distillery (Diageo) — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Linkwood distillery — Diageo (00023307) → Diageo
- Mannochmore Distillery — Diageo (00023307) → Diageo
- Mortlach Distillery — Diageo (00023307) → Diageo
- Oban Distillery — Diageo (00023307) → Diageo
- Port Ellen Distillery — Diageo (00023307) → Diageo
- Roseisle — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Royal Lochnagar Distillery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Strathmill — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc
- Talisker Distillery — Diageo (00023307) → Diageo
- Teaninich Distllery — DIAGEO SCOTLAND LIMITED (SC000750) → Diageo Plc

### Pernod Ricard (13)

Foreign parent: chain stops at Pernod Ricard SA.

- Aberlour Distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Allt-A-Bhainne — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Braeval Distillery — BRAEVAL DISTILLERY LIMITED (SC240804) → Pernod Ricard Sa
- Dalmunach Distillery — DALMUNACH DISTILLERY LIMITED (SC222298) → Pernod Ricard Sa
- Glen Keith Distillery — GLEN KEITH DISTILLERY COMPANY LIMITED (SC045679) → Pernod Ricard Sa
- Glenburgie Distillery — GLENBURGIE DISTILLERY LIMITED (00074809) → Pernod Ricard Sa
- Glentauchers Distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Longmorn distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Miltonduff Distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Scapa Distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- Strathclyde Distillery — STRATHCLYDE DISTILLERY LIMITED (SC043917) → Pernod Ricard Sa
- Strathisla Distillery — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa
- The Glenlivet — CHIVAS BROTHERS LIMITED (SC268758) → Pernod Ricard Sa

### William Grant (5)

William Grant & Sons Holdings Limited.

- Ailsa Bay — WILLIAM GRANT & SONS LIMITED (SC131772) → William Grant & Sons Holdings Limited
- Balvenie Distillery — WILLIAM GRANT & SONS LIMITED (SC131772) → William Grant & Sons Holdings Limited
- Girvan Distillery — WILLIAM GRANT & SONS LIMITED (SC131772) → William Grant & Sons Holdings Limited
- Glenfiddich Distillery — WILLIAM GRANT & SONS LIMITED (SC131772) → William Grant & Sons Holdings Limited
- Kininvie distillery — WILLIAM GRANT & SONS LIMITED (SC131772) → William Grant & Sons Holdings Limited

### Whyte & Mackay (5)

Emperador Holdings → Whyte & Mackay.

- Dalmore Distillery — WHYTE AND MACKAY GROUP LIMITED (SC221954) → Emperador Holdings (Gb) Limited
- Fettercairn Distillery — WHYTE AND MACKAY GROUP LIMITED (SC221954) → Emperador Holdings (Gb) Limited
- Invergordon Distillery — WHYTE AND MACKAY GROUP LIMITED (SC221954) → Emperador Holdings (Gb) Limited
- Isle of Jura Distillery — WHYTE AND MACKAY GROUP LIMITED (SC221954) → Emperador Holdings (Gb) Limited
- Tamnavulin Distillery — WHYTE AND MACKAY GROUP LIMITED (SC221954) → Emperador Holdings (Gb) Limited

### Inver House (5)

International Beverage → Inver House. Same ultimate_number, two name spellings.

- ANCNOC Distillery — INVER HOUSE DISTILLERS LIMITED (SC040036) → International Beverage Holdings Limited
- Balblair Distillery — THE BALBLAIR DISTILLERY COMPANY LIMITED (SC163039) → International Beverage Holdings (Uk) Limited
- Balmenach Distillery — INVER HOUSE DISTILLERS LIMITED (SC040036) → International Beverage Holdings Limited
- Pulteney Distillery — THE PULTENEY DISTILLERY COMPANY LIMITED (SC156412) → International Beverage Holdings (Uk) Limited
- Speyburn Distillery — INVER HOUSE DISTILLERS LIMITED (SC040036) → International Beverage Holdings Limited

### Bacardi (4)

Bacardi U.K. Limited.

- Aberfeldy Distillery — JOHN DEWAR AND SONS LIMITED (00613551) → Bacardi U.K. Limited
- Aultmore Distillery — JOHN DEWAR AND SONS LIMITED (00613551) → Bacardi U.K. Limited
- MacDuff Distillery — JOHN DEWAR AND SONS LIMITED (00613551) → Bacardi U.K. Limited
- Royal Brackla — JOHN DEWAR AND SONS LIMITED (00613551) → Bacardi U.K. Limited

### Ian Macleod (4)

Ian Macleod Distillers Limited.

- Glengoyne Distillery — IAN MACLEOD DISTILLERS LIMITED (SC032696) → IAN MACLEOD DISTILLERS LIMITED
- Ian Macleod Distillers Ltd — IAN MACLEOD DISTILLERS LIMITED (SC032696) → IAN MACLEOD DISTILLERS LIMITED
- Rosebank Distillery — IAN MACLEOD DISTILLERS LIMITED (SC032696) → IAN MACLEOD DISTILLERS LIMITED
- Tamdhu Distillery — IAN MACLEOD DISTILLERS LIMITED (SC032696) → IAN MACLEOD DISTILLERS LIMITED

### Suntory Global Spirits (4)

Beam Suntory UK Holdings Limited.

- Ardmore Distillery — BEAM SUNTORY UK LIMITED (05591988) → Beam Suntory Uk Holdings Limited
- Bowmore Distillery — BEAM SUNTORY UK LIMITED (05591988) → Beam Suntory Uk Holdings Limited
- Glen Garioch Distillery — BEAM SUNTORY UK LIMITED (05591988) → Beam Suntory Uk Holdings Limited
- Laphroaig Distillery — BEAM SUNTORY UK LIMITED (05591988) → Beam Suntory Uk Holdings Limited

## Mapped groups below the top eight

These are groups, not independents. On the map they use their own colour and join their sites with the same MST web. They appear in the left rail.

- **Brown-Forman** (4): Glenglassaugh Distillery; The Glendronach Distillery; Newbridge Bond - The Benriach Distillery Company Limited; Benriach Distillery
- **Distell** (3): Bunnahabhain Distillery; Tobermory Distillery; Deanston Distillery
- **Edrington** (2): Highland Park Distillery; The Macallan Distillery
- **Isle of Arran** (2): Arran Distillery; Lagg Distillery
- **La Martiniquaise** (2): Glen Moray Distillery; Glen Turner Distillery
- **Loch Lomond Group** (2): Loch Lomond Distillery; Glen Scotia Distillery
- **LVMH** (2): Ardbeg; Glenmorangie Distillery

## Map

No hub discs. Each group's sites stay at real coordinates and are joined by a minimum-spanning tree in the group colour at 30% alpha. Group names and counts sit in a left rail, sorted by count. Projection is a spherical transverse Mercator centred on 4.2°W, 57°N.

Site labels on the map: Talisker, Lagavulin, Caol Ila, Cardhu, Glenfiddich.

## Companies left as Independent with more than one site

None. Every multi-site controller in the matched Scotch set is a group.

## Unmatched Scotch sites (independent dots)

- 57° SKYE Distillery (57-skye-distillery)
- 8 Doors Distillery (8-doors-distillery)
- Aberargie Distillery (aberargie-distillery)
- Abhainn Dearg Distillery (abhainn-dearg-distillery)
- Ardross Distillery (ardross-distillery)
- Ballindalloch Distillery (ballindalloch-distillery)
- Benbecula Distillery (benbecula-distillery)
- Bonnington (bonnington)
- Daftmill Distillery (daftmill-distillery)
- Falkirk Distillery (falkirk-distillery)
- Galloway distillery (galloway-distillery)
- GlenWyvis Distillery (glenwyvis-distillery)
- Great Glen Distillery - Scotlands Smallest Craft Distillery (great-glen-distillery-scotlands-smallest-craft-distillery)
- Highland Boundary Wild Distillery (highland-boundary-wild-distillery)
- Isle of Tiree distillery (isle-of-tiree-distillery)
- Laggan Bay Distillery (laggan-bay-distillery)
- Luss Distillery (luss-distillery)
- Ogilvy Distillery (ogilvy-distillery)
- Persie Distillery (persie-distillery)
- Port of Leith distillery (port-of-leith-distillery)
- Reivers Distillery (reivers-distillery)
- Rhidorroch Distillery Cafe, Bar & Eatery (rhidorroch-distillery-cafe-bar-eatery)
- Stannergill Distillery (stannergill-distillery)
- Starlaw Distillery (starlaw-distillery)
- Stornoway Distillers Co. (stornoway-distillers-co)
- Tayport Distillery (tayport-distillery)
- The Cabrach Distillery (the-cabrach-distillery)
- The Machrihanish Distillery (the-machrihanish-distillery)

## Human look

- **Macdonald & Muir / Ardbeg / Glenmorangie.** The corrected PSC file now stops at LVMH. They are their own two-site group, not Diageo.
- **Newbridge Bond** is a Brown-Forman warehouse row, not a still. It is in the Brown-Forman four because the crosswalk row is high-confidence and the controller already has whisky-signal sites. A human may drop it.
- **Ian Macleod Distillers Ltd** is a name-match HQ row with an empty description and a whisky category verdict. Same treatment.
- **Speymalt / Gordon & MacPhail.** Benromach is a matched one-site controller (independent). The Cairn is empty-description and was not group-filled — it is not one of the six named malt restorations. Including it would invent a fifteenth group the README does not carry.
