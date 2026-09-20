# India and South Africa: company registers and licence lists for the crosswalk, 20 September 2026

Research for the India (105 pins) and South Africa (85 pins) legs of `data/company-crosswalk/`.
State for Indian pins is parsed from the address: Karnataka 14, Uttar Pradesh 14, Maharashtra 12,
Goa 9, Delhi 5, Kerala 4, Tamil Nadu 4, Gujarat 4, West Bengal 4, Himachal Pradesh 3, Puducherry 3,
Haryana 3, Madhya Pradesh 3, Chandigarh 2, Telangana 2, Daman 2, Punjab 2, Rajasthan 2, Odisha 1,
Andhra Pradesh 1, Bihar 1, Assam 1, and 9 with no usable address (one of them, `gelephu-distillery`,
is in Bhutan). South African pins carry no province; the tables below use coarse postal-code bands.

Every "free / bulk / API / licence" claim below comes from a page or file fetched on 20 Sep 2026.
Where a site blocked or errored, the table says so rather than guessing.

## Summary

India has one usable open source: the Ministry of Corporate Affairs company master data
republished on data.gov.in as state-wise CSVs under the Government Open Data License - India,
which allows commercial use with attribution. The catch is age: the files are the 2015 snapshot
("upto Mar 2015"), so companies incorporated since then (most craft gin distilleries) are absent,
and status is eleven years stale. The live MCA21 portal answered 403 "Access Denied" (Akamai edge)
to every page from this network, so its captcha and terms could not be read and it was not queried.
State excise licensee lists: Goa publishes its manufacturing units by excise station (names and
unit type, no licence numbers); Maharashtra has a public licensee search whose backend returned an
error on every query; Karnataka and Punjab excise sites were unreachable.

South Africa has no open register. CIPC's terms forbid "any technology to search and gain any
information from this site", its eServices search sits behind customer registration, and no
open-data extract exists (OpenCorporates' copy stops at September 2014 and is itself
captcha-gated). SARS excise licences and the provincial liquor-board registers are not published.
The only free, permitted route to a CIPC registration number is the distillery's own website,
where the number is often printed in the legal footer or terms page. That sweep is the South
African method here, and it was run for India too (Indian companies must print their CIN on
official publications, and many do so on their websites).

## India: company register

| Source | URL | Free lookup | Bulk open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| MCA21 portal, Master Data search | https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html | **Not verifiable from here.** Every URL on www.mca.gov.in (home page, MDS page, terms page, `mcafoportal/viewCompanyMasterData.do`) returned HTTP 403 with an Akamai "Access Denied ... errors.edgesuite.net" body, for curl and for the WebFetch tool alike. Captcha gating and the terms on automated use could not be read. | None on mca.gov.in | None found | Certified copies, document downloads (not verified: blocked) | **Not queried** |
| data.gov.in "Company Master Data" (MCA) | https://www.data.gov.in/catalog/company-master-data | n/a | **Yes.** Catalog nid 354261, "Published On 15/09/2015, Updated On 22/07/2026", contributor Ministry of Corporate Affairs, released under NDSAP. The catalog's own API (`/backend/dmspublic/v1/resources?filters[catalog_reference]=354261`) lists one resource, "Registrars of Companies (RoC)-wise Company Master Data", `frequency: Monthly`, note "The data upto 3rd November 2023", but its data file is `company_master_data_upto_Mar_2015_Goa.csv`. The sibling state files still exist at `https://data.gov.in/sites/default/files/dataurl15092015/company_master_data_upto_Mar_2015_<State>.csv` (302 to www.data.gov.in, then 200). Fields: CIN, date of registration, company name, status, class, category, authorised and paid-up capital, registered state, ROC, principal business activity, registered office address, sub-category. Content checked: Goa file, 7,353 companies, latest registration year 2015, so the files are the March 2015 snapshot whatever the catalog note says. Licence: page footer "licensed under the Government Open Data License - India"; the GODL gazette text (https://data.gov.in/sites/default/files/Gazette_Notification_OGDL.pdf) grants "a worldwide, royalty-free, non-exclusive license to use, adapt, publish ... for all lawful commercial and non-commercial purposes" subject to attribution ("The user must acknowledge the provider, source, and license of data by explicitly publishing the attribution statement"). Sizes downloaded (bytes): Maharashtra 94,486,449; Delhi 80,220,983; West Bengal 55,574,338; Tamil Nadu 37,269,115; Gujarat 25,905,884; Karnataka 25,727,016; Telangana 25,354,271; Uttar Pradesh 20,482,490; Rajasthan 14,051,186; Kerala 11,872,160; Madhya Pradesh 9,319,082; Haryana 7,841,051; Punjab 7,819,051; Bihar 6,024,675; Odisha 5,571,301; Chandigarh 3,822,108; Assam 2,809,150; Goa 2,173,681; Puducherry 844,959; plus Himachal Pradesh, Andhra Pradesh and Daman and Diu (see the run log). About 470 MB in total, kept in the scratchpad, never in the repo. | The catalog is flagged `is_api_available`, but the API record could not be listed (`/backend/dmspublic/v1/apis` returned 405 for every filter) and the api.data.gov.in endpoints need a registered key, so it was not used. | Nothing | **Yes**, matched locally |

Terms of use of data.gov.in (https://www.data.gov.in/terms-of-use) add only the usual accuracy
disclaimer; reuse is governed by the GODL.

## India: excise licence lists (second identifier layer)

| State | Source | Legal name? | Result |
|---|---|---|---|
| Goa | Department of Excise, "Contact Us" page, https://excise.goa.gov.in/contact_us.aspx | Unit name only, e.g. "M/s Fullarton Distilleries Pvt. Ltd. ( Distillery )", "M/s. Oceanking Distillers ( Distillery/Winery/Bottling of CL )", "M/s. John Distilleries Ltd. ( Distillery/Winery )", "M/s. Naveen Distillery ( Distillery/Winery/Bottling of CL )", "M/s United Spirits Ltd. ( Distillery/Winery )". No licence numbers, no addresses; the table is the excise guard posted at each manufacturing unit, grouped by excise station (Tiswadi, Ponda, Pernem, Salcete, Mormugao, Quepem, Canacona). | **Used** as a licence layer (`in-goa-excise`, number blank) and as a name bridge into the MCA file. The server's TLS chain is incomplete ("unable to get local issuer certificate" in curl and WebFetch), so the page was saved once by hand with `curl -k` into the cache; the matcher reads the cached copy and never fetches it. |
| Maharashtra | State Excise, "License Information" search, https://stateexcise.maharashtra.gov.in/1239/Licensee-Information (division, district, licence type; "Form 1" is the distillery licence, plus an "Export to Excel" button) | Should give licensee name and address | **No data.** Four POST queries (Form 1, PLL, BRL, FLW1; division ALL, district All) each returned the page with the message "The server committed a protocol violation. Section=ResponseHeader Detail=CR must be followed by LF" at the top and no results grid: the site's own backend failed. Not retried beyond that. The "Spirit Production And Dispatch System" (https://scmexcise.mahaonline.gov.in/distillery/) is a licensee login. |
| Karnataka | State Excise "List Of Distilleries" pages, e.g. https://stateexcise.karnataka.gov.in/info-4/List+Of+Distilleries/Composite+Distillery/en (also IMFL Manufacturing Distillery, Primary Distillery, Breweries; found via web search) | Unknown | **Unreachable**: six curl attempts timed out after 40 s; WebFetch got ECONNREFUSED 103.138.196.95:443. Worth retrying from an Indian network. |
| Punjab | https://excise.punjab.gov.in/ | Unknown | **Unreachable**: two attempts timed out at 25-30 s. |
| Others (UP, Kerala, TN, Delhi ...) | not searched | | Out of scope on this pass; UP alone has 14 pins, mostly sugar-mill distilleries whose companies are in the MCA file anyway. |

## South Africa: company register

| Source | URL | Free lookup | Bulk open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| CIPC eServices, Enterprise Search | https://eservices.cipc.co.za/ | Yes in principle ("search for enterprises on our register using enterprise name, enterprise number or director ID/passport number"), but "CONTINUE TO SEARCH" is a postback behind CUSTOMER REGISTRATION. No account was created. Terms (https://eservices.cipc.co.za/TermsConditions.aspx), clause 3 "Hyperlinks, framing, spiders and crawlers": "No person, business or website may ... (c) use any technology to search and gain any information from this site without the prior written permission of CIPC." Clause 4(5): commercial use "must be used and/or distributed only if such use, transmission and/or distribution is part of the service provision to client(s)". | None | None (the search results also say no public API; commercial resellers only) | Disclosure certificates and document copies, priced in regulations | **Not queried** (terms) |
| BizPortal | https://www.bizportal.gov.za/ | Company registration front end; same CIPC terms at https://www.bizportal.gov.za/terms.aspx | None | None | Registration fees | Not used |
| OpenCorporates, South Africa (register 237) | https://opencorporates.com/registers/237 | Web pages are hCaptcha-gated ("HAProxy Challenge" on `/companies/za?q=distillery`); the API (`api.opencorporates.com/v0.4/companies/search`) answers 401 "Invalid Api Token" without a key | Page text: "OpenCorporates' South Africa dataset was originally sourced from the predecessor body to CIPC, namely CIPRO, and is to be considered as for historical / archive purposes only, as data was gathered up to September 2014. In September 2014, CIPC introduced [terms] that restricted re-use of data from the new CIPC website." OpenCorporates bulk data is a paid/licensed product. | Keyed, paid tiers | Bulk and API plans | Not used (stale, gated) |
| Open Data ZA toolkit entry for CIPC | https://odza.opendata.durban/opendataza/resource/24 | Describes the CIPC search as free and anonymous; carries the DPSA site's own reuse notice ("Unless explicitly published under a relevant open license, any user wanting to use the website content, code or databases must contact the Website Administrator") | None | None | | Reference only |
| data.gov.za | https://data.gov.za/ | Host does not resolve (DNS failure on 20 Sep 2026). The "2010s dump" mentioned in the task could not be checked. | | | | Not available |

## South Africa: licence layer

| Body | Source | Result |
|---|---|---|
| SARS customs and excise (manufacturing warehouses, VM licences) | https://www.sars.gov.za/customs-and-excise/registration-licensing-and-accreditation/ | Describes the RLA (Registration, Licensing and Accreditation) eFiling system and application policy SC-CF-19. **No list of licensees is published**, as expected. |
| Western Cape Liquor Authority | https://www.wcla.gov.za/licensing/liquor-licence-database/ | The "Liquor Licence Database" page is an empty shell: the main content area holds no table, file or search widget (checked in the raw HTML and via WebFetch). The eLicence portal (https://elicence.wcla.gov.za/emats-wcla-elicence/) is a login. Nothing usable. |
| Gauteng Liquor Board | https://www.gauteng.gov.za/Services/ServiceDetails/CPM-002 (503 on fetch); www.gautengliquorboard.gov.za does not resolve | No register found. |
| Eastern Cape Liquor Board | https://www.eclb.co.za/ | Site reachable; no licence register linked from the home page. |
| KwaZulu-Natal Liquor Authority | www.kznliquor.co.za does not resolve | Not checked further. |

## Method

`scripts/match_india-southafrica_registers.py` (stdlib only; network only behind `--fetch-mca-states`
and `--fetch-websites`; `--cache DIR` holds the state CSVs, the Goa page and the website cache):

1. **India, MCA bulk (`mca-bulk-name`).** All state files in the cache are indexed by name token.
   Each Indian pin is scored by token Jaccard (legal suffixes and drinks words stripped), state
   agreement (pin address state vs `REGISTERED_STATE`), city agreement (pin city found in the
   registered-office address) and 2015 status. `high` = exact or Jaccard >= 0.8 with city agreeing
   or the pin tokens all inside the company name; `medium` = 0.6-0.8, or exact but not ACTIVE;
   `low` = weaker. Partial matches must carry a drinks/sugar word in the company name. Rows whose
   registered office is in another state are dropped unless the name is exact.
2. **Goa excise units (`goa-excise-unit-list`).** Goa pins are matched to the unit list; the unit
   name is then looked up exactly in the MCA file to give the CIN.
3. **Website sweep (`website-regno`).** For every pin with a website: fetch the home page, and if
   no number is found, up to two internal pages whose link text or path mentions contact / about /
   terms / privacy / legal / imprint / company / policy. Regex: CIN `[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}`
   for India, `YYYY/NNNNNN/NN` for South Africa. A CIN found on the site is looked up in the MCA
   file for the legal name; a ZA number takes the nearest "(Pty) Ltd / CC / Ltd" name from the
   page text. `high` when that name shares tokens with the pin, else `medium`. Facebook,
   NightsBridge and Yola-hosted "sites" are skipped. Responses are cached in `websites.json`, so
   reruns are offline.
4. **Hand rows (`hand`).** Group-run and renamed sites. For India the CIN is resolved from the MCA
   file by exact legal name at run time, never typed in; if the name is not in the 2015 file the
   number stays blank and the confidence drops one level. For South Africa the hand rows name the
   operator (Heineken Beverages for the three Distell sites, Edward Snell for Oude Molen) and take
   a number only if the site's own website printed one.

Nothing enters `company-crosswalk.csv` until a human copies a row into the manual or operators
file; the builder folds only `high`/`medium` rows that carry a register number.

## Results (second pass, 20 Sep 2026)

`python3 scripts/match_india-southafrica_registers.py --cache <scratchpad>/india-southafrica`
run twice back-to-back with no `--fetch-*` flags: byte-identical output both times, zero new
network requests (`requests this run: {} (cap 400)`), confirming the matcher is idempotent
against the cache left on disk. `112` candidate rows written to
`data/company-crosswalk/india-southafrica-candidates.csv`, `5` licence rows to
`data/company-crosswalk/india-southafrica-licences.csv`.

The counts below only credit a pin as high/medium/low when its best row carries a register
number, matching how the builder folds candidates (`high`/`medium` with a number only). A
handful of hand rows carry a known legal name but no CIN/CIPC number (CIPC's terms forbid an
automated search, and eight of the MCA hand cases predate the 2015 snapshot or fall outside
it); those rows are real leads in the candidates CSV but count as "unmatched" here because
they will not fold into the spine as-is.

| Country | Region | Pins | High | Medium | Low | Unmatched |
|---|---|---:|---:|---:|---:|---:|
| India | Karnataka | 14 | 7 | 4 | 0 | 3 |
| India | Uttar Pradesh | 14 | 4 | 4 | 0 | 6 |
| India | Maharashtra | 12 | 7 | 1 | 0 | 4 |
| India | (no address) | 9 | 1 | 1 | 0 | 7 |
| India | Goa | 9 | 4 | 0 | 0 | 5 |
| India | Kerala | 4 | 1 | 1 | 0 | 2 |
| India | Tamil Nadu | 4 | 2 | 0 | 0 | 2 |
| India | Delhi | 4 | 0 | 0 | 1 | 3 |
| India | Gujarat | 4 | 1 | 1 | 0 | 2 |
| India | West Bengal | 4 | 1 | 1 | 0 | 2 |
| India | Himachal Pradesh | 3 | 0 | 1 | 0 | 2 |
| India | Puducherry | 3 | 1 | 1 | 0 | 1 |
| India | Haryana | 3 | 3 | 0 | 0 | 0 |
| India | Punjab | 3 | 0 | 1 | 0 | 2 |
| India | Madhya Pradesh | 3 | 1 | 2 | 0 | 0 |
| India | Chandigarh | 2 | 2 | 0 | 0 | 0 |
| India | Telangana | 2 | 2 | 0 | 0 | 0 |
| India | Dadra/Nagar Haveli/Daman & Diu | 2 | 0 | 1 | 0 | 1 |
| India | Rajasthan | 2 | 1 | 1 | 0 | 0 |
| India | Odisha, Andhra Pradesh, Bihar, Assam | 4 | 0 | 0 | 1 | 3 |
| **India total** | | **105** | **38** | **20** | **2** | **45** |
| South Africa | Western Cape | 41 | 1 | 1 | 0 | 39 |
| South Africa | Gauteng | 20 | 0 | 1 | 0 | 19 |
| South Africa | (no postal code) | 6 | 0 | 0 | 0 | 6 |
| South Africa | KwaZulu-Natal | 6 | 0 | 0 | 0 | 6 |
| South Africa | Northern Cape | 4 | 0 | 0 | 0 | 4 |
| South Africa | Eastern Cape | 3 | 0 | 0 | 0 | 3 |
| South Africa | Mpumalanga | 2 | 0 | 0 | 0 | 2 |
| South Africa | Free State, North West, Limpopo | 3 | 0 | 0 | 0 | 3 |
| **South Africa total** | | **85** | **1** | **2** | **0** | **82** |

### Hand-row grounding check (this pass)

Every hand row for the well-known groups was checked against a file or page actually on
disk, not typed from memory:

- **India** — `amrut-distillery`/`amrut-distilleries-pvt-ltd`/`amrut-distilleries-private-limited`
  → CIN `U51101KA1972PLC002246` (AMRUT DISTILLERIES LIMITED), confirmed present in the cached
  `mca/Karnataka.csv`. `paul-john-distillery` → CIN `U51228KA1996PTC021158` (JOHN DISTILLERIES
  PRIVATE LIMITED), confirmed in `mca/Karnataka.csv`. `radico-nv-distilleries-maharashtra-ltd`
  and `rampur-distillery-a-unit-of-radico-khaitan-limited` → CIN `L26941UP1983PLC027278`
  (RADICO KHAITAN LIMITED), confirmed in `mca/Uttar_Pradesh.csv`.
  `allied-blenders-and-distillers-pvt-ltd` / `-limited` / three operator sites
  (Gaganpahad, Kalyani, Saha-Ambala) → CIN `U15511MH2008PTC187368` (ALLIED BLENDERS AND
  DISTILLERS PRIVATE LIMITED), confirmed in `mca/Maharashtra.csv`; the same four pins also
  carry a `website-regno` row with CIN `L15511MH2008PLC187368`, read directly off
  abdindia.com's contact page (cached in `websites.json`, not the MCA snapshot, since the
  company's 2024 public listing postdates the 2015 file). `brima-sagar-maharashtra-distilleries-ltd`
  (group row) → CIN `L15420PN1933PLC133303` (TILAKNAGAR INDUSTRIES LIMITED), confirmed in
  `mca/Maharashtra.csv`. Jagatjit Industries, Mohan Meakin, Som Distilleries, Globus Spirits,
  United Spirits/Diageo and Piccadily Sugar & Allied Industries have **no pin** in this
  dataset's India set (105 pins, checked by name against every pin) — there is nothing to add
  a hand row to; they are noted here so the gap is visible rather than silent.
- **South Africa** — none of Distell/Heineken Beverages (Klipdrift, James Sedgwick, Van Ryn's),
  Wilderer, Hope on Hopkins, Inverroche, Boplaas or Time Anchor ever had a CIPC number: CIPC's
  own terms forbid an automated search of its register (see the South Africa register table
  above), and the website sweep (cached in `websites.json`) fetched each site's homepage plus
  up to two contact/about/terms pages and found no registration number printed on any of them
  (three of the fetches — James Sedgwick, Van Ryn's, Inverroche — errored: HTTP 500/403). Per
  the crosswalk rule, **all eight rows were downgraded from `high`/`medium` to `low`, their
  `company_number` cleared, and the note now reads "... ; name known, number not read."** This
  downgrade is encoded in `scripts/match_india-southafrica_registers.py` itself (the `HAND_ZA`
  loop only keeps the hand-set confidence when a number was actually found on the site; a
  blank result always emits `low`), so it is not a one-off CSV edit — rerunning the matcher
  reproduces the same downgraded rows. KWV, Cape Town Gin Co., Woodstock and Tapanga have **no
  pin** in this dataset's South Africa set (85 pins, checked by name) — same as the missing
  India names, nothing to add a row to.

### Corrections made in this pass

Re-running the matcher against the same cache (no new fetches) also picked up three fixes
that the earlier, interrupted run had missed, because the Goa MCA file only finished
downloading partway through the previous session:
- `shaiv-distilleries-private-limited`, `adinco-distilleries` and
  `gemini-distilleries-goa-private-limited` had CIN `""` (blank) and `medium` confidence in
  the file left on disk; the legal names are in `mca/Goa.csv`
  (`U15511GA2002PTC003076`, `U15500GA2012PTC007006`, `U51228GA1996PTC003395`), so they now
  carry a real CIN and `high` confidence.
- `central-distillery-and-breweries-anheuser-busch-inbev-india-limited` had a blank number;
  the pre-merger name SABMILLER INDIA LIMITED is in `mca/Maharashtra.csv`
  (`U65990MH1988PLC049687`), so it now carries that CIN at `medium`.

### Unmatched slugs, grouped by reason

**India (45 unmatched pins in the register-match table above; 2 of these do have a named
hand row, see below):**
1. **Named group/operator known, but no CIN resolves** (2): `ocean-king-distillers` (Goa
   Excise lists "M/s. Oceanking Distillers"; no exact hit in the 2015 MCA snapshot),
   `the-east-side-distillery` (Goa Excise lists the site as "M/s. Naveen Distillery"; same
   gap).
2. **No website on file to sweep, and no 2015-MCA name match** (6): `karnali-feed-industries-pra-li`,
   `veri-distillery`, `patel-aata-chakki`, `public-tiolets`, `kaju`, `amritha-distillery` —
   the first four are almost certainly OSM mis-tags (a feed mill, a flour mill/aata chakki, a
   public toilet block, a cashew stall) rather than distilleries; left as unmatched rather
   than guessed at.
3. **Website fetched, no CIN printed anywhere on the homepage/about/contact/terms pages, and
   no 2015-MCA name match** (28): includes several essential-oil steam-distillation units
   (`citro-essential-oils-distillery-industry`, `the-nilgiris-eucalyptus-oil-and-essential-oils-distillery-tneoeod`,
   `jagat-aroma-oils-distillery`) and post-2015 incorporations with no CIN on their sites
   (`allwyn-brewery-distillery-pvt-ltd`, `alcokraft-distilleries-limited`,
   `vms-distillery-india-p-limited`, `forever-distillery-pvt-ltd`/`-deoria`, and 21 more —
   full list in the matcher's stderr log).
4. **Website fetch failed or was blocked** (9): `gelephu-distillery` (the pin itself is in
   Gelephu, Bhutan, so the whole premise — an Indian CIN — does not apply), plus 8 sites that
   errored (DNS failure, TLS failure, or HTTP 4xx/5xx) on the fetch attempt logged in
   `websites.json`: `k-s-distillery`, `mountain-spirits-blenders-and-distillers-llp`,
   `ginglani-distillers-private-limited-manufacturing-plant`,
   `karnataka-brewers-and-distillers-association-bangalore` (a trade association, not a
   producer, in any case), `fertile-green-industries-private-limited-distillery`,
   `distillery-spent-wash-treatment` (an effluent-treatment facility, not a distillery
   company), `ankoor-distilleries-pvt-ltd`, `blu-kings-distillers-pvt-ltd`.

**South Africa (82 unmatched pins; 9 of these do have a named hand row, downgraded to `low`
per the rule above):**
1. **Named operator/company known, CIPC number not read** (9): `klipdrift-brandy`,
   `james-sedgwick-distillery`, `van-ryn-s-distillery-and-brandy-cellar` (all Heineken
   Beverages, ex-Distell), `wilderer-gin`, `hope-distillery`, `inverroche-distillery`,
   `boplaas-winery-and-distillery`, `mirari-gin-time-anchor-distillery`,
   `oude-molen-distillery` (Edward Snell & Co).
2. **No website on file** (1): `stillman-distillery`.
3. **Website fetched, no CIPC number printed on any crawled page, no other source available**
   (60): the large majority of South African craft distilleries — none had a registration
   number on their homepage, about, or contact/terms pages, and CIPC's own register could not
   be queried (terms). Full list in the matcher's stderr log.
4. **Website fetch failed or was blocked** (12): `gonzo-distilling`, `ginologist-distillery`,
   `die-uil-craft-distillery`, `the-franschhoek-distillery`,
   `galactic-spirits-distillery-contract-distilling`, `conspiracy-distillery-pty-ltd`,
   `hallucinogin-craft-distillery-jinn-bar`, `triumph-distillers`, `blaq-distillery-pty-ltd`,
   `dunhill-distillery`, `25-degrees-south-distillery`,
   `thomac-cc-distillers-of-organic-helichrysum-splendidum-oil`.

### Request log

Two sessions touched this country group:

1. **Previous (interrupted) session** — bulk MCA state-file downloads: 23 state/UT CSVs
   fetched from `data.gov.in` (one request each, see file sizes in the India register table
   above; these are fixed-URL bulk-file GETs, not search-endpoint queries). Website sweep:
   **379 requests** logged verbatim in `<scratchpad>/india-southafrica/run-websites.log`
   ("`requests this run: {'pin websites': 379} (cap 400)`") — homepage plus up to two
   contact/about/terms pages for up to ~180 pins with a website on file, at the matcher's
   built-in 1 request/second pace. Plus roughly 15 one-off research fetches while scoping
   registers (data.gov.in catalog/API/terms pages, the GODL licence text, the Goa excise
   contact page fetched once by hand with `curl -k` because of a broken TLS chain, the
   Maharashtra excise licensee search POSTed 4 times, one fetch each of the WCLA "licence
   database" page, CIPC's terms page, and a couple of dead-end probes).
2. **This session** — the matcher was run twice, both times with no `--fetch-*` flag and
   against the cache only: `requests this run: {} (cap 400)` both times. **0 new network
   requests.**

**Running total: 379 website-sweep requests + 0 this session = 379 of the 400-request cap**
for the search/website-sweep category (the 23 MCA bulk downloads and ~15 misc. research
fetches are fixed-URL page/file reads, not the rate-limited search-endpoint category the cap
targets, but are listed above for completeness). CIPC's own search endpoint was never queried,
per its terms.
