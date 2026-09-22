# Ownership card — computed numbers

Edition: September 2026. Scotch whisky only. Built from `data/company-crosswalk/company-crosswalk.csv` (high/verified, Companies House), `data/ownership/psc-parents.csv` (ultimate controller), `data/categories/out_*.json`, and `public/data/distilleries.geojson`. `groups.json` is display names and colours only. Rebuild after pulling the crosswalk branch; do not copy these figures by hand onto the card.

## Claim on both slides

- **Two-thirds answer to a bigger company.**
- 163 operating Scotch whisky distilleries. 19 groups run 99 of them (61%). At most 56 are independent (34%). Diageo alone runs 31 (19%).
- By number of distilleries, not by litres.

| | |
|---|---:|
| Scotch whisky sites | 163 |
| Matched high/verified | 98 |
| Unmatched (drawn as independent) | 63 |
| One Scotch site, but part of a larger drinks company | 7 |
| Independent (one site, no larger drinks company above it) | 56 |
| Group-run | 99 |
| Groups >1 site | 19 |
| Diageo | 31 |

Universe (22 Sep 2026): Scotch whisky distilleries that distilled on site in the last 12 months or are temporarily paused, evidenced by the SWA September 2026 list or the operator / trade press. Gin-only, closed and not-yet-distilling sites are out. Independent means one Scotch site AND no larger drinks company above it; seven one-site owners sit under Campari, Rémy Cointreau, Nikka, Takara, Picard, Lalique and Halewood and are counted separately (`parent` column in the audit file). Counts, not litres.

## Universe

Map region `scotland`, excluding Shetland (lat > 59.85), visitor (Johnnie Walker Princes Street), the Gordon & MacPhail bottler, Distillers Market, whisky lounges, and gin-named sites. A site is in if the map description says malt/grain/whisky or the category verdict includes whisky. Empty-description high-confidence sites are added only when their controller already has a whisky-signal site (the group-fill that restores Auchroisk, Dufftown, Allt-A-Bhainne, Kininvie, Lagg, Glen Turner).

README on this branch dated the denominator 178 ±5. This rebuild is 163.

## Top eight operating groups (hubs on both slides)

| Group | Sites | Ultimate |
|---|---:|---|
| Diageo | 31 | Diageo |
| Pernod Ricard | 13 | Pernod Ricard |
| William Grant | 5 | William Grant |
| Whyte & Mackay | 5 | Whyte & Mackay |
| Inver House | 5 | Inver House |
| Bacardi | 5 | Bacardi |
| Suntory Global Spirits | 5 | Suntory |
| Ian Macleod | 4 | Ian Macleod |

### Diageo (31)

Diageo plc is PSC-exempt and is its own top; Wikidata rows and Diageo Scotland Limited both land here.

- Auchroisk distillery —  () → Diageo
- Benrinnes Distillery —  () → Diageo
- Blair Athol Distillery —  () → Diageo
- Brora Distillery —  () → Diageo
- Cameronbridge Distillery —  () → Diageo
- Caol Ila Distillery —  () → Diageo
- Cardhu Distillery —  () → Diageo
- Clynelish Distillery —  () → Diageo
- Cragganmore Distillery —  () → Diageo
- Dailuaine —  () → Diageo
- Dalwhinnie Distillery —  () → Diageo
- Dufftown distillery —  () → Diageo
- Glen Elgin Distillery —  () → Diageo
- Glen Ord Distillery —  () → Diageo
- Glen Spey Distillery —  () → Diageo
- Glendullan Distillery —  () → Diageo
- Glenkinchie Distillery —  () → Diageo
- Glenlossie —  () → Diageo
- Inchgower Distillery —  () → Diageo
- Knockando Distillery —  () → Diageo
- Lagavulin Distillery —  () → Diageo
- Linkwood distillery —  () → Diageo
- Mannochmore Distillery —  () → Diageo
- Mortlach Distillery —  () → Diageo
- Oban Distillery —  () → Diageo
- Port Ellen Distillery —  () → Diageo
- Roseisle —  () → Diageo
- Royal Lochnagar Distillery —  () → Diageo
- Strathmill —  () → Diageo
- Talisker Distillery —  () → Diageo
- Teaninich Distllery —  () → Diageo

### Pernod Ricard (13)

Foreign parent: chain stops at Pernod Ricard SA.

- Aberlour Distillery —  () → Pernod Ricard
- Allt-A-Bhainne —  () → Pernod Ricard
- Braeval Distillery —  () → Pernod Ricard
- Dalmunach Distillery —  () → Pernod Ricard
- Glen Keith Distillery —  () → Pernod Ricard
- Glenburgie Distillery —  () → Pernod Ricard
- Glentauchers Distillery —  () → Pernod Ricard
- Longmorn distillery —  () → Pernod Ricard
- Miltonduff Distillery —  () → Pernod Ricard
- Scapa Distillery —  () → Pernod Ricard
- Strathclyde Distillery —  () → Pernod Ricard
- Strathisla Distillery —  () → Pernod Ricard
- The Glenlivet —  () → Pernod Ricard

### William Grant (5)

William Grant & Sons Holdings Limited.

- Ailsa Bay —  () → William Grant
- Balvenie Distillery —  () → William Grant
- Girvan Distillery —  () → William Grant
- Glenfiddich Distillery —  () → William Grant
- Kininvie distillery —  () → William Grant

### Whyte & Mackay (5)

Emperador Holdings → Whyte & Mackay.

- Dalmore Distillery —  () → Whyte & Mackay
- Fettercairn Distillery —  () → Whyte & Mackay
- Invergordon Distillery —  () → Whyte & Mackay
- Isle of Jura Distillery —  () → Whyte & Mackay
- Tamnavulin Distillery —  () → Whyte & Mackay

### Inver House (5)

International Beverage → Inver House. Same ultimate_number, two name spellings.

- ANCNOC Distillery —  () → Inver House
- Balblair Distillery —  () → Inver House
- Balmenach Distillery —  () → Inver House
- Pulteney Distillery —  () → Inver House
- Speyburn Distillery —  () → Inver House

### Bacardi (5)

Bacardi U.K. Limited.

- Aberfeldy Distillery —  () → Bacardi
- Aultmore Distillery —  () → Bacardi
- Craigellachie —  () → Bacardi
- MacDuff Distillery —  () → Bacardi
- Royal Brackla —  () → Bacardi

### Suntory Global Spirits (5)

Beam Suntory UK Holdings Limited.

- Ardmore Distillery —  () → Suntory
- Auchentoshan Distillery —  () → Suntory
- Bowmore Distillery —  () → Suntory
- Glen Garioch Distillery —  () → Suntory
- Laphroaig Distillery —  () → Suntory

### Ian Macleod (4)

Ian Macleod Distillers Limited.

- Glengoyne Distillery —  () → Ian Macleod
- Laggan Bay Distillery —  () → Ian Macleod
- Rosebank Distillery —  () → Ian Macleod
- Tamdhu Distillery —  () → Ian Macleod

## Mapped groups below the top eight

These are groups, not independents. On the map they use their own colour and join their sites with the same MST web. They appear in the left rail.

- **Brown-Forman** (3): Benriach Distillery; Glenglassaugh Distillery; The Glendronach Distillery
- **CVH Spirits** (3): Bunnahabhain Distillery; Deanston Distillery; Tobermory Distillery
- **Edrington** (3): Glenrothes Distillery; Highland Park Distillery; The Macallan Distillery
- **Angus Dundee** (2): Glencadam Distillery; Tomintoul Distillery
- **Gordon & MacPhail** (2): Benromach; The Cairn
- **Isle of Arran** (2): Arran Distillery; Lagg Distillery
- **J & A Mitchell** (2): Glengyle; Springbank Distillery
- **La Martiniquaise** (2): Glen Moray Distillery; Starlaw Distillery
- **Loch Lomond Group** (2): Glen Scotia Distillery; Loch Lomond Distillery
- **LVMH** (2): Ardbeg; Glenmorangie Distillery
- **Mossburn** (2): Reivers Distillery; Torabhaig

## Map

No hub discs. Each group's sites stay at real coordinates and are joined by a minimum-spanning tree in the group colour at 50% alpha. Group names and counts sit in a left rail, sorted by count. Projection is a spherical transverse Mercator centred on 4.2°W, 57°N. The map is 12% smaller than the first top-left fit and anchored top-left so the Borders sit above the headline.

Site labels on the map: none.

## Companies left as Independent with more than one site

None. Every multi-site controller in the matched Scotch set is a group.

## Unmatched Scotch sites (independent dots)

- 8 Doors Distillery (8-doors-distillery)
- Aberargie Distillery (aberargie-distillery)
- Abhainn Dearg Distillery (abhainn-dearg-distillery)
- Annandale Distillery (annandale-distillery)
- Arbikie Distillery (arbikie-distillery)
- Ardgowan Distillery (ardgowan-distillery)
- Ardnahoe Distillery (ardnahoe-distillery)
- Ardnamurchan Distillery (ardnamurchan-distillery)
- Ardross Distillery (ardross-distillery)
- Badachro Distillery (badachro-distillery)
- Ballindalloch Distillery (ballindalloch-distillery)
- Balmaud Distillery (balmaud-distillery)
- Ben Nevis Distillery (ben-nevis-distillery)
- Benbecula Distillery (benbecula-distillery)
- Blackness Bay Distillery (blackness-bay-distillery)
- Bladnoch Distillery (bladnoch-distillery)
- Bonnington (bonnington)
- Bruichladdich Distillery (bruichladdich-distillery)
- Burnobennie Distillery (burnobennie-distillery)
- Clydeside Distillery (clydeside-distillery)
- Daftmill Distillery (daftmill-distillery)
- Deerness Distillery (deerness-distillery)
- Dornoch Distillery (dornoch-distillery)
- Dunphail distillery (dunphail-distillery)
- Eden Mill St Andrews (eden-mill-st-andrews)
- Edradour Distillery (edradour-distillery)
- Falkirk Distillery (falkirk-distillery)
- Galloway distillery (galloway-distillery)
- Glasgow Distillery (glasgow-distillery)
- Glen Grant Distillery (glen-grant-distillery)
- GlenAllachie Distillery (glenallachie-distillery)
- Glenfarclas Distillery (glenfarclas-distillery)
- GlenWyvis Distillery (glenwyvis-distillery)
- Holyrood Distillery (holyrood-distillery)
- InchDairnie Distillery (inchdairnie-distillery)
- Isle of Harris Distillery (isle-of-harris-distillery)
- Isle of Raasay Distillery (isle-of-raasay-distillery)
- Isle of Tiree distillery (isle-of-tiree-distillery)
- Jackton Distillery (jackton-distillery)
- Kilchoman Distillery (kilchoman-distillery)
- Kingsbarns Distillery (kingsbarns-distillery)
- Kythe Distillery (kythe-distillery)
- Lerwick Distillery (lerwick-distillery)
- Lindores Abbey Distillery (lindores-abbey-distillery)
- Lochlea Distillery (lochlea-distillery)
- Moffat distillery (moffat-distillery)
- Nc’nean Distillery (ncnean-distillery)
- North Point Distillery (north-point-distillery)
- North Uist Distillery (north-uist-distillery)
- Port of Leith distillery (port-of-leith-distillery)
- Stannergill Distillery (stannergill-distillery)
- Stirling distillery (stirling-distillery)
- Strathearn Distillery (strathearn-distillery)
- The Borders Distillery (the-borders-distillery)
- The Cabrach Distillery (the-cabrach-distillery)
- The Glenturret Distillery (the-glenturret-distillery)
- The Orkney Distillery (the-orkney-distillery)
- Tomatin Distillery (tomatin-distillery)
- Tormore Distillery (tormore-distillery)
- Toulvaddie Distillery (toulvaddie-distillery)
- Tullibardine Distillery (tullibardine-distillery)
- Uile-bheist Distillery (uile-bheist-distillery)
- Wolfburn Distillery (wolfburn-distillery)

## Human look

- **Macdonald & Muir / Ardbeg / Glenmorangie.** The corrected PSC file now stops at LVMH. They are their own two-site group, not Diageo.
- **Newbridge Bond** is a Brown-Forman warehouse row, not a still. It is in the Brown-Forman four because the crosswalk row is high-confidence and the controller already has whisky-signal sites. A human may drop it.
- **Ian Macleod Distillers Ltd** is a name-match HQ row with an empty description and a whisky category verdict. Same treatment.
- **Speymalt / Gordon & MacPhail.** Benromach is a matched one-site controller (independent). The Cairn is empty-description and was not group-filled — it is not one of the six named malt restorations. Including it would invent a fifteenth group the README does not carry.
