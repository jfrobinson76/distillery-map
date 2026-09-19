# Canada: company registers and licence lists for the crosswalk, 19 September 2026

Research for the Canadian leg of `data/company-crosswalk/`. The map has 270 pins with
`country: "Canada"` (after the 29 relabelled US-to-Canada pins on 19 Sep). Province is
parsed from the address: QC 61, ON 55, BC 55, AB 40, NS 18, SK 13, NB 11, MB 3, NL 2,
and 12 with no usable address.

Every "free / bulk / API" claim below comes from a page or API response fetched on
19 Sep 2026. Where a site blocked the fetch, the table says so rather than guessing.

## Summary

Three sources are free, bulk and licensed for reuse: the federal register, Quebec's RACJ
manufacturer-permit register (which carries the NEQ, the Quebec register number), and BC's
OrgBook API. Ontario has no bulk company file, but the AGCO manufacturer-licence list gives
the licensee's legal name, which is often a federal corporation or a numbered Ontario
company whose name is its OBR number. Alberta, Saskatchewan, Nova Scotia, New Brunswick,
Newfoundland and Manitoba have no bulk or API route; their pins only match if the company
is federally incorporated.

Canada's Business Registries (the federated search) exposes a JSON endpoint
(`https://ised-isde.canada.ca/cbr/srch/api/v3/search`, read from the site's `config.js`),
but its terms forbid automated use: "You are not allowed to use automated tools to copy,
search or scrape data from Canada's Business Registries" and "Automated tools that copy,
search or scrape search results are forbidden" (strings in the app bundle at
`https://ised-isde.canada.ca/cbr-rec/assets/index-y-6SjRgM.js`). It was not queried.
Its coverage, from the same bundle: federal, BC, AB, SK, MB, ON, QC, NB, NS, NL, PE, YT,
NT, NU.

## Company registers

| Jurisdiction | Register | Free lookup | Bulk open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| Federal | Corporations Canada, https://ised-isde.canada.ca/site/corporations-canada | Yes, web search | Yes. Open Government Licence - Canada, updated daily (CKAN `frequency: P1D`, last modified 19 Sep 2026). https://open.canada.ca/data/en/dataset/0032ce54-c5dd-4b66-99a0-320a7b5e99f2. Files: active CBCA 103.6 MB (644,875 rows), other active 9.2 MB (51,085), inactive CBCA 157.0 MB (828,816), plus the non-CBCA inactive file and French copies. Fields: corporation number, BN, names (two forms), governing act, status and status detail, anniversary date, year of last annual filing, registered office address, director min/max. No incorporation date, no directors. | Yes. `https://www.ic.gc.ca/app/scr/cc/CorporationsCanada/api/corporations/{id}.json?lang=eng`, documented at https://ised-isde.canada.ca/site/corporations-canada/en/accessing-federal-corporation-json-datasets. Returns names, addresses, BN, activities (incorporation and filings). The API Store entry (https://api.ised-isde.canada.ca/en/docs?api=corporations) shows a Public Plan at 60 hits per minute behind a login. | Certificates and document copies | Bulk files, matched locally |
| Quebec | Registraire des entreprises (REQ), https://www.registreentreprises.gouv.qc.ca | Yes, web search by name or NEQ | Yes in principle. Données Québec dataset `registre-des-entreprises`, licence **CC-BY-NC-SA 4.0** (non-commercial), bimonthly (CKAN metadata, last modified 16 Sep 2026). Download endpoint `.../GR03A2_22A_PIU_RecupDonnPub_PC/FichierDonneesOuvertes.aspx` returned **403 "accès temporairement interdit en raison d'une utilisation excessive"** on three attempts (HEAD and GET, with and without a browser user agent). Size unknown, not downloaded. | None found | Certified extracts | **Not used.** Two reasons: the licence is non-commercial, and the endpoint blocked the download. NEQs come from the RACJ permit register instead (below) |
| British Columbia | BC Registries; public copy in OrgBook BC, https://orgbook.gov.bc.ca | Yes | No bulk file. | Yes. `https://orgbook.gov.bc.ca/api/v4/` (OpenAPI at `/api/?format=openapi`): `search/topic`, `search/autocomplete`, `topic/{id}/credential-set`. No key. Response headers show `ratelimit-policy: 50; w=1` and `25; w=1`. Licence in the OpenAPI info block: "Access Only License - British Columbia"; the BC API Terms of Use (https://www2.gov.bc.ca/gov/content/data/policy-standards/data-policies/open-data/api-terms-of-use-for-ogl-information) say the information is governed by the Open Government Licence - British Columbia and the provider may impose limits without notice; attribution is required. Returns registration number (BC…, FM…, A…, S…), entity name history, entity status (ACT/HIS), entity type (BC, SP, GP, A…), registration date, business number. No addresses or directors in the topic search. | Corporate summaries via BC Registries | API, 200 requests in total, cached |
| Ontario | Ontario Business Registry (OBR), https://www.ontario.ca/page/ontario-business-registry | Yes, basic public record | None | None | Profile report $8, document copies $3, certificate of status $26 | Not queried (no bulk, no API). Legal names taken from the AGCO licence list; numbered Ontario companies give the OBR number directly |
| Alberta | Alberta Corporate Registry, via registry agents, https://www.alberta.ca/find-corporation-details | **No.** "Registry agents provide all of the search services"; "A registry agent will charge a government fee and a service fee" | None | None | All searches (registry-agent product catalogue) | Not used. Federal rows only |
| Saskatchewan | ISC Corporate Registry, https://corporateregistry.isc.ca (login portal) | Search sits behind the ISC customer portal. The information page (https://www.saskregistries.ca/corporateregistry/findanexistingbusiness/search-find-information-on-an-existing-business) says business information is public and available on request; profile reports carry type, status, registration date, addresses, directors and event history. The fee page only links a PDF. | None | Land Titles has an API; Corporate Registry does not (same page) | Profile reports | Not used. Federal rows only |
| Nova Scotia | Registry of Joint Stock Companies (RJSC Connect), https://rjsc.novascotia.ca | Yes. The Nova Scotia service page (https://www.novascotia.ca/search-business-or-non-profit-information-filed-registry-joint-stock-companies) says search is free by name, Registry ID or status and shows names, addresses, partners/directors/officers and activity history. `rjsc.novascotia.ca/search` itself returned a Cloudflare "you have been blocked" page to a script. | None | None | Standard and certified document copies | Not used. Federal rows only |
| New Brunswick | Corporate Affairs Registry Database, Service New Brunswick, https://www.pxw2.snb.ca/card_online/cardsearch.aspx | Not verified: every SNB and GNB page tried (`www2.snb.ca/.../registry.html`, `pxw1.snb.ca/snb7001/...`, `pxw2.snb.ca/card_online/cardsearch.aspx`, the GNB services page) returned 403 or a JavaScript challenge. | None found | None found | Unknown | Not used. Federal rows only |
| Newfoundland and Labrador | Companies and Deeds Online (CADO), https://cado.eservices.gov.nl.ca | Yes. "What's included" page (https://cado.eservices.gov.nl.ca/Company/CompanyWhatsIncluded.aspx): searching and viewing company records is free; records carry corporate name, registered office, directors, status ("In Good Standing" or not) and registration dates; no shareholder list. | None | None | Filings (incorporation $300 etc.), not searches | Not used. Federal rows only |
| Manitoba | Companies Office, Companies Online, https://companiesonline.gov.mb.ca | Yes, with an account. The office's guide (https://companiesoffice.gov.mb.ca/online_instructions/Searches_File_Summaries.pdf) says searches to determine whether a business is registered are free; results show name, registry number, status, compliance status, entity type and jurisdiction. | None | None | File Summary $5.00 per company | Not used. Federal rows only |

## Liquor manufacturer licence lists (second identifier layer)

| Province | List | Legal name? | Notes |
|---|---|---|---|
| BC | LCRB "Licensed Establishments in B.C.", https://catalogue.data.gov.bc.ca/dataset/licensed-establishments-in-b-c, file https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/liquor-regulation-licensing/reports/all_liquor_licensed_establishments_in_bc.xlsx | **Yes**, a `Licensee` column (legal name, or a list of individuals for sole proprietorships and partnerships) | Open Government Licence - British Columbia (CKAN record). 10,523 licence rows on 19 Sep 2026, of which 131 are Manufacturer / Distillery. Fields: licence number, type, sub-category, establishment name, address, city, local government, licensee, third-party operator, expiry. The download page says the reports are "updated regularly"; no cadence stated. |
| Ontario | AGCO "Liquor Manufacturer's Licence" open data, https://www.agco.ca/sites/default/files/opendata/OpenDataManufacturersLicences_En.csv (listed in the AGCO data inventory, https://www.agco.ca/en/general/data-inventory) | **Yes**, `Legal Entity Name` plus `Premises Name` | 3,718 rows on 19 Sep 2026 (all licence and endorsement types, breweries and wineries included); 190 active "Manufacturer's Licence - Distillery" rows plus expired, cancelled and deemed-to-continue rows. Fields: licence number, type, legal entity, premises, address, city, effective/issue/expiry dates, status, endorsements. Licence terms for the file are not stated on the fetched pages. |
| Quebec | RACJ "Registre des titulaires de permis de fabricant d'alcool en vigueur", https://www.donneesquebec.ca/recherche/dataset/racj-alcool-fabricant | **Yes**, `RaisonSociale`, `Titulaire` and the **NEQ** | CC-BY 4.0, monthly (CKAN; last modified 17 Sep 2026). CSV 305 KB, 1,811 permits, of which 83 "Distillateur" and 4 "Production artisanale d'alcools et spiritueux"; the rest are brewers, cider and wine makers, warehouses. Fields: permit type, legal name, holder, NEQ, permit number, category, establishment address, city, postal code. This is the route to Quebec register numbers while the REQ bulk file is unusable. |
| Alberta | AGLC "Alberta liquor manufacturers", https://aglc.ca/liquor/alberta-liquor-manufacturers, and https://albertamadeliquor.aglc.ca/find-alberta-liquor-manufacturers | Not verified | The aglc.ca page fetched is navigation only, with no list or file link; the albertamadeliquor.aglc.ca page returned 502 twice. Nothing usable on 19 Sep. |

## What the crosswalk does with this

`scripts/match_canada_registers.py` (stdlib only, no fetch without `--fetch-orgbook`):

1. Federal bulk files matched locally for all 270 pins (token Jaccard, city and province
   agreement, drinks-word signal for partial matches).
2. Quebec pins matched to RACJ permits; the NEQ goes into `qc-req` rows, and the legal
   name is cross-checked against the federal file.
3. Ontario pins matched to AGCO distillery licences; the legal name is cross-checked
   against the federal file, else an `on-obr` row with the number only when the name is
   a numbered Ontario company.
4. BC pins matched to LCRB distillery licences; the licensee legal name is searched in
   OrgBook (exact legal-name hit = high), then the pin name as a fallback.
5. Hand rows for Hiram Walker / Lot No. 40 (Hiram Walker & Sons Limited, Pernod Ricard
   Canada Ltée, Corby Spirit and Wine Limited), Crown Royal (Diageo Canada Inc.; the map
   pin is the visitor site at The Forks, Winnipeg, not the Gimli plant), Forty Creek
   (Campari), Alberta Distillers (Suntory), Glenora, Lucky Bastard.

Outputs: `data/company-crosswalk/canada-candidates.csv` (company-register rows) and
`data/company-crosswalk/canada-licences.csv` (licence rows, registries `on-agco`,
`bc-lcrb`, `qc-racj`). Nothing enters `company-crosswalk.csv` until a human copies a row
into the manual or operators file.

Request log, 19 Sep 2026: OrgBook 200 requests total (98 per matcher run, two runs, plus
4 probes), all at one request per second or slower, against a self-imposed cap of 400.
Canada's Business Registries search API: 0 requests. REQ download endpoint: 3 attempts,
all 403. No other search endpoint was called.

## Gaps

- AB (40 pins), SK (13), NS (18), NB (11), NL (2), MB (3): only federally incorporated
  companies match. Provincial numbers need the free web searches (NS, NL, MB by hand) or
  paid lookups (AB, SK).
- Quebec register numbers come from the RACJ permit list, so pins without a distiller or
  artisanal-spirits permit under a similar name stay unmatched, and REQ status and
  incorporation date are not checked.
- The federal CSV has no incorporation date; the `note` carries status, year of last
  annual filing and registered-office city instead.
- The Quebec REQ bulk licence (CC-BY-NC-SA) is a policy question for any commercial use
  of the crosswalk, separate from the download block.
