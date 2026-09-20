# Australia and New Zealand: company registers and licence lists for the crosswalk, 20 September 2026

Research for the Australian and New Zealand leg of `data/company-crosswalk/`. The map has
368 pins with `country: "Australia"` and 57 with `country: "New Zealand"`. State is parsed
from the address: VIC 86, NSW 83, QLD 53, TAS 51, WA 43, SA 37, ACT 4, NT 4, and 7 with no
usable address (one of them, `skin-gin`, carries a German address and is mislabelled).

Every "free / bulk / API" claim below comes from a page, CKAN record or file fetched on
20 Sep 2026. Where a site blocked the fetch or returned 404, the table says so.

## Summary

Australia has two free, bulk, CC-BY national registers that together give the legal entity
behind most trading names: the **ABN bulk extract** (entity name, registered business and
trading names, ACN, state and postcode) and the **ASIC Company Dataset** (ACN, status, type,
registration date). The ABR is the bridge: a distillery's trading name is usually a
registered business name on the ABN of the company or trust that runs it, and the ABN record
carries the ACN when the holder is a company. Only Victoria publishes a licence list with the
licensee's legal name; Tasmania publishes premises names only; NSW, QLD, SA and WA have web
searches, paid detail or nothing usable. The ATO excise manufacturer licence register is not
published.

New Zealand has no anonymous route: the Companies Office bulk files need an access request,
the NZBN API needs a subscription key, data.govt.nz is bot-gated, and the register search app
disallows all agents in its robots.txt. NZ rows therefore come only from one hand-fetched
search page and stay leads.

## Australia: company registers

| Register | URL | Free lookup | Bulk open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| Australian Business Register, ABN Lookup | https://abr.business.gov.au | Yes, web search by ABN, ACN or name | **Yes.** "ABN Bulk Extract", data.gov.au, https://data.gov.au/data/dataset/abn-bulk-extract, licence **CC-BY 3.0 AU** (CKAN `license_id: cc-by`), weekly (readme: "The extract is generated weekly"). Two zips, `public_split_1_10.zip` 498.1 MB and `public_split_11_20.zip` 497.9 MB (CKAN sizes), 20 XML files of ~630 MB each, **12.6 GB uncompressed**, 20,529,631 ABN records (RecordCount 1,026,900 in each of the first 19 files), extract time 2026-09-16. Fields (readme v2.6 and the XML): ABN and status with from-date, entity type code and text, main entity name or individual legal name, state and postcode of the main business location, ACN (`ASICNumber`), GST status, registered business names and trading names (`OtherEntity`, types BN/TRD/OTN), DGR names, record last-updated date. No street address, no directors, no incorporation date. | **Yes, registration required.** ABN Lookup web services (https://abr.business.gov.au/Tools/WebServices): "Access to the ABN Lookup web services is free of charge"; registration form issues "an authentication GUID ... required to access the ABN Lookup web services". SOAP/WSDL plus "limited JSON support for ABN and name searching" at https://abr.business.gov.au/json/. Not registered, not called. | Nothing | Bulk zips downloaded 20 Sep 2026 (extract of 16 Sep), streamed once into a slim index |
| ASIC company register | https://asic.gov.au (ASIC Connect search https://connectonline.asic.gov.au) | Yes, ASIC Connect free search returns name, ACN, status, type, registration date and state; documents are paid | **Yes.** "ASIC - Company Dataset", data.gov.au, https://data.gov.au/data/dataset/asic-companies, licence **CC-BY 3.0 AU** (CKAN), monthly file `company_202609.zip` 79.1 MB (CSV 399.8 MB), CKAN last modified 14 Sep 2026. Tab-separated: Company Name, ACN, Type (APTY/APUB), Class (LMSH...), Sub Class (PROP, NEXT, PNPC...), Status (REGD/DRGD), Date of Registration, Date of Deregistration, Previous State of Registration, State Registration number, Modified since last report, Current Name Indicator, ABN, Current Name, Current Name Start Date. Former names are separate rows. **No address.** 4,445,221 rows including former-name rows (scanned 20 Sep 2026). | ASIC Connect has no public API; ASIC's data is sold through information brokers | Company extracts and documents | Downloaded 20 Sep 2026, streamed once per run |
| ASIC business names register | https://asic.gov.au | Yes (ASIC Connect) | **Yes.** "ASIC - Business Names Dataset", https://data.gov.au/data/dataset/asic-business-names, CC-BY 3.0 AU, monthly, `business_names_202609.zip` 71.8 MB (CSV 247.5 MB), last modified 15 Sep 2026. Fields: register name, business name, status, registration date, cancellation date, state number, state of registration, ABN. | None | Extracts | Downloaded and inspected; **not used in matching** because the same current business names sit inside the ABR record as `OtherEntity type="BN"`, which also gives the holder and location. Kept as a fallback for registration dates. |
| ABN Lookup web services | https://abr.business.gov.au/Tools/WebServices | n/a | n/a | Free with GUID; see above | n/a | **Not used** (registration required by the brief's rule; bulk file covers the need) |

Entity-type codes seen in the slim index: PRV (Australian Private Company), IND (Individual/
Sole Trader), DTT / DIT / FUT / FPT / TRT (trusts of various kinds), PTR (partnership), PUB.
For trusts the ABN holder is "The Trustee for X Trust"; the trustee company is not in the
ABR record, so a trust row is `self` with the trust name and no ACN.

## Australia: liquor producer licence lists (second identifier layer)

| State | List | Legal name? | Notes |
|---|---|---|---|
| VIC | Liquor Control Victoria, "Victorian liquor licences by location", https://discover.data.vic.gov.au/dataset/victorian-liquor-licences-by-location | **Yes**, `Licensee` (legal name or individual) plus `Trading As` | **CC-BY 4.0** (CKAN `license_title`). Monthly xlsx stocktake; the August 2026 file (`Current_Victorian_Licences_By_Location_31_August_2026.xlsx`, 4.9 MB, "Current Victorian Liquor Licences as of 31/08/2026") has 23,036 licences, of which **1,155 Producer's Licence** rows (wine, beer and spirits producers together). Fields: licence number, licensee, trading as, category, trading hours, capacity, street address, suburb, postcode, council, region, lat/long, postal address. The sister dataset "Victorian liquor licences split by licence type" (https://discover.data.vic.gov.au/dataset/victorian-liquor-licences-split-by-licence-type, CC-BY 4.0) lists a `Producers_Licence.csv`, but every CloudFront URL in it returned **404** on 20 Sep 2026. |
| TAS | Land Tasmania, the LIST "Liquor Licences" layer, https://services.thelist.tas.gov.au/arcgis/rest/services/Public/EmergencyManagementPublic/MapServer/16 (data.gov.au record https://data.gov.au/data/dataset/liquor-licences) | **No**: `PREMISE_NA` only | Layer copyright text: **CC-BY 3.0 AU**, "the LIST (c) State of Tasmania". Esri REST query, no key. Fields: LICENCE_NO, CURRENCY, PREMISE_NA, address lines, SUBURB, POSTCODE, CATEGORY, SUB_CATEGO, WEB_LINK. Sub-category **Brewery/Distillery: 77 licences** (one query on 20 Sep 2026). Treasury's liquor pages (https://www.treasury.tas.gov.au/liquor-and-gaming/liquor and .../licence-and-permit-holders) carry no licensee list. |
| NSW | Liquor & Gaming NSW | Only in the paid/registered API | The data.nsw.gov.au "Liquor licence premises list" (https://data.nsw.gov.au/data/dataset/liquor-licence-premises-list and the 8 Feb 2021 file, CC-BY) is stale and **contains no producer/wholesaler licences** (19,304 rows: on-premises, packaged, hotel, limited, club, small bar only). The NSW "Liquor API" on api.nsw.gov.au (https://api.nsw.gov.au/Product/Index/19, last updated 30 Dec 2019) has Verify / Browse / Details operations and shows a sandbox key with "a limit of 5 calls every minute or alternatively register and subscribe"; not used (registration route). The liquorandgaming.nsw.gov.au "liquor licence data" link redirects to the generic resource library on nsw.gov.au with no file. |
| QLD | OLGR Online Licence Search, https://secure.olgr.qld.gov.au/forms/lls | Paid | Page text: "View basic licence details - Free ... Receive detailed information on selected results - $45.65 per licence ... unlimited selected results - $4,818.00 per annum". Basic results are premises name, address, licence number, type and status; licensee details are in the paid tier (Guideline 01, https://www.business.qld.gov.au/industries/hospitality-tourism-sport/liquor-gaming/liquor/liquor-guidelines/register-licences-permits). data.qld.gov.au has no liquor licence dataset (search returned none). **Not used.** |
| SA | CBS Liquor and Gaming public register, https://secure.cbs.sa.gov.au/LGPubReg/ | Yes on the web form (Licensee Name is a search field) | Form-driven (`LandG_licences_fromDB.php`), max 500 results, and the page showed "Error connecting to database" on 20 Sep 2026. The data.sa.gov.au "Liquor & Gaming Licences" dataset (https://data.sa.gov.au/data/dataset/liquor-gaming-licences, CC-BY) was last updated **19 Aug 2019** and its 6,844 rows carry premises name, address and status but **no licensee and no licence type**. **Not used.** |
| WA | Racing, Gaming and Liquor (DLGSC), https://www.wa.gov.au/organisation/racing-gaming-and-liquor/liquor-applications | Not found | The wa.gov.au liquor pages fetched describe applications and an online portal for licensees; no public licence list or search page was found (the guessed search URLs returned 404; catalogue.data.wa.gov.au has no liquor dataset). **Not used.** |
| ACT, NT | Not researched (4 pins each) | | |
| Federal | ATO excise manufacturer licence | n/a | Not published as a register. Distillers must hold an ATO excise manufacturer licence (Excise Act 1901), but the ATO does not publish licensees; the crosswalk records this as an unavailable layer. |

Trade lists (Australian Distillers Association members) are not registers and were skipped.

## New Zealand

| Register | URL | Free lookup | Bulk | API | Used |
|---|---|---|---|---|---|
| NZ Companies Register (Companies Office, MBIE) | https://companies-register.companiesoffice.govt.nz, search app https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search | Yes, web search returns company number, NZBN, status, type, registered office and incorporation date | "Bulk data is a monthly snapshot of most of the publicly available information on the Companies Register contained in a series of CSV files ... once you have access you can download it free of charge" but access must be requested (https://www.companiesoffice.govt.nz/data-services/ways-to-get-our-data/). Website content is CC-BY 4.0 "excluding the public notices and contents of the registers" (https://www.companiesoffice.govt.nz/about-us/copyright/). | Companies API (https://portal.api.business.govt.nz/api/companies-register) is for maintaining companies and needs a subscription key plus 3-legged OAuth/RealMe consent; "Use the NZBN API for retrieving public details". | **Not queried.** `https://app.companiesoffice.govt.nz/robots.txt` is `User-agent: * / Disallow: /`. Two hand requests were made on 20 Sep 2026 to read the first results page for "distillery" (184 results, 15 shown) before the robots file was checked; that saved page is the only NZ source. |
| NZBN Register | https://www.nzbn.govt.nz | Yes, web search | "you can request bulk data access. Once approved you can log in and download files ... JSON or CSV ... updated on a monthly basis" (https://portal.api.business.govt.nz/api/nzbn) | NZBN API: "There is no fee for using this API"; needs a developer-portal login and subscription key; "for most users who only need to search and get public information from the register the subscription key method is all that's needed". Not registered. | **Not used** |
| data.govt.nz | https://catalogue.data.govt.nz/dataset/the-companies-office | | The catalogue and its CKAN API returned a bot-challenge page ("Pardon Our Interruption") to a script on 20 Sep 2026, so whether a bulk companies extract is listed there could not be verified. | | **Not used** |

## Method

`scripts/match_australia_registers.py` (stdlib only; network only behind `--fetch-tas`):

1. `--build-abr-index` streams the two ABR zips once and keeps every record whose entity,
   business or trading name has token Jaccard >= 0.4 against any pin name or alias, or
   carries a drinks word (distillery, spirits, whisky, gin, rum, brewery, wines...), writing
   `abr-slim.tsv` in the cache (129,284 of 20,529,631 records).
2. ABR matching for all 368 Australian pins: token Jaccard on every name of the record,
   postcode agreement (strong) and state agreement (weak); records in another state are
   skipped unless the name is exact. Sole-trader ABNs are capped at `medium` and the
   person's name is not copied into the CSV. Trusts are kept with the trust name.
3. ASIC company file streamed once, keeping rows whose ACN was reached through an ABR row
   or a Victorian licensee, and rows whose name resembles a pin. ACN-linked rows inherit the
   ABR grade; name-only rows are capped at `medium` unless the state of registration agrees
   or the name is distinctive and carries a drinks word (the file has no address).
4. Victorian pins matched to Producer's Licence rows on Trading As and Licensee; licence
   rows go to `australia-licences.csv` (registry `vic-lcv`), and the licensee legal name is
   looked up exactly in the ABR to give the ABN and ACN (`lcv-licensee+abr-bulk`).
5. Tasmanian pins matched to the LIST Brewery/Distillery layer on premises name
   (`tas-list`, licence layer only, no legal name).
6. New Zealand: the saved first search page is parsed; company rows are written only where
   the name matches a pin (Jaccard >= 0.6 or exact).

Registries in the output: `au-abr` (ABN), `au-asic` (ACN), `nz-companies` (company number,
NZBN in the note); licence layer `vic-lcv`, `tas-list`.

## Result

Run of 20 Sep 2026 (ABR extract of 16 Sep, ASIC file of Sep 2026, LCV stocktake of 31 Aug
2026, LIST layer fetched 20 Sep). Best grade per pin:

| Region | Pins | High | Medium | Low | Unmatched |
|---|---|---|---|---|---|
| VIC | 86 | 70 | 8 | 5 | 3 |
| NSW | 83 | 62 | 14 | 1 | 6 |
| QLD | 53 | 44 | 5 | 1 | 3 |
| TAS | 51 | 37 | 10 | 4 | 0 |
| WA | 43 | 36 | 5 | 1 | 1 |
| SA | 37 | 29 | 4 | 2 | 2 |
| ACT | 4 | 2 | 1 | 0 | 1 |
| NT | 4 | 3 | 1 | 0 | 0 |
| (no address) | 7 | 3 | 2 | 0 | 2 |
| **Australia** | **368** | **286** | **50** | **14** | **18** |
| New Zealand | 57 | 2 | 1 | 0 | 54 |
| Total | 425 | 288 | 51 | 14 | 72 |

Rows written: `australia-candidates.csv` 1,032 rows (`au-abr` 546, `au-asic` 483,
`nz-companies` 3; high 633, medium 345, low 54; 977 high/medium rows carry a register
number, covering 339 pins). Match methods: `abr-bulk-name` 519, `abr-acn-link` 243,
`asic-bulk-name` 227, `lcv-licensee+abr-bulk` 13, `lcv-licensee+abr-acn-link` 13, `hand`
14, `nz-search-page-name` 3. 87 rows are sole-trader or individual-partnership ABNs (the
person's name is not copied; the row says "(individual, sole trader ABN; trades as ...)"
and is capped at `medium`). 99 rows are trusts.
`australia-licences.csv` 95 rows: `vic-lcv` 61 (61 Victorian pins), `tas-list` 34
(29 Tasmanian pins).

Hand rows (numbers read from the ABR slim index during the run): Four Pillars
(Healesville Distilling Pty Ltd, ABN 89606461367; Lion-Beer, Spirits & Wine Pty Ltd as
group), Starward (New World Whisky Distillery Pty Ltd, 78603892888), Beenleigh (Inner
Circle Distillery Pty Limited, 29102738670, operator; Bickfords Trading Pty Ltd, group),
Bundaberg (Bundaberg Distilling Company Pty Limited, 97009657069; Diageo Australia as
group, number not looked up), Sullivan's Cove (Sullivans Cove Distillery Pty Ltd,
91614780460), Lark Hobart and Pontville (Lark Distillery Pty Ltd, 57100738074; Lark
Distilling Co. Ltd, 62104600544, group), Limeburners Albany and the Swan Valley site (Latro
Southern Pty Ltd, 78110857504, trading as Great Southern Distilling Company).

Grading rules applied on top of the common ones: a match on one shared word only is capped
at `medium` unless the register name carries a drinks word; a name whose category word
differs from the pin (brewing, winery, farm, cellar door) with no distilling word on the
same ABN is capped at `medium`, or `low` for one-word pins; ASIC name-only rows are capped
at `medium` when the name has no drinks word or is a former name; ABN-cancelled or
deregistered entities are `medium`.

## Request log, 20 Sep 2026

Search endpoints (the ones the cap applies to): `app.companiesoffice.govt.nz` company
search, **2 requests** (one probe, one saved page), then stopped when its robots.txt was read.
No other search endpoint was queried. ABN Lookup web services, ASIC Connect, NSW Liquor
API, QLD OLGR, SA CBS, NZBN API: **0 requests**.

Bulk downloads (data.gov.au, 20 Sep 2026): ABR `public_split_1_10.zip` 498.1 MB and
`public_split_11_20.zip` 497.9 MB; ASIC `company_202609.zip` 79.1 MB; ASIC
`business_names_202609.zip` 71.8 MB; two help PDFs. Victoria xlsx 4.9 MB; NSW 2021 premises
CSV 4.9 MB; SA 2019 xlsx 0.9 MB; Tasmanian LIST layer JSON (77 features). Total about
1.16 GB against the 2 GB cap.

Page and metadata fetches: data.gov.au CKAN API 4; abr.business.gov.au 6 (two 404s);
discover.data.vic.gov.au 3 plus 2 CloudFront CSV attempts (both 404); data.nsw.gov.au 3
(one 404 on the wrong API path); nsw.gov.au / liquorandgaming.nsw.gov.au 2; api.nsw.gov.au 1;
data.qld.gov.au 2; secure.olgr.qld.gov.au 1; business.qld.gov.au 2 (one 404); data.sa.gov.au
4; cbs.sa.gov.au 1 (403); secure.cbs.sa.gov.au 1; catalogue.data.wa.gov.au 2; wa.gov.au 2
(one 404); dlgsc.wa.gov.au 1 (404); treasury.tas.gov.au 3 (one 404); services.thelist.tas.gov.au
4; catalogue.data.govt.nz 2 (bot challenge); companiesoffice.govt.nz 8 (four 404s, one
robots.txt); portal.api.business.govt.nz 2; app.companiesoffice.govt.nz 3 (2 searches, 1
robots.txt). Four web-search-engine queries were used to find register URLs. All fetches were
sequential at one request per second or slower.

## Unmatched pins

Australia, 18 pins:

- Not a spirits distillery or mislabelled (5): `skin-gin` (German address, country wrong),
  `the-distillery-pty-ltd-trading-as-distillery-software` (software company), `yesteryear-
  plantations-eucalyptus-oil-distillers` and `mickey-s-eucy-distillery` (eucalyptus oil),
  `new-tricks` (no address, generic name). These are map data-quality items, not register gaps.
- Trading name not registered under a resembling name in the ABR, and no licence layer for
  the state (13): `anther-gin`, `monday-distillery` (VIC, no LCV producer's licence under
  that name either), `wild-flower-gin-distilling`, `mcw-distillery`, `ladbroken-distillery-
  brewhouse`, `three-valleys-gin-distillery`, `moonshiner-gin-distillery`, `kawal-rock-
  distillery`, `wildstreak-distillery`, `conrad-distillery`, `bent-road-winery-distillery`,
  `30-knots-distillery`, `aob-distillery`. The ABN Lookup web search (by hand) would resolve
  most of these; the trading name is probably held by a company or trust with an unrelated
  name and no registered business name.

New Zealand, 54 pins: no permitted free route (see the NZ table). The three matched pins
(`ruapehu-distillery`, `aurora-distillery` high on name plus registered-office address;
`auld-farm-distillery` medium) come from the one saved search page.

## Gaps and licence calls for John

- All datasets used are CC-BY (ABR 3.0 AU, ASIC 3.0 AU, LCV 4.0, LIST 3.0 AU); no
  non-commercial or share-alike licence is involved. Attribution is required.
- The ABR gives state and postcode only, so "location agrees" means postcode; a company
  registered to an accountant's postcode will not agree and stays `medium`.
- The ASIC file has no address, so ASIC rows are only `high` when reached through an ABR
  ACN link or when the state of registration agrees.
- NSW (83 pins), QLD (53), WA (43) and SA (37) have no licence layer, so their pins depend
  on the trading name being a registered business or trading name on the ABR.
- Trusts: many small distilleries are run by a family or unit trust; the trustee company
  is not in any free file, so those rows carry the trust ABN only.
- New Zealand needs either a bulk-data access request to the Companies Office or an NZBN
  API subscription key, both free but registered. Until then NZ pins stay leads.
- ATO excise manufacturer licences are not published; there is no federal producer layer.
