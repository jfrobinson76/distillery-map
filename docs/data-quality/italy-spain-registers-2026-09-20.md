# Italy and Spain: company registers and licence lists for the crosswalk, 20 September 2026

Research for the Italian and Spanish legs of `data/company-crosswalk/`. The map has 251 pins
with `country: "Italy"` and 66 with `country: "Spain"`. Italian province is parsed from the
Google-style address ("38123 Trento TN, Italy"); Spanish province from "..., Granada, Spain".
Italy: 213 pins carry a province, 38 do not. Spain: 42 carry a province, 24 do not.

Every "free / paid / bulk / API / licence" statement below comes from a page fetched on
20 Sep 2026; the URL is given each time. Where a page could not be read, the table says so.

## Summary

Neither country has a free company register that can be searched or downloaded in bulk, so
there is no Italian or Spanish equivalent of Companies House, the CRO extract, the TTB
permit list or the Corporations Canada CSV. The register survey is the main output of this
note. The candidate rows come from a different route: both countries oblige companies to
print their tax number on their own website (Italy: partita IVA, art. 35 DPR 633/1972;
Spain: NIF, LSSI art. 10), so the script reads the number from each pin's own site,
checksum-validates it, and reads the legal name printed next to it. The number is real and
the site is the pin's own, but nothing has been checked against a register yet, which is why
the note says "not yet checked against the register" on every machine row.

Spain has one usable bulk list: AESAN's RGSEAA food-business register (all registered food
businesses, key 30 = alcoholic beverages), reusable commercially with attribution. It gives
the legal name and the RGSEAA number but no NIF. Italy has no equivalent list.

## Italy

| Register / list | URL | Free lookup | Bulk | API | Paid | Terms on automated use | Used |
|---|---|---|---|---|---|---|---|
| Registro Imprese (InfoCamere, for the Camere di Commercio) | https://www.registroimprese.it/ | Yes, "Trova impresa". The service notes (modal "Note per l'utilizzo del servizio" on the home page) list what the free search returns: "Denominazione dell'impresa, Indicazione Sede/Unità Locale, Comune, indirizzo, forma giuridica (generica) e settore di attività (generico), Domicilio digitale/PEC". **No codice fiscale, no partita IVA, no REA number.** Ceased companies are included behind a filter; companies in liquidation or insolvency are not searchable. The search form is submitted through reCAPTCHA Enterprise (`grecaptcha.enterprise.execute` in the page source). | None | The autocomplete calls `https://risuggester.infocamere.it/raceSuggWeb/suggester` (page source); no public API | Visura ordinaria/storica, bilanci, "elenchi di imprese" (see Camere di Commercio row) | "E' inoltre vietato svolgere attività di distribuzione e/o vendita dei dati, nonché tentare di accedervi con modalità diverse da quelle consentite ed, in particolare, estrarre i dati per via automatica e massiva allo scopo di velocizzare le attività o creare autonome banche dati." (same modal). robots.txt allows everything, but the notes govern. | **Not queried** (terms forbid it, and it would not return the number anyway) |
| Camere di Commercio "elenchi di imprese" (the paid bulk route) | https://www.romagna.camcom.it/it/adempimenti/registro-imprese/accesso-alle-banche-dati/elenchi-di-imprese | No | Yes, paid: "€ 20.00 costo richiesta + € 0.12 per ogni nominativo" for the extended list, which carries "n. REA, n. R.I., codice fiscale, numero addetti e numero di telefono (se dichiarati), stato dell'impresa". Lists can be filtered by ATECO and territory, so a national ATECO 11.01 (distillazione, rettifica e miscelatura degli alcolici) extract would cost about €20 plus €0.12 per company. | None | All of it | Not stated on the page | Not used; this is the cheapest way to get codici fiscali for the whole sector if John wants them |
| Agenzia delle Entrate "Verifica partita IVA" | https://telematici.agenziaentrate.gov.it/VerificaPIVA/Scegli.do | Yes, one number at a time. Returns "lo stato - attiva, sospesa, cessata; la denominazione o il cognome e nome del titolare; la data di inizio attività e le eventuali date di sospensione/cessazione" (page text). Search is by number only, not by name. | None | None | Nothing | The form posts an image/audio CAPTCHA ("Codice di sicurezza", `inCaptchaChars`), so it cannot be scripted. | Not queried. It is the right tool for a human to confirm a P.IVA read from a website: status, legal name and start date in one screen. |
| EU VIES VAT validation (REST) | https://ec.europa.eu/taxation_customs/vies/rest-api/ms/IT/vat/{number} | Yes, one number at a time, no key. For Italy the response carries `name` and `address` (probe: FERRARI S.P.A., Via Emilia Est 1163, Modena). Only VAT numbers enrolled in the VIES archive (intra-EU traders) return valid; small domestic producers often are not enrolled. | None | Yes, REST and SOAP (`checkVatService.wsdl`) | Nothing | The service disclaimer (string `disclaimer_txt_para00` in `https://ec.europa.eu/taxation_customs/vies/assets/i18n/en.json`): "Any other use and any extraction and use of the data which is not in conformity with the objective of this site is strictly forbidden", the objective being confirmation of a counterparty's VAT number for intra-Community supplies. Concurrent-request limits are global per member state (`MS_MAX_CONCURRENT_REQ`). | **Not used for the crosswalk** beyond 4 probes (2 IT, 2 ES) made to learn what it returns. Building a register crosswalk is outside the stated objective. |
| dati.gov.it (national open-data catalogue) | https://www.dati.gov.it/opendata/api/3/action/package_search?q=registro+imprese | n/a | 188 hits for "registro imprese", all aggregates or sector lists (Regione Toscana "Imprese e unità locali InfoCamere 2024" is counts by province/ATECO; Lombardia "Registro dei microbirrifici" is a brewery list, CC0; Campania "Registro imprese storiche"). Query `distillerie OR grappa OR acquaviti OR distillati`: 0 datasets. **No company-level extract of the Registro Imprese exists on the catalogue.** | CKAN API | n/a | CKAN open | Confirms the gap |
| Agenzia delle Dogane e dei Monopoli (ADM), depositi fiscali alcoli | https://www.adm.gov.it/portale/en/dogane/operatore/accise/telematizzazione-delle-accise/settore-alcoli/depositari-autorizzati-settore-alcoli and .../tabelle-riferimento-alcoli-in-opendocument | No operator list. The "Depositari autorizzati settore alcoli" page is the telematic-filing service (register templates, ALCODA profile). The OpenDocument tables are code tables (TA01 to TA28: request types, offices, products, movements), not operators. ADM's datasets on dati.gov.it (8 of them) are excise revenue and declaration counts. | None | None | n/a | n/a | **There is no Italian equivalent of the TTB permit list.** The codice accisa (13 characters, 7th = A for alcohol) is assigned per deposito but ADM does not publish the list. |
| AssoDistil (trade association, "circa il 95% delle distillerie italiane") | https://assodistil.it/associati/ | Member section is 60 logos with no names or legal names in the HTML (all `alt="client"` bar one) | None | None | n/a | n/a | Not usable |
| Istituto Nazionale Grappa | https://www.istitutograppa.org/ | Connection failed (curl exit, no HTTP response) on two attempts, with and without www | Unknown | Unknown | Unknown | Unknown | Not read |
| OpenCorporates (IT and ES) | https://api.opencorporates.com/documentation/API-Reference | Web search only | No | Yes, key required: "An API key is required in order to use the OpenCorporates API." Free accounts only for open-data products under share-alike ("API accounts are free if you are going to be using the data in an open data project"), default "200 requests per month, and 50 requests per day". Paid plans "remove the OpenCorporates share-alike restrictions". `/registers/it` and `/registers/es` returned 404. | Paid for commercial use | Share-alike on the free tier | Skipped, as the brief said |

### Italy: what the script does instead

`it-registro-imprese` rows carry the partita IVA / codice fiscale numerico (11 digits) read
from the pin's own website. The number is the same identifier the Registro Imprese uses as
the company key, and the Luhn-style check digit is verified before a row is written. The
legal name is whatever company name with a legal form (S.r.l., S.p.A., S.n.c., S.a.s., S.S.,
Società Agricola, Soc. Coop., GmbH for South Tyrol) is printed within about 260 characters
before the number; when none is printed the row keeps the pin name and says so. Numbers that
sit next to a web-agency credit ("realizzato da", "powered by") are graded `low` because
Italian agencies print their own P.IVA in client footers.

Grades: `high` = legal name on the site matches the pin (token Jaccard >= 0.5 or pin tokens
a subset), or no legal form printed but the pin's own name sits next to the number; `medium`
= number found, legal name differs or absent; `low` = agency credit nearby or several numbers
on the page. Every row's note ends "not yet checked against the register (AdE VerificaPIVA
by hand)". That check is a 20-second CAPTCHA form per number.

## Spain

| Register / list | URL | Free lookup | Bulk | API | Paid | Terms on automated use | Used |
|---|---|---|---|---|---|---|---|
| Registro Mercantil Central (RMC), denominaciones sociales | https://www.rmc.es/ and https://www.rmc.es/Deno_consultas.aspx | **No free name search.** "Formulario para Consultas sobre disponibilidad de una Denominación Social (Acceso mediante pago con tarjeta o usuario registrado)"; the only free consulta is "Sólo disponible si ha obtenido una Certificación Denegatoria". The RMC holds names, not NIFs. | None | None | Denominación consultas and certificaciones (card payment; price not printed on the pages read) | Aviso legal (https://www.rmc.es/AvisoLegal.aspx): "No se permite la reproducción —total o parcialmente— de ninguno de los Contenidos y/o Servicios del Sitio Web sin autorización expresa". robots.txt disallows the `denominacionesSocialesInfo` listing controls and all `/privado` paths. | Not queried |
| Registro Mercantil provincial, via the Colegio de Registradores | https://sede.registradores.org/site/mercantil (redirects to a JavaScript portal) | No | None | None | "Nota informativa mercantil", "Depósito de cuentas", certificaciones (product list in the portal menu; prices not readable without login) | Not read (JS app) | Not used |
| BORME (Boletín Oficial del Registro Mercantil), AEBOE open data | API doc https://www.boe.es/datosabiertos/api/api.php, FAQ https://www.boe.es/datosabiertos/faq/borme.php | Yes, `GET /datosabiertos/api/borme/sumario/{yyyymmdd}` (JSON or XML, no key; probe for 20260918 returned the day's sumario with per-province section A items and PDF URLs, e.g. `BORME-A-2026-181-03.pdf`, 344 KB, Alicante). Sumarios exist "Desde enero de 2009". | Effectively yes, but as PDFs: section A ("Empresarios. Actos inscritos") is one PDF per province per publication day (roughly 50 PDFs of 150 to 350 KB each per day, ~250 days a year, so several GB per year). The acts carry the company name and the register data (tomo, folio, hoja) but **not the NIF**. The legacy `xml.php?id=` documents are disallowed in robots.txt. | Yes (above) | Nothing | Licence (https://www.boe.es/informacion/aviso_legal/index.php, "Condiciones de reutilización", resolution of 27 June 2024): reuse "para fines comerciales y no comerciales" is permitted, including "la modificación, adaptación, extracción, reordenación y combinación de la información", with attribution ("Basado en datos de la Agencia Estatal Boletín Oficial del Estado"), no suggestion of official status, and the date of last update kept. | **Not used.** Building a name index means parsing years of PDFs with a PDF library; stdlib-only and the 2 GB cap rule it out here. It is the durable open route to Spanish register (hoja) numbers if John wants one later. |
| LibreBORME (community BORME index) | https://librebor.me/ | Returned HTTP 403 with a Cloudflare "Just a moment..." challenge page; content and licence not readable. `borme.es` redirects to boe.es. | Unknown | Unknown | Unknown | Unknown | Not used |
| AEAT (tax agency) | n/a | Publishes no NIF lookup and no census. The VIES REST probe for a Spanish number returns `isValid` only, with `name` and `address` as "---" (Spain withholds them), so VIES cannot bridge NIF to name for Spain. | None | None | n/a | VIES disclaimer as in the Italy table | Not used |
| datos.gob.es (national open-data catalogue) | https://datos.gob.es/apidata/catalog/dataset/title/mercantil, .../sociedades, .../destilerías | n/a | Hits are statistics (INE "Estadística de Sociedades Mercantiles", CC-BY 4.0; regional SOCMER; Sociedades Agrarias de Transformación registers). "destilerías": 0 datasets. **No company-level register extract.** | Linked-data API | n/a | Open | Confirms the gap |
| **RGSEAA, Registro General Sanitario de Empresas Alimentarias y Alimentos (AESAN)** | https://www.aesan.gob.es/registro-sanitario/empresas-alimentarias; search https://rgsa-web-aesan.mscbs.es/rgsa/formulario_principal_js.jsp | Yes, by razón social, RGSEAA number, sector key, region (POST form, no CAPTCHA seen) | **Yes.** "Listado completo": https://www.aesan.gob.es/dam/jcr:0e74247c-5a4e-4c79-863b-b5dae6e79ada/260901_Industrias_RGSEAA.xlsx, 9.4 MB, titled "Listado de empresas alimentarias inscritas en España (RGSEAA) (actualizado a 1 de septiembre de 2026)". 142,426 rows; columns N_RGSEAA, Razon_Social, Domicilio_industrial, Provincia, CCAA, Clave, Clave_Descripcion. Key 30 "Bebidas alcohólicas": 8,762 rows (wine, beer and spirits together; no sub-activity in the file). Cadence: the file name is a date stamp; the page does not state a schedule. | None beyond the form | Nothing | Aviso legal (https://www.aesan.gob.es/aviso-legal): "La información disponible en este sitio web, salvo indicación expresa en contrario, es susceptible de reutilización; quedando autorizada su reproducción total o parcial, modificación, distribución y comunicación, para usos comerciales y no comerciales", subject to not distorting the content, citing the source and stating the date of last update. | **Used** as the licence layer (`es-rgseaa`). It gives the legal name (razón social) and province, which is the bridge from trading name to legal name; the NIF is not in the file. |

### Spain: what the script does instead

`es-rmc` rows carry the NIF read from the pin's own website (usually the "aviso legal"
page), checksum-validated for both company CIFs (letter + 7 digits + control) and personal
NIFs (8 digits + letter, sole traders). The registry code is `es-rmc` as the brief asked; the
number is the NIF, not a Registro Mercantil hoja. `es-rgseaa` rows in the licences file come
from the AESAN list, matched on normalised name (S.L., S.A., S.Coop, destilería(s), bodega(s),
licores, aguardientes stripped) with province agreement; single-token names (e.g. "Mallorca")
never grade above medium unless the full names agree.

## Method

`scripts/match_italy-spain_registers.py` (stdlib only, `--cache DIR`, no network without
`--fetch-websites`, idempotent):

1. Load the 317 pins; parse province, city and website.
2. With `--fetch-websites`: fetch each pin's home page (one request per second, 12 s timeout,
   TLS verified with the default context, cap 800 requests per run, every response cached
   under `<cache>/websites/` and every attempt logged in `<cache>/websites-log.json`). If no
   number is on the home page, follow up to three same-host links whose text or path looks
   like privacy / aviso legal / note legali / contatti / contacto, else two guessed paths
   (`/privacy-policy`, `/contatti`; `/aviso-legal`, `/contacto`). Hosts with a broken
   certificate chain are logged as `tls` and skipped; verification is never switched off.
3. Extract tax numbers with keyword regexes ("P.IVA", "Partita IVA", "C.F.", "VAT", "IT" +
   11 digits; "CIF", "NIF", "ES" + CIF pattern), validate the check digit, drop duplicates,
   flag numbers next to web-agency credits, and read the legal name printed before the
   number.
4. Match Spanish pins against RGSEAA key 30 (token Jaccard, province agreement).
5. Write `data/company-crosswalk/italy-spain-candidates.csv` and
   `data/company-crosswalk/italy-spain-licences.csv`.

The RGSEAA xlsx was converted to `rgseaa-industrias.csv` in the cache with a stdlib
zipfile + ElementTree pass (header is the second row of the sheet; the first is the title).

## Results

| Country | Region | Pins | High | Medium | Low | Unmatched |
|---|---|---|---|---|---|---|
| Italy | Trentino-Alto Adige | 37 | 20 | 6 | 1 | 10 |
| Italy | Piemonte | 30 | 9 | 6 | 1 | 14 |
| Italy | (no address) | 29 | 4 | 1 | 2 | 22 |
| Italy | Veneto | 25 | 13 | 5 | 0 | 7 |
| Italy | Lombardia | 25 | 5 | 4 | 2 | 14 |
| Italy | Emilia-Romagna | 15 | 12 | 0 | 0 | 3 |
| Italy | Friuli-Venezia Giulia | 12 | 4 | 3 | 0 | 5 |
| Italy | Toscana | 11 | 5 | 1 | 0 | 5 |
| Italy | Sicilia | 10 | 4 | 2 | 1 | 3 |
| Italy | Campania | 9 | 2 | 0 | 0 | 7 |
| Italy | Puglia | 9 | 2 | 2 | 0 | 5 |
| Italy | Marche | 6 | 2 | 2 | 0 | 2 |
| Italy | Lazio | 6 | 4 | 1 | 0 | 1 |
| Italy | Sardegna | 6 | 3 | 1 | 0 | 2 |
| Italy | Abruzzo | 6 | 2 | 1 | 1 | 2 |
| Italy | Liguria | 5 | 1 | 0 | 0 | 4 |
| Italy | Valle d'Aosta | 4 | 1 | 2 | 0 | 1 |
| Italy | Calabria | 3 | 1 | 1 | 0 | 1 |
| Italy | Umbria | 3 | 0 | 0 | 1 | 2 |
| Spain | (no address) | 24 | 1 | 2 | 0 | 21 |
| Spain | Illes Balears | 8 | 1 | 3 | 0 | 4 |
| Spain | Andalucia | 6 | 3 | 0 | 0 | 3 |
| Spain | Comunitat Valenciana | 5 | 1 | 0 | 0 | 4 |
| Spain | Galicia | 5 | 3 | 0 | 0 | 2 |
| Spain | Castilla y Leon | 4 | 1 | 1 | 0 | 2 |
| Spain | Cantabria | 2 | 0 | 1 | 0 | 1 |
| Spain | Murcia | 2 | 0 | 1 | 0 | 1 |
| Spain | Canarias | 2 | 0 | 0 | 0 | 2 |
| Spain | Navarra | 2 | 1 | 0 | 0 | 1 |
| Spain | Pais Vasco | 2 | 0 | 0 | 0 | 2 |
| Spain | Madrid | 2 | 1 | 0 | 0 | 1 |
| Spain | La Rioja | 1 | 1 | 0 | 0 | 0 |
| Spain | Cataluna | 1 | 0 | 1 | 0 | 0 |
| **Total** | | **317** | **107** | **47** | **9** | **154** |

Candidate rows: 168 (149 high/medium rows with a number, which is what the builder folds in). Licence rows: 38 `es-rgseaa` rows covering 27 Spanish pins.

| Country | Registry | High | Medium | Low |
|---|---|---|---|---|
| Italy | `it-registro-imprese` | 94 | 38 | 11 |
| Spain | `es-rmc` | 13 | 12 | 0 |
| Spain | `es-rgseaa` (licences file) | 11 | 17 | 10 |

## Request log, 20 Sep 2026

- Pins' own websites: 518 distinct URLs fetched across the fetch runs (277 distinct hosts), one request per second, 12 s timeout, TLS verified with the default `ssl` context (no `CERT_NONE`, no `check_hostname = False`). Outcomes by final status: 200 = 439, 404 = 37, 403 = 22, error = 10, tls = 6, 500 = 1, 302 = 1, 402 = 1, timeout = 1. Hosts skipped for TLS/certificate errors (broken chain, logged and never fetched insecurely): 6. Cap per run: 800; the crawl never reached it. `timeout`/`error`/`tls` outcomes are retried on the next `--fetch-websites` run; `404`/`403`/`402`/`500`/`302` are treated as durable failures and not retried.
- Registro Imprese free search (`registroimprese.it`, InfoCamere suggester): 0 requests (terms forbid automated extraction).
- Agenzia delle Entrate VerificaPIVA: 0 requests (CAPTCHA).
- VIES REST API: 4 probes (IT 00456500288 invalid, IT 00159560366 Ferrari S.p.A., ES A28000032 invalid, ES A28015865 valid, name withheld) to learn the response shape; not used for matching.
- Registro Mercantil Central: 0 searches (paid). BORME sumario API: 2 requests (one 404 for a Saturday, one sumario for 18 Sep 2026).
- dati.gov.it CKAN API: 6 searches. datos.gob.es API: 8 searches. AESAN: 1 download (9.4 MB xlsx).
- Search-endpoint total against the 400 cap: 20 (unchanged by the TLS fix and rerun, which only touched the per-website fetch pool, tracked separately against its own 800 cap).

## Unmatched pins, by reason

- **site unreachable (not fetched)** (77): `maxentia`, `distillerie-camel-spa-bepi-tosolini`, `destileria-rios`, `distillerie-aragonesi`, `aguilar-destilerias`, `grappa-brugnolaro`, `cellocco-elefante`, `distilleria-tranquillini`, `destilerias-pepe-albela`, `casa-d-amalfi`, `a-distilleria-toscana`, `distillerie-faled`, `fabrica-de-licors-hijo-de-j-juan-mompo`, `fabrica-de-anisados-la-violetera`, `distilleria-driussi`, `puni-destillerie`, `distilleria-schiavo`, `distilleria-le-crode`, `destileria-de-arehucas`, `distilleria-fratelli-caffo`, `distilleria-dellavalle`, `destileria-sinc`, `destileria-patxaran-zoco`, `destilerias-el-clavel-1896`, `siderit`, `destileria-bizkaia-sl-fabrica-de-licores`, `distiller-s-a`, `la-vecchia-distilleria`, `mallorca-gin-distillery`, `antica-distilleria-quaglia`, `distillerie-brillo-brillo-srlsb`, `gino12-distillery`, `distilleria-azienda-agricola-cascina-la-noce`, `strada-ferrata-distilleria-originale`, `fratelli-branca-distillerie-srl`, `distilleria-artigianale-milano`, `distilleria-radaelli-sas`, `doa-distilleria-orobica-autonoma`, `distilleria-artigiana-carlo-gobetti`, `le-distillerie-di-sarnico-1886`, `distillerie-valentini-1872`, `distilleria-negroni-srl`, `ladinia-distillery`, `distilleria-aquileia`, `mercedes-de-mezzo-distillerie-s-r-l`, `noara-mediterranean-distillery`, `the-ideas-distillery`, `cala-dor-gin-distillery`, `xoriguer-oficina-destileria`, `destilerias-san-valero-s-coop`, `distilleria-alma`, `monterbe-distilleria-artigianale`, `antiche-distillerie-poscia`, `distilleria-morelli-dante`, `distilleria-urbana-italia`, `green-heart-distillery-s-r-l`, `distilleria-casale-della-montagna-di-jeremy-palazzolo-c-s-a-s`, `distilleria-tremontis`, `distilleria-del-barbaresco`, `distilleria-locatelli-fabrizio`, `distilleria-del-limoncino-amalfi`, `5060-distilleria-rurale`, `distilleria-de-luca-srl`, `distilleria-leanza-1890`, `distillerie-clandestine`, `peter-in-florence-distillery`, `distilleria-flaminia`, `distilleria-clandestina`, `ditta-silvio-meletti-distilleria-spaccio-aziendale`, `il-cerro-distilleria`, `monti-s-distillery`, `distilleria-bocchino`, `distilleria-scardina-srl`, `distilleria-marna`, `distilleria-ghelfi-francesco-s-n-c-di-ghelfi-alessandro-e-ghelfi-stef`, `agro-grape-distillery-s-l`, `destileria-zumaque-s-l`
- **no website on the pin** (32): `distilleria-giacomozzi`, `destileria-de-alcohol-sevilla`, `orujo-y-licores-valle-de-bedoya`, `distillerie-valdoglio`, `truebano-aguardientes-s-l`, `acetaia-terre-di-matilde-di-canossa`, `cantine-scarpari`, `filippi-ezio-wine-beer-spirit`, `saccharomyces-beerfirm`, `terre-dei-calanchi-piceni`, `alcoholera-de-santib-ez-de-vidriales`, `cooperativa-alcoholera-mopesa-factory`, `destillery-at-24-san-ildefonso-street-utiel`, `fassina`, `fabrica-de-aguardiente`, `joaquin-vento-destillery`, `nave-de-la-cooperativa-campo-de-tejada`, `distillerie-nonino-sito-produttivo`, `fischerhof`, `les-bieres-du-grand-saint-bernard`, `la-collina-di-ovi-antonio-c`, `licores-de-mariola`, `dismavi`, `lagar-o-solleiro`, `distilleria-marchisio`, `grappa-mazzetti-altavilla`, `dec-impianti-impianto-recupero-solventi-huhtamaki-flexibles-italy`, `destileria-segarra`, `distilleria-enrico-toro`, `el-granero-de-san-francisco`, `antoni-nadal`, `la-navarra-sa`
- **site returned HTTP 403** (22): `distilleria-lidia`, `rossi-d-angera`, `futuredrink-srl`, `liquorificio-il-re-dei-re`, `fondazione-prada`, `fabrica-de-aguardientes-los-tres-hermanos`, `distillerie-st-roch`, `bodegues-tunel`, `basque-moonshiners`, `antica-distilleria-cugge`, `distilleria-sibona`, `eugin-distilleria-indipendente`, `distilleria-pagura-1879`, `mchenry-distillery-italia`, `distilleria-amato-liquori`, `breaking-booze-distillery`, `liquori-toro-enrico-toro-distilleria`, `distilleria-dr-m-montanaro`, `distilleria-bellomi`, `distilleria-cinque-terre`, `distillerie-pietro-mazzetti-c-s-a-s`, `era-destileria`
- **site unreachable (error)** (10): `distillerie-carlo-novelli`, `pacharan-el-purriego`, `opificio-il-reale`, `distilleria-angeli`, `distillerie-venete-denever-srl`, `distillerie-cappello-srl`, `ciminiera-distilleria-de-luca`, `distilleria-carpenito`, `distillery-gualco-s-n-c`, `la-destileria-1888`
- **site unreachable (tls)** (6): `distilleria-erboristica-alpina`, `distillerie-zini`, `distilleria-marzadro`, `distilleria-bailoni-trento`, `pircher-brennerei`, `del-lama-distillery`
- **site unreachable (timeout)** (2): `pircher`, `distilleria-artigianale-effluvium`
- **site returned HTTP 404** (2): `bognanco-birra-distillery`, `lucrezio-r-distilleria`
- **site returned HTTP 500** (1): `distilleria-vieux-moulin`
- **no VAT/tax number on home or legal pages** (1): `distilleria-bonaventura-maschio-s-r-l`
- **site returned HTTP 402** (1): `destileria-spirit-tellers-distilled-stories`

## Gaps and calls for John

- **No register check yet.** Every machine row is a number read from the pin's own site.
  Before any row is promoted, the Italian numbers should go through the AdE "Verifica
  partita IVA" form (status, legal name, start date; CAPTCHA, by hand) and the Spanish ones
  through a Registradores nota or the RGSEAA legal name. The `verified` column stays blank
  until then.
- **Paid bulk for Italy is cheap.** A Camera di Commercio "elenco esteso" for ATECO 11.01
  nationally is about €20 plus €0.12 per company and carries codice fiscale, REA number and
  status. That would replace the website route for Italy in one purchase.
- **BORME is the open route for Spain**, but it needs a PDF parser and multi-GB history; it
  yields register hoja numbers and acts, not NIFs.
- **VIES**: usable by a human for a handful of Italian numbers (it returns name and address
  for Italy), but its disclaimer limits use to intra-EU trade checks, so it is not wired into
  the script.
- **RGSEAA licence call**: AESAN's terms allow commercial reuse with attribution and the
  update date; the licences file notes "list dated 1 Sep 2026" on every row. No share-alike
  or non-commercial clause, so no licence flag beyond attribution.
- Pins with no website (32) and pins whose site was unreachable or printed no number stay
  unmatched; the reasons are listed above.
- **Legal-form regex made case-insensitive, 20 Sep, later the same day.** The first run
  matched `S.r.l.` / `S.p.A.` only as written, so a footer printing "SRL" or "SPA" in caps
  was not read as a legal name and the row fell back to the own-name-proximity grade. Fixed
  with `re.I` on the suffix alternatives, the leading capture kept case-sensitive
  (`(?-i:[A-ZÀ-Ü0-9])`) so it cannot start mid-word, and fragments rejected (postcodes,
  "es una sociedad limitada", anything with brackets). Rerun from the same cache: 40 more
  rows carry the printed legal name (Leonardelli SRL, Mazzetti d'Altavilla srl, Antiche
  Distillerie Riunite for Rossi d'Asiago), one grade moved down and correctly so
  (Magnoberta's legal entity is Luparia Alberto & Figli sas). High/medium/low 107/48/8.
- **The matcher was not idempotent before this pass.** The candidates/licences files
  inherited from the previous agent (timestamped 07:01, alongside a `run1.log` claiming 31
  high / 124 medium / 14 low) did not reproduce when the current, TLS-fixed script was rerun
  against the same cache — a clean rerun (both with and without `--fetch-websites`,
  cache-complete) gives the same output every time: 107 high / 47 medium / 9 low PIN-level,
  168 candidate rows. Two independent reruns of the current script against the same cache
  produced byte-identical CSVs (diffed). The 168-row file in the repo now is that verified,
  reproducible output; the earlier 171-row file could not be reconciled (no backup existed to
  diff against) and is superseded. No TLS bypass exists in either version — the change is in
  how many rows a legal name was successfully extracted for, not in what was fetched.
