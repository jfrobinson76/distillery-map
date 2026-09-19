# Ownership data audit — September 2026

## 1. Verdict

**Do not publish the four numbers as they stand:** 176 includes non-whisky premises, a duplicate and a closed plant, while omitting operating distilleries.
**Recomputed, conditional mapped inventory: 161 named distilleries, 99 in 19 multi-distillery groups, one separately counted joint venture, and 61 residual sites—not 61 verified independents.**
**Diageo: 31 commercial distilleries, approximately one in five; “half independent” is unsupported.** Strict SWA-list reconciliation gives 155 / 97 / 19 / 29 respectively; these are different scopes, not competing exact national censuses.

Audit date: 19 September 2026. Audited data and claim: `dae51805fc2f0367cebee6d36a42c5bff1085537` on `viz/ownership-map`, PR #35. The requested brief was absent from that branch and was read from `origin/main`, commit `6f32442`. The working branch subsequently advanced to `e2c43a8`; a comparison found the three input datasets and category files unchanged (the ownership display palette changed). This report is deliberately pinned to the reviewed revision. No data, category verdict, ownership file, builder script, or artwork has been changed.

“Operating” below ordinarily means listed in the September 2026 SWA operating inventory, not a personal observation of running stills on 19 September. Six additional established/commissioned plants are retained in a separately identified scenario. Unknowns are not silently converted into independent owners.

## 2. Disagreements

Effects are against the reviewed build. G means its multi-distillery-group bucket, I its alleged-independent bucket, T the total. Effects across rows are not all additive: a new second distillery also reclassifies its already-present sibling. The complete reconciliation and executable calculation below resolve those interactions.

| Slug | Build says | Audit finding | Outside source | Effect |
| --- | --- | --- | --- | --- |
| `glencadam-distillery` | Independent | Angus Dundee also operates omitted Tomintoul. | [source](https://www.angusdundee.co.uk/) | I −1; G +1 (before interacting exclusions/additions) |
| `benromach` | Independent | Gordon & MacPhail also operates omitted Cairn. | [source](https://www.gordonandmacphail.com/corporate/our-brands) | I −1; G +1 (before interacting exclusions/additions) |
| `glenrothes-distillery` | Independent | Edrington plant; supplied chain terminates on unpadded Scottish company number with error. | [source](https://www.edrington.com/en/brands) | I −1; G +1 (before interacting exclusions/additions) |
| `glengyle` | Independent | J & A Mitchell also operates Springbank. | [source](https://kilkerran.scot/) | I −1; G +1 (before interacting exclusions/additions) |
| `auchentoshan-distillery` | Independent | Suntory lists this plant; matched SC511856 is a mixed-farming company. | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) | I −1; G +1 (before interacting exclusions/additions) |
| `torabhaig` | Independent | Mossburn also operates Reivers. | [source](https://mossburndistillers.com/projects/) | I −1; G +1 (before interacting exclusions/additions) |
| `diageo-global-supply-centre` | Included; Diageo | Leven is not one of Diageo’s 31 commercial Scotch distilleries; experimental distilling is reported, so this is a scope exclusion, not proof that no still exists. | [source](https://www.diageo.com/en/our-brands/scotch-whisky) | T −1; G −1 |
| `craigellachie` | Independent | Bacardi lists this distillery; name-matched CRAIGELLACHIE LIMITED is not evidence of its operator. | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) | I −1; G +1 (before interacting exclusions/additions) |
| `greenock-distillery` | Included; independent | Titan Spirits is a rum operation, not evidence of Scotch whisky production. | [source](https://titanspiritsltd.com/) | T −1; I −1 |
| `north-british-distillery` | Independent | Joint venture, not independent; count once. | [source](https://find-and-update.company-information.service.gov.uk/company/SC141866/persons-with-significant-control) | I −1; JV +1 (before interacting exclusions/additions) |
| `starlaw-distillery` | Independent | La Martiniquaise; same production plant as Glen Turner alias. | [source](https://ceed-scotland.com/member/glen-turner-distillery-ltd) | I −1; G +1 (before interacting exclusions/additions) |
| `deeside-distillery` | Included; independent | Lost Loch Spirits produces other spirits; do not confuse this row with omitted Burn o’Bennie. | [source](https://lostlochspirits.com/) | T −1; I −1 |
| `persie-distillery` | Included; independent | Simon and Chrissie Fairclough run Persie; its own account treats whisky as a future possibility. | [source](https://www.persiedistillery.com/team/) | T −1; I −1 |
| `kinrara-distillery` | Included; independent | Kinrara’s own offer describes gin, not on-site Scotch whisky production. | [source](https://www.kinraradistillery.com/) | T −1; I −1 |
| `stirling-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `uile-bheist-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `city-of-aberdeen-distillery` | Included; independent | City of Aberdeen operates a gin distillery and gin school. | [source](https://cityofaberdeendistillery.co.uk/) | T −1; I −1 |
| `glen-turner-distillery` | Included; La Martiniquaise | Glen Turner’s Bathgate distillery is Starlaw; retain starlaw-distillery once, not a second plant under the operator name. | [source](https://ceed-scotland.com/member/glen-turner-distillery-ltd) | T −1; G −1 |
| `ogilvy-distillery` | Included; independent | Graeme Jarron and Caroline Bruce-Jarron run the potato-vodka business. | [source](https://ogilvyspirits.com/) | T −1; I −1 |
| `deerness-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `the-cairn` | Omitted | SWA-listed operating distillery; Gordon & MacPhail | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf); [source](https://www.gordonandmacphail.com/corporate/our-brands) | T +1; group/residual per ledger |
| `highland-boundary-wild-distillery` | Included; independent | Marian and Simon’s Highland Boundary makes botanical spirits and liqueurs; whisky cocktail references are not whisky distilling. | [source](https://highlandboundary.com/pages/about-us) | T −1; I −1 |
| `jackton-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `speyside-distillery` | Included; independent | The operator announced closure in May 2025 and plans for a new site. | [source](https://speysidedistillery.co.uk/news/33/34/Speyside-Distillery-A-lost-distillery) | T −1; I −1 |
| `tomintoul-distillery` | Omitted | SWA-listed operating distillery; Angus Dundee | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf); [source](https://www.angusdundee.co.uk/) | T +1; group/residual per ledger |
| `isle-of-bute-distillery` | Included; independent | The distillery’s own products establish gin, not whisky production. | [source](https://isleofbutedistillery.com/) | T −1; I −1 |
| `the-machrihanish-distillery` | Included; independent | R&B Distillers (SC483145, also Raasay) advertises this as coming soon; not an independent operating whisky site. | [source](https://machrihanishdistillery.com/) | T −1; I −1 |
| `isle-of-cumbrae-distillers` | Included; independent | Gin is distilled here; selling Lion Rock blended malt does not establish whisky distillation. | [source](https://isleofcumbrae-distillers.com/) | T −1; I −1 |
| `linlithgow-distillery` | Included; independent | Gin distillery with sourced whisky and retirement/closure messaging; not the reopened Rosebank plant. | [source](https://www.linlithgowdistillery.uk/) | T −1; I −1 |
| `blackness-bay-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `luss-distillery` | Included; independent | Loch Lomond Group runs Luss; gin is made here while the whisky comes from Alexandria. | [source](https://lussdistillery.com/) | T −1; I −1 |
| `newbridge-bond-the-benriach-distillery-company-limited` | Included; Brown-Forman | Brown-Forman group premises at Newbridge are bottling/bond facilities, not a fourth whisky distillery. | [source](https://www.glenglassaugh.com/benriach-announces-record-profits-and-new-25-million-investment/) | T −1; G −1 |
| `57-skye-distillery` | Included; independent | Seumas Gorman and Seamus O’Baoighill run the gin/liqueur operation; blending or finishing whisky is not whisky distilling. | [source](https://57skyedistillery.com/about_us/) | T −1; I −1 |
| `isle-of-skye-distillers` | Included; independent | Whisky facilities are described as a development project; a planned start is not a verified commissioning date. | [source](https://isleofskyedistillers.com/news/) | T −1; I −1 |
| `great-glen-distillery-scotlands-smallest-craft-distillery` | Included; independent | Great Glen Distillery Ltd markets its gin operation; no whisky-production evidence found. | [source](https://www.greatglendistillery.co.uk/) | T −1; I −1 |
| `dunkeld-distillery` | Included; independent | Own site prioritises gin while describing whisky ambitions; first whisky spirit not verified. | [source](https://dunkelddistillery.com/) | T −1; I −1 |
| `tayport-distillery` | Included; independent | Duncan, Ally and Kecia’s family business makes gin, vodka and liqueurs, not demonstrated Scotch whisky. | [source](https://www.tayportdistillery.com/) | T −1; I −1 |
| `burnobennie-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `isle-of-barra-distillers` | Included; independent | Own whisky distillery remains a construction project; existing whisky sales do not prove distillation here. | [source](https://isleofbarradistillers.com/pages/barra-whisky) | T −1; I −1 |
| `stornoway-distillers-co` | Included; independent | Stornoway Distillers operates gin production and a gin school; no whisky-production evidence found. | [source](https://stornowaydistillers.com/) | T −1; I −1 |
| `rhidorroch-distillery-cafe-bar-eatery` | Included; independent | Katie and Lawrie run a gin distillery with café/bar; it is not merely a café, but not a demonstrated whisky distillery either. | [source](https://rhidorrochdistillery.co.uk/) | T −1; I −1 |
| `north-point-distillery` | Omitted | SWA-listed operating distillery; ownership remains residual | [source](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) | T +1; group/residual per ledger |
| `ian-macleod-distillers-ltd` | Included; Ian Macleod | The Broxburn company/HQ row is not a separate whisky still; the group’s actual plants are counted individually. | [source](https://www.ianmacleod.com/) | T −1; G −1 |
| `springbank-distillery` | Independent | Same operating group as Glengyle, despite separate companies. | [source](https://kilkerran.scot/) | I −1; G +1 (before interacting exclusions/additions) |
| `laggan-bay-distillery` | Independent | Ian Macleod / Russell family fourth whisky plant. | [source](https://www.lagganbay.com/) | I −1; G +1 (before interacting exclusions/additions) |
| `reivers-distillery` | Independent | Mossburn also operates Torabhaig. | [source](https://mossburndistillers.com/projects/) | I −1; G +1 (before interacting exclusions/additions) |
| `loch-lomond-distillery` | One distillery | Separate named malt and grain production units; Luss is gin and is not the missing Scotch unit. | [source](https://www.lochlomondgroup.com/pages/who-we-are) | T +1; G +1 under named-distillery definition |
| `ben-nevis-distillery` | Independent; Demball terminal | Nikka parent; still one Scotch distillery in the narrow count. | [source](https://www.nikka.com/en/about/) | No multi-Scotch arithmetic change; independence claim fails |
| `bruichladdich-distillery` / `glen-grant-distillery` / `bonnington` | Independent | Rémy Cointreau / Campari / Halewood affiliations; singleton is not economic independence. | [source](https://www.bruichladdich.com/pages/faqs); [source](https://www.camparigroup.com/it/pages/brands); [source](https://crabbiewhisky.com/privacy-and-cookie-policy/) | Residual category requires relabelling |
| `glenglassaugh-distillery` | Operating Brown-Forman member | Ownership supported; operating-list status conflicts with reported production pause. | [source](https://www.thespiritsbusiness.com/2025/01/glenglassaugh-pauses-production/?edition=asia) | 0 in listed/commissioned scenario; T/G −1 if paused excluded |
| `bunnahabhain-distillery` / `deanston-distillery` / `tobermory-distillery` | Distell terminal | CVH/Capevin, not assumed Heineken; minority Campari stake does not establish common control. | [source](https://tobermorydistillery.com/en-us/pages/modern-slavery-statement) | Label/control evidence correction; no 3-site count change |


### Why the denominator is not “176 ±5”

The [September SWA list](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) enumerates 155 distilleries, corresponding to 154 map records because Loch Lomond malt and grain share one record. Of those records, 145 are in the build and nine are missing. The build also contains 31 records absent from that list. This audit excludes 25 of those 31 and retains six in the commissioned-plant scenario: Abhainn Dearg, Eden Mill, Stannergill, Kythe, Glen Spey and Strathmill. Thus **176 − 25 + 9 = 160 map records; counting Loch Lomond’s two named production units gives 161 distilleries.**

This is not an exhaustive national census. [Levenbank](https://www.levenbank.com/blog) reports distilling during 2025 but is absent from the map; its [operator](https://www.levenbank.com/) is the Loch Lomond **Brewery** team, which must not be merged into Loch Lomond Group on name similarity. Adding this documented external omission gives at least 162 named candidates in the broader commissioned inventory, subject to current operating-status checks. The arbitrary Shetland latitude exclusion also has no place in a Scotland-wide definition: [Lerwick's operator](https://shetlandwhisky.com/pages/our-journey) describes its project, but the reviewed evidence did not establish a first-spirit date. It remains an explicit coverage question.

Brora, Port Ellen and Rosebank belong in the reopened population. The Lost Distillery Company whisky lounge, Gordon & MacPhail's office, and Johnnie Walker Princes Street were already excluded: they do **not** explain the excess. `black-friars-distillery` and Warner’s are outside this 176-row Scottish set; this audit does not validate any English-company linkage merely because it has no effect on the Scotch count.

## 3. Recomputed figures and definitions

A counted unit is a named Scotch malt or grain production distillery, including commissioned new-make production before its first three-year-old release. It is not a brand, visitor centre, corporate registration, bottling line or warehouse. Separate named plants at a common complex are counted separately: Loch Lomond malt/grain, Ailsa Bay/Girvan, and Kininvie/Balvenie. Therefore do not relabel these numbers as unique geographic premises.

A **multi-distillery group** is an evidenced common operating/ownership group controlling at least two counted Scotch distilleries. Family businesses qualify. North British is a separate **joint venture**, counted once, never credited in full to both parents and never treated as independent merely because its controller string occurs once. A **residual site** has no second Scotch plant assigned to its operator in this audit; that is not a finding of economic independence. In particular Ben Nevis/Nikka, Bruichladdich/Rémy Cointreau, Glen Grant/Campari and Bonnington/Halewood demonstrate the difference.

| Scope | Total | Multi-distillery group-run | Joint venture | Residual, not proven independent | Groups ≥2 | Diageo |
| --- | --- | --- | --- | --- | --- | --- |
| September SWA list | 155 | 97 | 1 | 57 | 19 | 29 |
| Commissioned mapped inventory | 161 | 99 | 1 | 61 | 19 | 31 |


The 61 residuals are an **upper bound on the build-style single-Scotch-site category**, not a verified independence percentage. They are 37.9% of 161; the comparable strict-list residual is 57/155 = 36.8%. Even that residual contains multinational subsidiaries and unresolved ownership. “Roughly half independent” cannot be rescued by treating unmatched records as small businesses. No precise count of economically independent enterprises is certified here.

Sensitivity: excluding Glenglassaugh's reported pause and the two Diageo plants missing from the SWA list reduces the commissioned scenario to **158 total, 96 grouped, one JV, 61 residual, 19 groups, Diageo 29**. This 158–161 interval is a **status sensitivity within the reconstructed map inventory**, not a national confidence interval. Levenbank and any other missing producers sit outside it.

| Audited operating group | Named distilleries |
| --- | --- |
| Diageo | 31 |
| Pernod Ricard | 13 |
| Bacardi | 5 |
| Inver House | 5 |
| Suntory | 5 |
| Whyte & Mackay | 5 |
| William Grant | 5 |
| Ian Macleod | 4 |
| Brown-Forman | 3 |
| CVH / Capevin | 3 |
| Edrington | 3 |
| Loch Lomond | 3 |
| Angus Dundee | 2 |
| Gordon & MacPhail | 2 |
| Isle of Arran | 2 |
| J & A Mitchell | 2 |
| LVMH | 2 |
| La Martiniquaise | 2 |
| Mossburn | 2 |


### Diageo: name-by-name check of the claimed 32

| Claimed name | Audit |
| --- | --- |
| Auchroisk distillery | Retain |
| Benrinnes Distillery | Retain |
| Blair Athol Distillery | Retain |
| Brora Distillery | Retain |
| Cameronbridge Distillery | Retain |
| Caol Ila Distillery | Retain |
| Cardhu Distillery | Retain |
| Clynelish Distillery | Retain |
| Cragganmore Distillery | Retain |
| Dailuaine | Retain |
| Dalwhinnie Distillery | Retain |
| Dufftown distillery | Retain |
| Glen Elgin Distillery | Retain |
| Glen Ord Distillery | Retain |
| Glen Spey Distillery | Retain; current production unresolved |
| Glendullan Distillery | Retain |
| Glenkinchie Distillery | Retain |
| Glenlossie | Retain |
| Inchgower Distillery | Retain |
| Knockando Distillery | Retain |
| Lagavulin Distillery | Retain |
| Leven Distillery (Diageo) | Exclude Leven from commercial count |
| Linkwood distillery | Retain |
| Mannochmore Distillery | Retain |
| Mortlach Distillery | Retain |
| Oban Distillery | Retain |
| Port Ellen Distillery | Retain |
| Roseisle | Retain |
| Royal Lochnagar Distillery | Retain |
| Strathmill | Retain; current production unresolved |
| Talisker Distillery | Retain |
| Teaninich Distllery | Retain |


The [Diageo Scotch page](https://www.diageo.com/en/our-brands/scotch-whisky) states 31 owned Scotch whisky distilleries. Its [2017 published map](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) already includes Roseisle among the 28 malt distilleries, plus Cameronbridge grain. Add reopened Brora and Port Ellen to reach 31. Adding Roseisle again, as the arithmetic suggested in the brief could do, double-counts it. The build's additional name is Leven. Experimental distilling has been reported there; the commercial-site definition excludes it without claiming it is only a warehouse or that its stills do not exist. No missing commercial Diageo name was identified against those lists. North British remains a separately counted JV.

31/161 = 19.3%, so “about one in five” survives this scope. The stricter SWA-list subset has 29 Diageo entries because Glen Spey and Strathmill are missing from that list. Their [Diageo](https://www.malts.com/en-gb/products/glen-spey-12-year-old-flora-fauna-single-malt-whisky-70cl) [brand pages](https://www.malts.com/en-gb/products/strathmill-12-year-old-flora-and-fauna-single-malt-whisky-70cl) establish the association, not current production; absence from SWA alone is not proof of closure.

### Five PSC chains re-walked on the public register

These are observations of live public pages, not merely repetitions of `psc-parents.csv`. Links identify each visited stage. A stop at joint control or at individuals is the end of the control chain for this audit; it is not evidence that no wider business group exists.

| Chain | Public-register walk and finding | Audit implication |
|---|---|---|
| Macdonald & Muir / Ardbeg | [SC019038](https://find-and-update.company-information.service.gov.uk/company/SC019038/persons-with-significant-control) → [Glenmorangie SC026752](https://find-and-update.company-information.service.gov.uk/company/SC026752/persons-with-significant-control) → LVMH, with the higher >50–<75% band; Diageo is in the >25–≤50% band. | Highest-band choice is supported in this case. Do not assign Ardbeg or Glenmorangie to Diageo. |
| North British | [SC001491](https://find-and-update.company-information.service.gov.uk/company/SC001491/persons-with-significant-control) → [Lothian SC141866](https://find-and-update.company-information.service.gov.uk/company/SC141866/persons-with-significant-control) → Edrington Distillers Group SC017727 and Diageo Great Britain 00507652, each in the 25–50% band. | Joint control is recorded correctly upstream but loses its meaning when a singleton controller is rendered independent. The bands alone do not establish an exact 50/50 split. Count one JV. |
| Benromach | [SC437374](https://find-and-update.company-information.service.gov.uk/company/SC437374/persons-with-significant-control) → [Speymalt SC037522](https://find-and-update.company-information.service.gov.uk/company/SC037522/persons-with-significant-control) → no registrable PSC statement. | Stop is not proof of a one-distillery business. [Gordon & MacPhail](https://www.gordonandmacphail.com/corporate/our-brands) identifies both Benromach and The Cairn. |
| Ben Nevis | [SC022667](https://find-and-update.company-information.service.gov.uk/company/SC022667/persons-with-significant-control) → [Demball 02302862](https://find-and-update.company-information.service.gov.uk/company/02302862/persons-with-significant-control) → The Nikka Whisky Distilling Co., Ltd. | File stops at Demball with `individual`; live page shows Nikka. [Nikka's account](https://www.nikka.com/en/about/) corroborates the business connection. Cache/schema cause not proven, but the terminal classification is unreliable. |
| J & A Mitchell / Springbank | [SC003582](https://find-and-update.company-information.service.gov.uk/company/SC003582/persons-with-significant-control) lists active individuals exercising significant influence/control; stop there. | An individual-controlled top can own multiple distilleries: [Kilkerran/Glengyle](https://kilkerran.scot/) identifies the J & A Mitchell connection and [Springbank](https://www.springbank.scot/about/story/) identifies the family business. Two sites, one group. |

Additional partial walk: [Glenrothes SC052114](https://find-and-update.company-information.service.gov.uk/company/SC052114/persons-with-significant-control) names BB&R Spirits; [Highland Distillers SC158731](https://find-and-update.company-information.service.gov.uk/company/SC158731/persons-with-significant-control) names 1887; [1887 SC199077](https://find-and-update.company-information.service.gov.uk/company/SC199077/persons-with-significant-control) records Edrington as `SC36374`, and [correctly padded SC036374](https://find-and-update.company-information.service.gov.uk/company/SC036374/persons-with-significant-control) leads to Kintail. BB&R's intermediate page and Kintail's terminal page could not be retrieved in this session, so this is **not** counted among the five complete walks. The crawler normalizes numeric-only IDs, leaving this Scottish number unpadded; the supplied chain ends `error` at `SC36374`. Edrington's own brand list independently resolves Glenrothes to the same group as Highland Park and Macallan.

Method defects demonstrated by the files and code:

- `none`, `error`, `max levels`, foreign stops and individual stops are different evidence states; none proves independence. A foreign parent also needs normalization across sibling companies.
- Corporate name similarity is not operator identity. [AUCHENTOSHAN LIMITED SC511856](https://find-and-update.company-information.service.gov.uk/company/SC511856) has SIC 01500, mixed farming; Suntory's own plant list identifies the whisky business. High-confidence name matching does not make this a sound link.
- The scoring rule takes the maximum band across shares and votes; these rights need not agree. It prioritizes corporate PSCs over individuals and considers only two equal-band corporate candidates. Those are method limitations, not proof that a particular unexamined chain is wrong.
- In the five complete walks, **no wrong-parent selection caused specifically by the highest-band comparison was demonstrated**. The demonstrated failures are truncation/classification, entity matching, omitted siblings and singleton interpretation. Do not overstate the evidence.
- `groups.json` is described as display-only, but the builder uses its aliases in controller grouping. Entity resolution should not depend on a presentation list. The README still carries 178/90/14/34 while the reviewed summary/card uses 176/89/15/32; neither is an independent validation of the other.

## 4. What remains unverified

1. Current production at Glen Spey, Strathmill and Glenglassaugh. The latter remains on the SWA list despite a [reported January 2025 pause](https://www.thespiritsbusiness.com/2025/01/glenglassaugh-pauses-production/?edition=asia). The report does not certify a restart.
2. Exact September operating continuity and current parent at Eden Mill following its 2025 operational restart and subsequently reported ownership changes. The old Inverleith chain is not a current ownership certification.
3. First whisky spirit at Isle of Skye Distillers, Dunkeld and Lerwick; project/cask-sale language is insufficient. [Portintruan's operator](https://elixirdistillers.com/distilleries) describes development toward production; Tormore is not moved into a two-operating-site group without proof of Portintruan's commissioning.
4. Ultimate legal/beneficial ownership at Ardross, Ballindalloch, Falkirk, Galloway and several other unmatched businesses. Their own sites can identify an operating business without proving the full control chain. The 28-row review below records those limits explicitly.
5. Current complete national coverage beyond the map, including Levenbank and other recent projects. The 161-row-unit scenario must not be published as a certified exhaustive Scottish total.
6. Exact legal reason for Demball's `individual` stop; raw current API classification was not independently captured. Selected CH pages failed to load (including the additional BB&R/Kintail stages and attempted Angus Dundee subsidiary pages). Operator evidence supports the business grouping but does not pretend those missing register checks succeeded.
7. Independence of every residual owner: this is a targeted audit, not a beneficial-ownership certification of all companies. The 28 unmatched review plus the matched sample exceeds the required sample size, but uncrossed individual holdings may still hide more groups.
8. Warner’s English PSC chain is outside the counted population and was not re-walked. No Scotch-count correction is attributed to it.

## Appendix A — every one of the 176 entries, plus nine omitted SWA records

`In build` is comparison metadata. `Units` is the audit contribution (zero for exclusions, two for Loch Lomond malt/grain). The SWA source establishes operating-list status; the separate group-membership appendix establishes ownership for each of the 89 group assignments. A listed operation can be temporarily paused: see the explicit Glenglassaugh exception. No category-model verdict alone establishes whisky production.

| Slug | In build | Status / classification | Units | Audit group or residual | Status evidence |
| --- | --- | --- | --- | --- | --- |
| `57-skye-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://57skyedistillery.com/about_us/) |
| `8-doors-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `aberargie-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `aberfeldy-distillery` | yes | operating (SWA) | 1 | Bacardi | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `aberlour-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `abhainn-dearg-distillery` | yes | commissioned; outside SWA list | 1 | residual | [operator / evidence](https://abhainndeargdistillery.co.uk/) |
| `ailsa-bay` | yes | operating (SWA) | 1 | William Grant | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `allt-a-bhainne` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ancnoc-distillery` | yes | operating (SWA) | 1 | Inver House | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `annandale-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `arbikie-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardbeg` | yes | operating (SWA) | 1 | LVMH | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardgowan-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardmore-distillery` | yes | operating (SWA) | 1 | Suntory | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardnahoe-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardnamurchan-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ardross-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `arran-distillery` | yes | operating (SWA) | 1 | Isle of Arran | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `auchentoshan-distillery` | yes | operating (SWA) | 1 | Suntory | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `auchroisk-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `aultmore-distillery` | yes | operating (SWA) | 1 | Bacardi | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `badachro-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `balblair-distillery` | yes | operating (SWA) | 1 | Inver House | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ballindalloch-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `balmaud-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `balmenach-distillery` | yes | operating (SWA) | 1 | Inver House | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `balvenie-distillery` | yes | operating (SWA) | 1 | William Grant | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ben-nevis-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `benbecula-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `benriach-distillery` | yes | operating (SWA) | 1 | Brown-Forman | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `benrinnes-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `benromach` | yes | operating (SWA) | 1 | Gordon & MacPhail | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `blackness-bay-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `bladnoch-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `blair-athol-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `bonnington` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `bowmore-distillery` | yes | operating (SWA) | 1 | Suntory | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `braeval-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `brora-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `bruichladdich-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `bunnahabhain-distillery` | yes | operating (SWA) | 1 | CVH / Capevin | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `burnobennie-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `cameronbridge-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `caol-ila-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `cardhu-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `city-of-aberdeen-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://cityofaberdeendistillery.co.uk/) |
| `clydeside-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `clynelish-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `cragganmore-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `craigellachie` | yes | operating (SWA) | 1 | Bacardi | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `daftmill-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dailuaine` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dalmore-distillery` | yes | operating (SWA) | 1 | Whyte & Mackay | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dalmunach-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dalwhinnie-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `deanston-distillery` | yes | operating (SWA) | 1 | CVH / Capevin | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `deerness-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `deeside-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://lostlochspirits.com/) |
| `diageo-global-supply-centre` | yes | research / packaging, excluded | 0 | Diageo | [operator / evidence](https://www.diageo.com/en/our-brands/scotch-whisky) |
| `dornoch-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dufftown-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `dunkeld-distillery` | yes | not yet producing (unconfirmed) | 0 | residual | [operator / evidence](https://dunkelddistillery.com/) |
| `dunphail-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `eden-mill-st-andrews` | yes | commissioned; outside SWA list | 1 | residual | [operator / evidence](https://www.edenmill.com/blogs/distillery/we-are-now-operational) |
| `edradour-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `falkirk-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `fettercairn-distillery` | yes | operating (SWA) | 1 | Whyte & Mackay | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `galloway-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `girvan-distillery` | yes | operating (SWA) | 1 | William Grant | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glasgow-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-elgin-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-garioch-distillery` | yes | operating (SWA) | 1 | Suntory | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-grant-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-keith-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-moray-distillery` | yes | operating (SWA) | 1 | La Martiniquaise | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-ord-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-scotia-distillery` | yes | operating (SWA) | 1 | Loch Lomond | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glen-spey-distillery` | yes | commissioned; outside SWA list | 1 | Diageo | [operator / evidence](https://www.malts.com/en-gb/products/glen-spey-12-year-old-flora-fauna-single-malt-whisky-70cl) |
| `glen-turner-distillery` | yes | duplicate | 0 | La Martiniquaise | [operator / evidence](https://ceed-scotland.com/member/glen-turner-distillery-ltd) |
| `glenallachie-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenburgie-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glencadam-distillery` | yes | operating (SWA) | 1 | Angus Dundee | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glendullan-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenfarclas-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenfiddich-distillery` | yes | operating (SWA) | 1 | William Grant | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenglassaugh-distillery` | yes | operating list; reported production pause | 1 | Brown-Forman | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glengoyne-distillery` | yes | operating (SWA) | 1 | Ian Macleod | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glengyle` | yes | operating (SWA) | 1 | J & A Mitchell | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenkinchie-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenlossie` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenmorangie-distillery` | yes | operating (SWA) | 1 | LVMH | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenrothes-distillery` | yes | operating (SWA) | 1 | Edrington | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glentauchers-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `glenwyvis-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `great-glen-distillery-scotlands-smallest-craft-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://www.greatglendistillery.co.uk/) |
| `greenock-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://titanspiritsltd.com/) |
| `highland-boundary-wild-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://highlandboundary.com/pages/about-us) |
| `highland-park-distillery` | yes | operating (SWA) | 1 | Edrington | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `holyrood-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ian-macleod-distillers-ltd` | yes | office | 0 | Ian Macleod | [operator / evidence](https://www.ianmacleod.com/) |
| `inchdairnie-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `inchgower-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `invergordon-distillery` | yes | operating (SWA) | 1 | Whyte & Mackay | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `isle-of-barra-distillers` | yes | not yet producing | 0 | residual | [operator / evidence](https://isleofbarradistillers.com/pages/barra-whisky) |
| `isle-of-bute-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://isleofbutedistillery.com/) |
| `isle-of-cumbrae-distillers` | yes | gin / other | 0 | residual | [operator / evidence](https://isleofcumbrae-distillers.com/) |
| `isle-of-harris-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `isle-of-jura-distillery` | yes | operating (SWA) | 1 | Whyte & Mackay | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `isle-of-raasay-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `isle-of-skye-distillers` | yes | not yet producing (unconfirmed) | 0 | residual | [operator / evidence](https://isleofskyedistillers.com/news/) |
| `isle-of-tiree-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `jackton-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `kilchoman-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `kingsbarns-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `kininvie-distillery` | yes | operating (SWA) | 1 | William Grant | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `kinrara-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://www.kinraradistillery.com/) |
| `knockando-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `kythe-distillery` | yes | commissioned; outside SWA list | 1 | residual | [operator / evidence](https://kythedistillery.com/) |
| `lagavulin-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `lagg-distillery` | yes | operating (SWA) | 1 | Isle of Arran | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `laggan-bay-distillery` | yes | operating (SWA) | 1 | Ian Macleod | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `laphroaig-distillery` | yes | operating (SWA) | 1 | Suntory | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `lindores-abbey-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `linkwood-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `linlithgow-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://www.linlithgowdistillery.uk/) |
| `loch-lomond-distillery` | yes | operating (SWA) | 2 | Loch Lomond | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `lochlea-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `longmorn-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `luss-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://lussdistillery.com/) |
| `macduff-distillery` | yes | operating (SWA) | 1 | Bacardi | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `mannochmore-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `miltonduff-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `moffat-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `mortlach-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ncnean-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `newbridge-bond-the-benriach-distillery-company-limited` | yes | warehouse / bottling | 0 | Brown-Forman | [operator / evidence](https://www.glenglassaugh.com/benriach-announces-record-profits-and-new-25-million-investment/) |
| `north-british-distillery` | yes | operating (SWA) | 1 | JV | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `north-point-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `north-uist-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `oban-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `ogilvy-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://ogilvyspirits.com/) |
| `persie-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://www.persiedistillery.com/team/) |
| `port-ellen-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `port-of-leith-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `pulteney-distillery` | yes | operating (SWA) | 1 | Inver House | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `reivers-distillery` | yes | operating (SWA) | 1 | Mossburn | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `rhidorroch-distillery-cafe-bar-eatery` | yes | gin / other | 0 | residual | [operator / evidence](https://rhidorrochdistillery.co.uk/) |
| `rosebank-distillery` | yes | operating (SWA) | 1 | Ian Macleod | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `roseisle` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `royal-brackla` | yes | operating (SWA) | 1 | Bacardi | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `royal-lochnagar-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `scapa-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `speyburn-glenlivet-distillery` | yes | operating (SWA) | 1 | Inver House | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `speyside-distillery` | yes | closed | 0 | residual | [operator / evidence](https://speysidedistillery.co.uk/news/33/34/Speyside-Distillery-A-lost-distillery) |
| `springbank-distillery` | yes | operating (SWA) | 1 | J & A Mitchell | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `stannergill-distillery` | yes | commissioned; outside SWA list | 1 | residual | [operator / evidence](https://www.thespiritsbusiness.com/2026/07/stannergill-distillery-starts-production/) |
| `starlaw-distillery` | yes | operating (SWA) | 1 | La Martiniquaise | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `stirling-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `stornoway-distillers-co` | yes | gin / other | 0 | residual | [operator / evidence](https://stornowaydistillers.com/) |
| `strathclyde-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `strathearn-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `strathisla-distillery` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `strathmill` | yes | commissioned; outside SWA list | 1 | Diageo | [operator / evidence](https://www.malts.com/en-gb/products/strathmill-12-year-old-flora-and-fauna-single-malt-whisky-70cl) |
| `talisker-distillery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tamdhu-distillery` | yes | operating (SWA) | 1 | Ian Macleod | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tamnavulin-distillery` | yes | operating (SWA) | 1 | Whyte & Mackay | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tayport-distillery` | yes | gin / other | 0 | residual | [operator / evidence](https://www.tayportdistillery.com/) |
| `teaninich-distllery` | yes | operating (SWA) | 1 | Diageo | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-borders-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-cabrach-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-cairn` | no | operating (SWA) | 1 | Gordon & MacPhail | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-glendronach-distillery` | yes | operating (SWA) | 1 | Brown-Forman | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-glenlivet` | yes | operating (SWA) | 1 | Pernod Ricard | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-glenturret-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-macallan-distillery` | yes | operating (SWA) | 1 | Edrington | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `the-machrihanish-distillery` | yes | not yet producing | 0 | residual | [operator / evidence](https://machrihanishdistillery.com/) |
| `the-orkney-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tobermory-distillery` | yes | operating (SWA) | 1 | CVH / Capevin | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tomatin-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tomintoul-distillery` | no | operating (SWA) | 1 | Angus Dundee | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `torabhaig` | yes | operating (SWA) | 1 | Mossburn | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tormore-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `tullibardine-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `uile-bheist-distillery` | no | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |
| `wolfburn-distillery` | yes | operating (SWA) | 1 | residual | [SWA](https://www.scotch-whisky.org.uk/media/f2fm4u0u/list-of-current-operating-scotch-whisky-distilleries-for-public-website-september-2026.pdf) |


## Appendix B — all 28 unmatched records

Each row identifies the operator to the extent its own site supports it, without equating a missing match with independence. The named founders or team are not automatically asserted to be the legal ultimate controllers.

| Slug | Operator finding | Own-site / company evidence | Treatment |
| --- | --- | --- | --- |
| `57-skye-distillery` | Seumas Gorman and Seamus O’Baoighill run the gin/liqueur operation; blending or finishing whisky is not whisky distilling. | [source](https://57skyedistillery.com/about_us/) | Exclude: gin / other |
| `8-doors-distillery` | Kerry and Derek Campbell founded and run 8 Doors, an operating whisky distillery. | [source](https://www.8doorsdistillery.com/) | Residual; independence not certified |
| `aberargie-distillery` | Morrison Distillers operates Aberargie; no inference of shared ownership with Clydeside is made merely from the Morrison surname. | [source](https://www.morrisondistillers.com/distillery) | Residual; independence not certified |
| `abhainn-dearg-distillery` | Mark Tayburn established Abhainn Dearg, whose own site describes whisky production. | [source](https://abhainndeargdistillery.co.uk/) | Residual; independence not certified |
| `ardross-distillery` | Ardross’s own site identifies its distillery team and chairman Andrew Rankin; the ultimate beneficial owner was not independently established. | [source](https://theardross.com/) | Residual; independence not certified |
| `ballindalloch-distillery` | Ballindalloch presents itself as a family-owned estate distillery; the precise legal operator remains unverified here. | [source](https://www.ballindallochdistillery.com/) | Residual; independence not certified |
| `benbecula-distillery` | Founder Angus MacMillan’s Benbecula operation belongs to the MacMillan spirits business. | [source](https://benbeculadistillery.com/home-2-2/) | Residual; independence not certified |
| `bonnington` | John Crabbie’s Bonnington operation is linked to Halewood by its own legal notice, corroborating the separately published Halewood ownership attribution. | [source](https://crabbiewhisky.com/privacy-and-cookie-policy/) | Residual; independence not certified |
| `daftmill-distillery` | Francis and Ian Cuthbert run the farm distillery at Daftmill. | [source](https://www.daftmill.com/our-distillery/) | Residual; independence not certified |
| `falkirk-distillery` | Falkirk’s own story describes the family operation and its new-make production; its ultimate legal control chain has not been established by this audit. | [source](https://www.falkirkdistillery.com/our-story-home) | Residual; independence not certified |
| `galloway-distillery` | The former Crafty site now trades as Galloway Distillery; its own account names Sam Heughan and Alex Norouzi as its 2025 founders, while the legal control chain remains unverified. | [source](https://gallowaydistillery.com/pages/galloway-distillery) | Residual; independence not certified |
| `glenwyvis-distillery` | GlenWyvis describes a community-owned distillery, not a missing corporate match that can automatically be called independent. | [source](https://glenwyvis.com/) | Residual; independence not certified |
| `great-glen-distillery-scotlands-smallest-craft-distillery` | Great Glen Distillery Ltd markets its gin operation; no whisky-production evidence found. | [source](https://www.greatglendistillery.co.uk/) | Exclude: gin / other |
| `highland-boundary-wild-distillery` | Marian and Simon’s Highland Boundary makes botanical spirits and liqueurs; whisky cocktail references are not whisky distilling. | [source](https://highlandboundary.com/pages/about-us) | Exclude: gin / other |
| `isle-of-tiree-distillery` | Ian Smith and Alain Campbell founded Tiree Whisky Company, the operator behind Tiree’s distillery. | [source](https://www.tyreegin.com/copy-of-about) | Residual; independence not certified |
| `laggan-bay-distillery` | The Russell family’s Ian Macleod business operates Laggan Bay, its fourth whisky distillery; move this dot into that group. | [source](https://www.lagganbay.com/) | Ian Macleod |
| `luss-distillery` | Loch Lomond Group runs Luss; gin is made here while the whisky comes from Alexandria. | [source](https://lussdistillery.com/) | Exclude: gin / other |
| `ogilvy-distillery` | Graeme Jarron and Caroline Bruce-Jarron run the potato-vodka business. | [source](https://ogilvyspirits.com/) | Exclude: gin / other |
| `persie-distillery` | Simon and Chrissie Fairclough run Persie; its own account treats whisky as a future possibility. | [source](https://www.persiedistillery.com/team/) | Exclude: gin / other |
| `port-of-leith-distillery` | Muckle Brig Ltd operates Port of Leith; its Lind & Lime gin operation does not create a second Scotch whisky distillery. | [source](https://www.leithdistillery.com/) | Residual; independence not certified |
| `reivers-distillery` | Mossburn operates Reivers and Torabhaig, so Reivers is not an unmatched independent. | [source](https://mossburndistillers.com/projects/) | Mossburn |
| `rhidorroch-distillery-cafe-bar-eatery` | Katie and Lawrie run a gin distillery with café/bar; it is not merely a café, but not a demonstrated whisky distillery either. | [source](https://rhidorrochdistillery.co.uk/) | Exclude: gin / other |
| `stannergill-distillery` | Founder Martin Murray’s Stannergill at Castletown Mill describes a working whisky distillery; ultimate legal ownership has not been re-walked here. | [source](https://stannergillwhisky.co.uk/) | Residual; independence not certified |
| `starlaw-distillery` | Glen Turner / La Martiniquaise operates Starlaw; it is the same Bathgate plant as the build’s Glen Turner row. | [source](https://ceed-scotland.com/member/glen-turner-distillery-ltd) | La Martiniquaise |
| `stornoway-distillers-co` | Stornoway Distillers operates gin production and a gin school; no whisky-production evidence found. | [source](https://stornowaydistillers.com/) | Exclude: gin / other |
| `tayport-distillery` | Duncan, Ally and Kecia’s family business makes gin, vodka and liqueurs, not demonstrated Scotch whisky. | [source](https://www.tayportdistillery.com/) | Exclude: gin / other |
| `the-cabrach-distillery` | The Cabrach describes a community-interest company reinvesting its profits locally; retain the producing site without inventing a verified corporate parent. | [source](https://www.thecabrach.com/) | Residual; independence not certified |
| `the-machrihanish-distillery` | R&B Distillers (SC483145, also Raasay) advertises this as coming soon; not an independent operating whisky site. | [source](https://machrihanishdistillery.com/) | Exclude: not yet producing |


## Appendix C — outside-source check of all 89 group-run assignments

Each claimed member is listed separately. “Supported” concerns its ownership association; inclusion as an operating whisky distillery is assessed independently in Appendix A. Glen Turner is a valid group operation but duplicates Starlaw. Newbridge, the Ian Macleod office, and Leven require the separate scope corrections already described. William Grant's five named plants are corroborated by the SWA member directory, including Kininvie and the distinct Ailsa Bay/Girvan operations. LVMH ownership is also corroborated by the register walk above.

| Slug | Claimed group (normalized label) | Finding | Outside ownership evidence |
| --- | --- | --- | --- |
| `aberfeldy-distillery` | Bacardi | Supported | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) |
| `aultmore-distillery` | Bacardi | Supported | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) |
| `macduff-distillery` | Bacardi | Supported | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) |
| `royal-brackla` | Bacardi | Supported | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) |
| `benriach-distillery` | Brown-Forman | Supported | [source](https://investors.brown-forman.com/investors/news-releases/press-release/2016/Brown-Forman-Completes-Acquisition-of-The-GlenDronach-BenRiach-and-Glenglassaugh-Single-Malt-Scotch-Whiskies/default.aspx) |
| `glenglassaugh-distillery` | Brown-Forman | Supported | [source](https://investors.brown-forman.com/investors/news-releases/press-release/2016/Brown-Forman-Completes-Acquisition-of-The-GlenDronach-BenRiach-and-Glenglassaugh-Single-Malt-Scotch-Whiskies/default.aspx) |
| `newbridge-bond-the-benriach-distillery-company-limited` | Brown-Forman | Group association supported; exclude warehouse / bottling | [source](https://investors.brown-forman.com/investors/news-releases/press-release/2016/Brown-Forman-Completes-Acquisition-of-The-GlenDronach-BenRiach-and-Glenglassaugh-Single-Malt-Scotch-Whiskies/default.aspx) |
| `the-glendronach-distillery` | Brown-Forman | Supported | [source](https://investors.brown-forman.com/investors/news-releases/press-release/2016/Brown-Forman-Completes-Acquisition-of-The-GlenDronach-BenRiach-and-Glenglassaugh-Single-Malt-Scotch-Whiskies/default.aspx) |
| `bunnahabhain-distillery` | CVH / Capevin | Supported | [source](https://tobermorydistillery.com/en-us/pages/modern-slavery-statement) |
| `deanston-distillery` | CVH / Capevin | Supported | [source](https://tobermorydistillery.com/en-us/pages/modern-slavery-statement) |
| `tobermory-distillery` | CVH / Capevin | Supported | [source](https://tobermorydistillery.com/en-us/pages/modern-slavery-statement) |
| `auchroisk-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `benrinnes-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `blair-athol-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `brora-distillery` | Diageo | Supported | [source](https://www.diageo.com/en/our-brands/scotch-whisky) |
| `cameronbridge-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `caol-ila-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `cardhu-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `clynelish-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `cragganmore-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `dailuaine` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `dalwhinnie-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `dufftown-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glen-elgin-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glen-ord-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glen-spey-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glendullan-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glenkinchie-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `glenlossie` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `inchgower-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `knockando-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `lagavulin-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `diageo-global-supply-centre` | Diageo | Group association supported; exclude research / packaging, excluded | [source](https://www.diageo.com/en/our-brands/scotch-whisky) |
| `linkwood-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `mannochmore-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `mortlach-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `oban-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `port-ellen-distillery` | Diageo | Supported | [source](https://www.diageo.com/en/our-brands/scotch-whisky) |
| `roseisle` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `royal-lochnagar-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `strathmill` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `talisker-distillery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `teaninich-distllery` | Diageo | Supported | [source](https://media.diageo.com/diageo-corporate-media/media/lsudcvp0/161_john_kennedy_scotch.pdf) |
| `highland-park-distillery` | Edrington | Supported | [source](https://www.edrington.com/en/brands) |
| `the-macallan-distillery` | Edrington | Supported | [source](https://www.edrington.com/en/brands) |
| `glengoyne-distillery` | Ian Macleod | Supported | [source](https://www.ianmacleod.com/) |
| `ian-macleod-distillers-ltd` | Ian Macleod | Group association supported; exclude office | [source](https://www.ianmacleod.com/) |
| `rosebank-distillery` | Ian Macleod | Supported | [source](https://www.ianmacleod.com/) |
| `tamdhu-distillery` | Ian Macleod | Supported | [source](https://www.ianmacleod.com/) |
| `ancnoc-distillery` | Inver House | Supported | [source](https://www.interbevgroup.com/our-group/where-we-operate) |
| `balblair-distillery` | Inver House | Supported | [source](https://www.interbevgroup.com/our-group/where-we-operate) |
| `balmenach-distillery` | Inver House | Supported | [source](https://www.interbevgroup.com/our-group/where-we-operate) |
| `pulteney-distillery` | Inver House | Supported | [source](https://www.interbevgroup.com/our-group/where-we-operate) |
| `speyburn-glenlivet-distillery` | Inver House | Supported | [source](https://www.interbevgroup.com/our-group/where-we-operate) |
| `arran-distillery` | Isle of Arran | Supported | [source](https://www.arranwhisky.com/news/394-lochranza-is-distillery-of-the-year) |
| `lagg-distillery` | Isle of Arran | Supported | [source](https://www.arranwhisky.com/news/394-lochranza-is-distillery-of-the-year) |
| `ardbeg` | LVMH | Supported | [source](https://www.lvmh.com/en/our-maisons/wines-spirits/ardbeg) |
| `glenmorangie-distillery` | LVMH | Supported | [source](https://www.lvmh.com/en/our-maisons/wines-spirits/glenmorangie) |
| `glen-moray-distillery` | La Martiniquaise | Supported | [source](https://ceed-scotland.com/member/glen-turner-distillery-ltd) |
| `glen-turner-distillery` | La Martiniquaise | Group association supported; exclude duplicate | [source](https://ceed-scotland.com/member/glen-turner-distillery-ltd) |
| `glen-scotia-distillery` | Loch Lomond | Supported | [source](https://www.lochlomondgroup.com/pages/who-we-are) |
| `loch-lomond-distillery` | Loch Lomond | Supported | [source](https://www.lochlomondgroup.com/pages/who-we-are) |
| `aberlour-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `allt-a-bhainne` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `braeval-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `dalmunach-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `glen-keith-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `glenburgie-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `glentauchers-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `longmorn-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `miltonduff-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `scapa-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `strathclyde-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `strathisla-distillery` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `the-glenlivet` | Pernod Ricard | Supported | [source](https://www.chivasbrothers.com/about/) |
| `ardmore-distillery` | Suntory | Supported | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) |
| `bowmore-distillery` | Suntory | Supported | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) |
| `glen-garioch-distillery` | Suntory | Supported | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) |
| `laphroaig-distillery` | Suntory | Supported | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) |
| `dalmore-distillery` | Whyte & Mackay | Supported | [source](https://careers.whyteandmackay.com/locations) |
| `fettercairn-distillery` | Whyte & Mackay | Supported | [source](https://careers.whyteandmackay.com/locations) |
| `invergordon-distillery` | Whyte & Mackay | Supported | [source](https://careers.whyteandmackay.com/locations) |
| `isle-of-jura-distillery` | Whyte & Mackay | Supported | [source](https://careers.whyteandmackay.com/locations) |
| `tamnavulin-distillery` | Whyte & Mackay | Supported | [source](https://careers.whyteandmackay.com/locations) |
| `ailsa-bay` | William Grant | Supported | [source](https://www.scotch-whisky.org.uk/join-us/members-directory/) |
| `balvenie-distillery` | William Grant | Supported | [source](https://www.scotch-whisky.org.uk/join-us/members-directory/) |
| `girvan-distillery` | William Grant | Supported | [source](https://www.scotch-whisky.org.uk/join-us/members-directory/) |
| `glenfiddich-distillery` | William Grant | Supported | [source](https://www.scotch-whisky.org.uk/join-us/members-directory/) |
| `kininvie-distillery` | William Grant | Supported | [source](https://www.scotch-whisky.org.uk/join-us/members-directory/) |


CVH is not automatically Heineken. The [operator](https://cvhspirits.com/) and [Tobermory's legal statement](https://tobermorydistillery.com/en-us/pages/modern-slavery-statement) identify the Capevin relationship; [CVH's June 2024 announcement](https://cvhspirits.com/wp-content/uploads/CVH-Spirits_s122-Announcement_12June2024.pdf) concerns Heineken's disposal. [Campari's 14.6% minority investment](https://www.camparigroup.com/sites/default/files/downloads/20240917_CVH%20minority%20stake%20acquisition_ENG.pdf) is not a basis to merge these three distilleries with Glen Grant. Use CVH/Capevin as the operating-group label; the supplied foreign Distell stop is historical and incomplete.

## Appendix D — targeted review of the independent bucket

All 28 in Appendix B were drawn from the build's 87 alleged independents. The following additional matched-site checks deliberately target family holdings, foreign parents, wrong company matches and JVs. Together these comfortably exceed the requested 25-site sample. “Residual” still does not mean verified independent.

| Sampled alleged-independent slug | Finding | Outside evidence |
| --- | --- | --- |
| `craigellachie` | Bacardi; wrong name-match link | [source](https://www.bacardilimited.com/media/news-archive/bacardi-invests-in-future-of-premium-scotch-whisky-with-multi-million-pound-distillery-and-warehousing-investments/) |
| `auchentoshan-distillery` | Suntory; wrong company match | [source](https://www.suntoryglobalspirits.com/news/beam-suntory-and-suntory-announce-peatland-water-sanctuary-initiative-scotland) |
| `glenrothes-distillery` | Edrington; malformed-ID chain stop | [source](https://www.edrington.com/en/brands) |
| `benromach` | Gordon & MacPhail: two whisky plants | [source](https://www.gordonandmacphail.com/corporate/our-brands) |
| `glencadam-distillery` | Angus Dundee: Glencadam and Tomintoul | [source](https://www.angusdundee.co.uk/) |
| `springbank-distillery` | J & A Mitchell: Springbank and Glengyle | [source](https://www.springbank.scot/about/story/) |
| `glengyle` | J & A Mitchell: shared family operating group | [source](https://kilkerran.scot/) |
| `torabhaig` | Mossburn: Torabhaig and Reivers | [source](https://mossburndistillers.com/projects/) |
| `north-british-distillery` | Joint control, not independent | [source](https://find-and-update.company-information.service.gov.uk/company/SC141866/persons-with-significant-control) |
| `ben-nevis-distillery` | Nikka; foreign group with one counted Scotch plant | [source](https://www.nikka.com/en/about/) |
| `bruichladdich-distillery` | Rémy Cointreau; not economically independent | [source](https://www.bruichladdich.com/pages/faqs) |
| `glen-grant-distillery` | Campari; minority CVH investment is not common control | [source](https://www.camparigroup.com/it/pages/brands) |
| `kingsbarns-distillery` | Wemyss family; Darnley’s is gin, not a second Scotch distillery | [source](https://wemyssfamilyspirits.com/who-we-are) |
| `ardnahoe-distillery` | Hunter Laing family business; residual in multi-Scotch definition | [source](https://ardnahoedistillery.com/pages/our-story) |
| `glenallachie-distillery` | Not assigned to Pernod; independent-era operator, detailed trust control unverified | [source](https://theglenallachie.com/news/billy-walker-led-team-unveil-vision-to-launch-single-malt-and-create-premium-blends/) |
| `tormore-distillery` | Elixir, not Pernod; Portintruan commissioning remains open | [source](https://elixirdistillers.com/distilleries) |
| `eden-mill-st-andrews` | New production site confirmed; current ownership not certified | [source](https://www.edenmill.com/blogs/distillery/we-are-now-operational) |
| `speyside-distillery` | Closed site removed | [source](https://speysidedistillery.co.uk/news/33/34/Speyside-Distillery-A-lost-distillery) |
| `isle-of-cumbrae-distillers` | Gin plus sourced whisky does not make a Scotch producer | [source](https://isleofcumbrae-distillers.com/) |
| `kinrara-distillery` | Gin operation removed | [source](https://www.kinraradistillery.com/) |
| `city-of-aberdeen-distillery` | Gin operation removed | [source](https://cityofaberdeendistillery.co.uk/) |
| `greenock-distillery` | Titan rum operation removed | [source](https://titanspiritsltd.com/) |
| `deeside-distillery` | Lost Loch other spirits; distinct from omitted Burn o’Bennie | [source](https://lostlochspirits.com/) |


## Appendix E — standalone recomputation, embedded to keep the change report-only

Run the Python block below from the repository root at the audited revision. It reads the GeoJSON, crosswalk and PSC CSV directly; it does not import or execute `build-ownership-card.mjs`, read the generated summary, or use `groups.json`. The embedded TSV is this auditor's explicit inclusion and externally checked multi-site-group adjudication, not a builder output. Category verdicts were only screening hints. Unreviewed ownership remains residual; PSC terminals are retained for diagnostics, not treated as proof of independence.

Input hashes bind the calculation to the reviewed files. The executable block checks every manifest slug against the map and joins company and PSC records before counting. It emits both the strict September SWA reconciliation and the broader commissioned-plant scenario. The no-SWA rows in the latter are explicitly marked in Appendix A. It does not silently add off-map Levenbank or assume hypothetical openings.

| Input | SHA-256 |
| --- | --- |
| public/data/distilleries.geojson | 152bcc6d8947f7dba21a536d57bdb4ae1752cf31dac415a6de9a3717e42dc432 |
| data/company-crosswalk/company-crosswalk.csv | 8fe6bd6dc05dfe25539a32d050727f36e14c532a2d800f1ea123c5dff7bb7200 |
| data/ownership/psc-parents.csv | 824427eb3734fb8e1293f832f1b86bfa8fd288da7253892651408c5d05bc6ce0 |


```python
import csv, hashlib, io, json, re
from collections import Counter
from pathlib import Path

root = Path.cwd()
report = root / "docs/research/ownership-audit-2026-09.md"
expected = {'public/data/distilleries.geojson': '152bcc6d8947f7dba21a536d57bdb4ae1752cf31dac415a6de9a3717e42dc432', 'data/company-crosswalk/company-crosswalk.csv': '8fe6bd6dc05dfe25539a32d050727f36e14c532a2d800f1ea123c5dff7bb7200', 'data/ownership/psc-parents.csv': '824427eb3734fb8e1293f832f1b86bfa8fd288da7253892651408c5d05bc6ce0'}
for path, digest in expected.items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, path
geo = json.loads((root / "public/data/distilleries.geojson").read_text())
features = {f["properties"]["slug"]: f for f in geo["features"]}
xwalk = {r["slug"]: r for r in csv.DictReader(
    (root / "data/company-crosswalk/company-crosswalk.csv").open())}
psc = {r["company_number"]: r for r in csv.DictReader(
    (root / "data/ownership/psc-parents.csv").open())}
manifest = re.search(r"```tsv\n(.*?)\n```", report.read_text(), re.S).group(1)
rows = list(csv.DictReader(io.StringIO(manifest), delimiter="\t"))
assert len(rows) == len({r["slug"] for r in rows})
joined = []
for row in rows:
    if row["group"] == "-":
        row["group"] = ""
    feature = features[row["slug"]]
    assert feature["properties"]["region"] == "scotland"
    company = xwalk.get(row["slug"], {})
    accepted = (company.get("registry") == "companies-house"
                and company.get("confidence") in ("high", "verified"))
    parent = psc.get(company.get("company_number"), {}) if accepted else {}
    # A terminal, failure or unmatched company is never proof of independence.
    row["accepted_match"] = accepted
    row["recorded_parent"] = parent.get("ultimate_name", "unresolved")
    row["stop"] = parent.get("stopped_because", "unresolved")
    joined.append(row)
print("manifest", len(joined), "reviewed build records",
      sum(int(r["built"]) for r in joined), "unmatched build records",
      sum(r["built"] == "1" and not r["accepted_match"] for r in joined))
for label, field in [("SWA", "swa"), ("commissioned mapped", "include")]:
    active = [r for r in joined if r[field] == "1"]
    group_counts = Counter()
    residual = joint = 0
    for row in active:
        weight = int(row["units"])
        group = row["group"]
        if group == "JV":
            joint += weight
        elif group:
            group_counts[group] += weight
        else:
            residual += weight
    assert all(n >= 2 for n in group_counts.values())
    grouped = sum(group_counts.values())
    print(label, dict(total=grouped+joint+residual, group_run=grouped,
          joint_venture=joint, residual_not_verified_independent=residual,
          groups=len(group_counts), Diageo=group_counts["Diageo"]))
    print("groups", dict(sorted(group_counts.items())))
print("Included residual PSC stops", dict(Counter(
    r["stop"] for r in joined if r["include"] == "1" and not r["group"])))
```

```tsv
slug	built	swa	include	units	group
57-skye-distillery	1	0	0	1	-
8-doors-distillery	1	1	1	1	-
aberargie-distillery	1	1	1	1	-
aberfeldy-distillery	1	1	1	1	Bacardi
aberlour-distillery	1	1	1	1	Pernod Ricard
abhainn-dearg-distillery	1	0	1	1	-
ailsa-bay	1	1	1	1	William Grant
allt-a-bhainne	1	1	1	1	Pernod Ricard
ancnoc-distillery	1	1	1	1	Inver House
annandale-distillery	1	1	1	1	-
arbikie-distillery	1	1	1	1	-
ardbeg	1	1	1	1	LVMH
ardgowan-distillery	1	1	1	1	-
ardmore-distillery	1	1	1	1	Suntory
ardnahoe-distillery	1	1	1	1	-
ardnamurchan-distillery	1	1	1	1	-
ardross-distillery	1	1	1	1	-
arran-distillery	1	1	1	1	Isle of Arran
auchentoshan-distillery	1	1	1	1	Suntory
auchroisk-distillery	1	1	1	1	Diageo
aultmore-distillery	1	1	1	1	Bacardi
badachro-distillery	1	1	1	1	-
balblair-distillery	1	1	1	1	Inver House
ballindalloch-distillery	1	1	1	1	-
balmaud-distillery	1	1	1	1	-
balmenach-distillery	1	1	1	1	Inver House
balvenie-distillery	1	1	1	1	William Grant
ben-nevis-distillery	1	1	1	1	-
benbecula-distillery	1	1	1	1	-
benriach-distillery	1	1	1	1	Brown-Forman
benrinnes-distillery	1	1	1	1	Diageo
benromach	1	1	1	1	Gordon & MacPhail
blackness-bay-distillery	0	1	1	1	-
bladnoch-distillery	1	1	1	1	-
blair-athol-distillery	1	1	1	1	Diageo
bonnington	1	1	1	1	-
bowmore-distillery	1	1	1	1	Suntory
braeval-distillery	1	1	1	1	Pernod Ricard
brora-distillery	1	1	1	1	Diageo
bruichladdich-distillery	1	1	1	1	-
bunnahabhain-distillery	1	1	1	1	CVH / Capevin
burnobennie-distillery	0	1	1	1	-
cameronbridge-distillery	1	1	1	1	Diageo
caol-ila-distillery	1	1	1	1	Diageo
cardhu-distillery	1	1	1	1	Diageo
city-of-aberdeen-distillery	1	0	0	1	-
clydeside-distillery	1	1	1	1	-
clynelish-distillery	1	1	1	1	Diageo
cragganmore-distillery	1	1	1	1	Diageo
craigellachie	1	1	1	1	Bacardi
daftmill-distillery	1	1	1	1	-
dailuaine	1	1	1	1	Diageo
dalmore-distillery	1	1	1	1	Whyte & Mackay
dalmunach-distillery	1	1	1	1	Pernod Ricard
dalwhinnie-distillery	1	1	1	1	Diageo
deanston-distillery	1	1	1	1	CVH / Capevin
deerness-distillery	0	1	1	1	-
deeside-distillery	1	0	0	1	-
diageo-global-supply-centre	1	0	0	1	Diageo
dornoch-distillery	1	1	1	1	-
dufftown-distillery	1	1	1	1	Diageo
dunkeld-distillery	1	0	0	1	-
dunphail-distillery	1	1	1	1	-
eden-mill-st-andrews	1	0	1	1	-
edradour-distillery	1	1	1	1	-
falkirk-distillery	1	1	1	1	-
fettercairn-distillery	1	1	1	1	Whyte & Mackay
galloway-distillery	1	1	1	1	-
girvan-distillery	1	1	1	1	William Grant
glasgow-distillery	1	1	1	1	-
glen-elgin-distillery	1	1	1	1	Diageo
glen-garioch-distillery	1	1	1	1	Suntory
glen-grant-distillery	1	1	1	1	-
glen-keith-distillery	1	1	1	1	Pernod Ricard
glen-moray-distillery	1	1	1	1	La Martiniquaise
glen-ord-distillery	1	1	1	1	Diageo
glen-scotia-distillery	1	1	1	1	Loch Lomond
glen-spey-distillery	1	0	1	1	Diageo
glen-turner-distillery	1	0	0	1	La Martiniquaise
glenallachie-distillery	1	1	1	1	-
glenburgie-distillery	1	1	1	1	Pernod Ricard
glencadam-distillery	1	1	1	1	Angus Dundee
glendullan-distillery	1	1	1	1	Diageo
glenfarclas-distillery	1	1	1	1	-
glenfiddich-distillery	1	1	1	1	William Grant
glenglassaugh-distillery	1	1	1	1	Brown-Forman
glengoyne-distillery	1	1	1	1	Ian Macleod
glengyle	1	1	1	1	J & A Mitchell
glenkinchie-distillery	1	1	1	1	Diageo
glenlossie	1	1	1	1	Diageo
glenmorangie-distillery	1	1	1	1	LVMH
glenrothes-distillery	1	1	1	1	Edrington
glentauchers-distillery	1	1	1	1	Pernod Ricard
glenwyvis-distillery	1	1	1	1	-
great-glen-distillery-scotlands-smallest-craft-distillery	1	0	0	1	-
greenock-distillery	1	0	0	1	-
highland-boundary-wild-distillery	1	0	0	1	-
highland-park-distillery	1	1	1	1	Edrington
holyrood-distillery	1	1	1	1	-
ian-macleod-distillers-ltd	1	0	0	1	Ian Macleod
inchdairnie-distillery	1	1	1	1	-
inchgower-distillery	1	1	1	1	Diageo
invergordon-distillery	1	1	1	1	Whyte & Mackay
isle-of-barra-distillers	1	0	0	1	-
isle-of-bute-distillery	1	0	0	1	-
isle-of-cumbrae-distillers	1	0	0	1	-
isle-of-harris-distillery	1	1	1	1	-
isle-of-jura-distillery	1	1	1	1	Whyte & Mackay
isle-of-raasay-distillery	1	1	1	1	-
isle-of-skye-distillers	1	0	0	1	-
isle-of-tiree-distillery	1	1	1	1	-
jackton-distillery	0	1	1	1	-
kilchoman-distillery	1	1	1	1	-
kingsbarns-distillery	1	1	1	1	-
kininvie-distillery	1	1	1	1	William Grant
kinrara-distillery	1	0	0	1	-
knockando-distillery	1	1	1	1	Diageo
kythe-distillery	1	0	1	1	-
lagavulin-distillery	1	1	1	1	Diageo
lagg-distillery	1	1	1	1	Isle of Arran
laggan-bay-distillery	1	1	1	1	Ian Macleod
laphroaig-distillery	1	1	1	1	Suntory
lindores-abbey-distillery	1	1	1	1	-
linkwood-distillery	1	1	1	1	Diageo
linlithgow-distillery	1	0	0	1	-
loch-lomond-distillery	1	1	1	2	Loch Lomond
lochlea-distillery	1	1	1	1	-
longmorn-distillery	1	1	1	1	Pernod Ricard
luss-distillery	1	0	0	1	-
macduff-distillery	1	1	1	1	Bacardi
mannochmore-distillery	1	1	1	1	Diageo
miltonduff-distillery	1	1	1	1	Pernod Ricard
moffat-distillery	1	1	1	1	-
mortlach-distillery	1	1	1	1	Diageo
ncnean-distillery	1	1	1	1	-
newbridge-bond-the-benriach-distillery-company-limited	1	0	0	1	Brown-Forman
north-british-distillery	1	1	1	1	JV
north-point-distillery	0	1	1	1	-
north-uist-distillery	1	1	1	1	-
oban-distillery	1	1	1	1	Diageo
ogilvy-distillery	1	0	0	1	-
persie-distillery	1	0	0	1	-
port-ellen-distillery	1	1	1	1	Diageo
port-of-leith-distillery	1	1	1	1	-
pulteney-distillery	1	1	1	1	Inver House
reivers-distillery	1	1	1	1	Mossburn
rhidorroch-distillery-cafe-bar-eatery	1	0	0	1	-
rosebank-distillery	1	1	1	1	Ian Macleod
roseisle	1	1	1	1	Diageo
royal-brackla	1	1	1	1	Bacardi
royal-lochnagar-distillery	1	1	1	1	Diageo
scapa-distillery	1	1	1	1	Pernod Ricard
speyburn-glenlivet-distillery	1	1	1	1	Inver House
speyside-distillery	1	0	0	1	-
springbank-distillery	1	1	1	1	J & A Mitchell
stannergill-distillery	1	0	1	1	-
starlaw-distillery	1	1	1	1	La Martiniquaise
stirling-distillery	0	1	1	1	-
stornoway-distillers-co	1	0	0	1	-
strathclyde-distillery	1	1	1	1	Pernod Ricard
strathearn-distillery	1	1	1	1	-
strathisla-distillery	1	1	1	1	Pernod Ricard
strathmill	1	0	1	1	Diageo
talisker-distillery	1	1	1	1	Diageo
tamdhu-distillery	1	1	1	1	Ian Macleod
tamnavulin-distillery	1	1	1	1	Whyte & Mackay
tayport-distillery	1	0	0	1	-
teaninich-distllery	1	1	1	1	Diageo
the-borders-distillery	1	1	1	1	-
the-cabrach-distillery	1	1	1	1	-
the-cairn	0	1	1	1	Gordon & MacPhail
the-glendronach-distillery	1	1	1	1	Brown-Forman
the-glenlivet	1	1	1	1	Pernod Ricard
the-glenturret-distillery	1	1	1	1	-
the-macallan-distillery	1	1	1	1	Edrington
the-machrihanish-distillery	1	0	0	1	-
the-orkney-distillery	1	1	1	1	-
tobermory-distillery	1	1	1	1	CVH / Capevin
tomatin-distillery	1	1	1	1	-
tomintoul-distillery	0	1	1	1	Angus Dundee
torabhaig	1	1	1	1	Mossburn
tormore-distillery	1	1	1	1	-
tullibardine-distillery	1	1	1	1	-
uile-bheist-distillery	0	1	1	1	-
wolfburn-distillery	1	1	1	1	-
```
