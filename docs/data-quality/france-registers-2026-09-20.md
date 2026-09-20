# France: company registers and licence lists for the crosswalk, 20 September 2026

Research for the French leg of `data/company-crosswalk/`. The map has 481 pins with
`country: "France"`: 358 mainland pins with a postcode in the address, 5 Corsica, 28 in the
overseas départements (Guadeloupe 10, Martinique 12, Réunion 6) and 90 with no postcode
(mostly OSM pins with an empty address). Two French rows already sat in the generated
spine from Wikidata (Warenghem SIREN 436150049; Hennessy -> LVMH 775670417); the matcher
drops any row that repeats a slug + number already in `company-crosswalk.csv`.

Every "free / bulk / API / licence" claim below comes from a page or API response fetched on
20 Sep 2026. Where a site blocked the fetch, the table says so.

## Summary

France has one register that matters and it is fully open: INSEE's Sirene, published under
the Licence Ouverte / Etalab 2.0, with a public search API that needs no key. Every legal unit
whose principal activity is NAF 11.01Z "Production de boissons alcooliques distillées" was
pulled through that API (2,610 units, 1,833 of them active, 105 pages of 25) and matched
locally; pins still unmatched then got one name search each, filtered to their département.
Result: 347 of 481 pins have a SIREN candidate (271 high, 55 medium, 21 low, Warenghem's
existing spine row counted), 134 unmatched.

There is no licence layer. French customs (DGDDI) does not publish a list of entrepositaires
agréés (the excise status a distillery needs); the interprofessions (BNIC, BNIA, IDAC) keep
member lists, not registers. No `france-licences.csv` is written.

## Company registers

| Register | URL | Free lookup | Bulk open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| Sirene (INSEE) through the **API Recherche d'entreprises** (Annuaire des Entreprises, DINUM) | https://recherche-entreprises.api.gouv.fr (spec: https://recherche-entreprises.api.gouv.fr/openapi.json; UI: https://annuaire-entreprises.data.gouv.fr) | Yes. The OpenAPI description says the API is "totalement ouverte d'accès"; excluded are non-diffusible companies (sole traders who opted out) and companies refused RCS registration. It states it is a search API, not full Sirene access. | Yes. data.gouv dataset "Données des entreprises utilisées dans l'Annuaire des Entreprises", https://www.data.gouv.fr/datasets/donnees-des-entreprises-utilisees-dans-lannuaire-des-entreprises, licence `lov2` (Licence Ouverte 2.0), **daily**, last update 19 Sep 2026. Files: unites-legales csv.gz 808.5 MB / parquet 1.13 GB; etablissements csv.gz 1.00 GB / parquet 1.69 GB. Not downloaded: the API with the NAF filter covers the same ground in 105 requests. | `GET /search`: `q` (name, address, dirigeants, or a SIREN/SIRET), `activite_principale` (NAF, **legal unit only**, comma list), `departement` / `code_postal` / `code_commune` (filter on establishments), `etat_administratif` (A/C), `nature_juridique`, `nom_personne`, `per_page` (max 25), `page`, `minimal=true` + `include=siege,dirigeants,matching_etablissements,finances,tva`. No key. Rate limit in the spec: "au maximum 7 requêtes par seconde" per IP, 30/s per ASN, HTTP 429 with `Retry-After` when exceeded, explicit `User-Agent` recommended, access may be restricted in busy periods. `GET /near_point` also exists. Spec licence: MIT. | Nothing | **Yes**, sole source. Matcher stays at <= 1 request/second |
| Sirene bulk files (INSEE on data.gouv) | https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret | n/a | Yes, licence `lov2`, **monthly** (1 Sep 2026 edition, last update 1 Sep 2026). StockUniteLegale zip 974.6 MB (parquet 708.6 MB); StockEtablissement zip 2.87 GB (parquet 2.21 GB); plus Historique, LiensSuccession and Doublons files and the PDF/CSV file layouts. The dataset text says INSEE now feeds data.gouv directly (stable URLs only for automation) and that NAF 2025 codes are double-published since 16 Dec 2025 with the switch in January 2027. | n/a | Nothing | No. Establishment-level NAF needs the 2.87 GB StockEtablissement zip, over the 2 GB cap; the legal-unit file is 975 MB but the API gives the same 11.01Z set in 105 calls |
| API Sirene (INSEE, api.insee.fr) | Catalogue entry: https://www.data.gouv.fr/dataservices/api-sirene-open-data (listed at https://api.gouv.fr/les-api/api-sirene) | The data.gouv API catalogue labels "API Sirene open data" as **"Ouvert avec un compte"** (free, needs an account and token) and "API Sirene dont unités à diffusion partielle" as "Accès restreint". | n/a | Yes, token behind an account. **Not registered**, per the brief. | Nothing stated | No |
| API Entreprise (DINUM, Sirene bundle) | https://api.gouv.fr/les-api/api-entreprise | Catalogue label "Accès restreint": for administrations only. | n/a | Restricted | n/a | No |
| INPI, Registre national des entreprises (RNE), data.inpi.fr | https://data.inpi.fr | **Not verified.** `https://data.inpi.fr/content/editorial/Acces_API_Entreprises` returned a Cloudflare 403 "you have been blocked" page to a script. A data.gouv dataset search for "inpi rne" returned 0 datasets; "INPI" returned only the BCE/INPI financial-ratio datasets (lov2). Not registered, per the brief. | Not located on data.gouv | Not verified | Unknown | No |
| BODACC (DILA) | https://www.data.gouv.fr/datasets/bodacc | n/a | Yes, licence `fr-lo` (Licence Ouverte), resources: current-year XML flow, historical XML flow, CSV/JSON/Excel export from the Opendatasoft API, DTD and documentation PDFs; dataset last updated 20 Sep 2026. | Opendatasoft export API (from the resource list; not queried) | Nothing | No. Announcements (incorporations, sales, insolvencies), useful later for status changes, not for name-to-SIREN matching |

What a free lookup returns (API Recherche d'entreprises, observed in the responses): SIREN,
`nom_complet` (with the enseigne in brackets), `nom_raison_sociale`, `sigle`, NAF of the legal
unit and its NAF 2025 code, `nature_juridique` (INSEE legal-form code), `etat_administratif`
(A active / C ceased), `date_creation`, `categorie_entreprise`, employee band, `siege` (SIRET,
full address, postcode, INSEE commune code, département, coordinates, enseignes, `nom_commercial`,
establishment state A/F), `matching_etablissements` (the establishments that satisfied a
location filter, same fields), `dirigeants` (natural persons: names, qualité, birth year; legal
persons: name, SIREN, qualité), plus `finances` and `tva` blocks when not minimal. No paid tier.

## Licence and trade lists (second identifier layer)

| List | URL | Legal name? | Notes |
|---|---|---|---|
| DGDDI entrepositaires agréés (excise warehousekeepers) | https://www.douane.gouv.fr | n/a | **No public list found.** `/fiche/statut-dentrepositaire-agree` and `/fiche/lentrepositaire-agree` both returned 404; the site search for "entrepositaire agréé" returned a page with no fiche link. Treated as not published. |
| BNIC (Cognac interprofession) | https://www.cognac.fr | n/a | Home page fetched (200); it carries no "annuaire" or house list link. A trade body, not a register. Not used. |
| BNIA (Armagnac), IDAC (Calvados) | not fetched, no URL verified | n/a | Trade bodies; member lists at best, only useful for bridging a brand name to a house name by hand. Not used. |

No licence layer, so no `france-licences.csv`.

## Method

`scripts/match_france_registers.py` (stdlib only, `--cache DIR`, no network without
`--fetch-naf` / `--fetch-names`, every response cached, reruns offline and byte-identical):

1. **NAF pass.** Pull every legal unit with `activite_principale=11.01Z` (105 pages, 2,610 units,
   cached in `naf-1101z.json`). Index the legal name, `nom_complet`, sigle, `nom_commercial` and
   every enseigne. For each pin: token Jaccard after stripping accents, legal forms (SAS, SARL,
   SA, EURL, SCEA, EARL, GAEC, SCI, SNC, société, établissements...) and generic words
   (distillerie, distillery, domaine, maison, château, spiritueux, brasserie, ferme, famille...).
   Location from the pin address: 5-digit postcode -> département (97x kept as three digits,
   Corsica 200/201 -> 2A else 2B) and commune.
2. **Grades.** `high` = exact name or Jaccard >= 0.8, unit active, and postcode/commune agrees or
   the name is distinctive (>= 2 shared tokens, or one shared token of >= 7 letters). `medium`
   = same but ceased, or Jaccard 0.6-0.8 with département agreement. `low` = weaker.
   Containment upgrade: when one name is wholly inside the other (Google Places names carry
   taglines: "Distillerie du Tigre Thiré" vs "DISTILLERIE DU TIGRE") and the postcode or
   commune agrees, the pair is graded on the shared part.
3. **Name pass.** Pins without a high/medium NAF hit get `q=<pin name head>` (text before the
   first " - ", ":" or "(", six words max) with `departement=<pin dept>` when known, else
   nationwide. The API ANDs every term, so a second query with generic words removed
   ("Cognac Frapin" -> "frapin", "Distillery G. Miclo" -> "g miclo") runs when the first
   finds nothing. Hits are graded as above with extra caps: SCI / property / construction NAF
   -> `low` and marked "not the operator"; holding NAF (64.20Z, 70.10Z) -> at most `medium`,
   relation `group`; no location agreement and a NAF outside the drinks set (11.0x, 46.34Z,
   47.25Z, 01.21Z vines, 01.28Z aromatic plants, 20.53Z essential oils, 20.14Z industrial
   alcohol, 10.89Z) -> at most `medium`; two or more distinct companies at the top grade with
   no location agreement -> all dropped a grade.
4. **Hand rows** (`match_method: hand`, `relation: operator`, group named in the note; the
   register row itself still comes from the API): Hennessy -> Société Jas Hennessy & C°
   (905620035, Moët Hennessy / LVMH); Palais Bénédictine -> Distillerie Bénédictine 340083724
   and Bénédictine Distil. Liqueur Abbaye Fécamp 345550172 (Bacardi; both `medium`, see the
   status in the note); Chartreuse Aiguenoire -> Cie Française de la Grande Chartreuse
   054502356 (11.01Z); Saint-James -> Rhums Martiniquais Saint-James 303159883 and Saint James
   International 303152250 (La Martiniquaise-Bardinet / COFEPP); Depaz -> Distillerie Depaz
   353432529 (La Martiniquaise; unit ceased, so `medium`); Dillon -> Distillerie Dillon
   466203338 (La Martiniquaise); La Mauny -> Les Planteurs de la Mauny 807606959 and La Mauny
   Vallée SA 382842045 (Campari, Rhumantilles); Rhum JM -> Héritiers Crassous de Médeuil
   410151526 (GBH); Boulard -> Société Anonyme Calvados Boulard 706620275 and Soc. des
   Calvados Boulard et Cie 950334946 (Spirit France Diffusion, both `medium`); Père Magloire:
   only a ceased tasting-bar unit was returned, no operating-company row.
5. Rows already in `company-crosswalk.csv` for the same slug and SIREN are dropped (Warenghem).

Output: `data/company-crosswalk/france-candidates.csv`, 428 rows, registry `fr-sirene`,
`company_number` = SIREN, SIRET of the closest establishment plus postcode, commune, NAF,
creation date, unit status and up to three dirigeants in the note. `source` is the Annuaire
page for the SIREN. Row breakdown: 265 from the NAF pull, 149 from name searches, 14 hand;
283 high / 89 medium / 56 low; relation 411 self, 14 operator, 3 group.

## Result table (best grade per pin)

| Group | pins | high | medium | low | unmatched |
|---|---|---|---|---|---|
| mainland, postcode in address | 358 | 235 | 35 | 9 | 79 |
| Corsica (2A/2B) | 5 | 1 | 0 | 1 | 3 |
| Guadeloupe (971) | 10 | 8 | 1 | 0 | 1 |
| Martinique (972) | 12 | 4 | 1 | 1 | 6 |
| Réunion (974) | 6 | 3 | 0 | 2 | 1 |
| no postcode in address | 90 | 20 | 18 | 8 | 44 |
| **Total** | **481** | **271** | **55** | **21** | **134** |

Warenghem counts as high (spine row). Guyane has no pins.

## Request log, 20 Sep 2026

All against `https://recherche-entreprises.api.gouv.fr/search`, one request per second or
slower, explicit User-Agent, no 429 seen. Self-imposed cap 400.

| Call | Requests |
|---|---|
| Manual probes (11.01Z page 1; 11.01Z active count) | 2 |
| NAF 11.01Z pull, pages 1-105 | 105 |
| Name search, first form (pin name head, département filter where known) | 238 |
| Name search, second form (distinctive tokens only) | 50 (capped) |
| **Total** | **395** |

Non-search fetches (not counted against the cap): data.gouv dataset API x4, the OpenAPI spec
and docs page, api.gouv catalogue x2, data.inpi.fr x1 (403), douane.gouv.fr x3 (404, 404,
search page), cognac.fr x1. Per-request log with timestamps and result counts in the cache
folder (`request-log.txt`, scratchpad, not committed).

75 pins still have a second-form query pending because the cap was reached; rerun
`--fetch-names --max-requests 80` on another day to clear them (the first-form responses are
cached, so only the pending queries cost requests).

## Unmatched (134 pins), by reason

**Searched with the département filter, no plausible hit (85).** Both query forms ran for the
alphabetically earlier ones; the legal name shares no token with the pin, the company sits in
another département, or the trading name is not recorded as an enseigne in Sirene.

- Spirits producers, worth a hand search (59): glann-ar-mor-distillery (Celtic Whisky
  Compagnie), cognac-frapin, distillerie-citadelle-gin (Maison Ferrand), distillery-g-miclo,
  trois-rivieres-distillery (Campari / Rhumantilles), rhum-a1710, habitation-saint-etienne,
  distillerie-moon-harbor, distillerie-calvados-garnier, distillerie-du-maout,
  distillerie-grallet-dupic, distillerie-brana-showroom, distillerie-labarrere-1773,
  distillerie-belin, distillerie-wezenn, distillerie-bonvalet, distillerie-g-hardy,
  distillerie-h-b-s, distillerie-bonne-mere, distillerie-lachanenche,
  distillerie-le-serpent-vert-alchimie-botanic, distillerie-terre-d-alchimie,
  distillerie-montjoie, distillerie-les-coulets, distillerie-mobydick, distillerie-54-colnet,
  distillerie-alpitude-45, distillerie-aux-quatre-sillons, distillerie-du-chant-du-cygne,
  distillerie-du-pere-jo, distillerie-le-vadrouilleur, le-vadrouilleur-distillerie,
  distillerie-artisanale-jm-leisen-eaux-de-vie-whisky-gin-vodka-vins-cidre-cadeaux,
  distillerie-les-ll-du-temps, distillerie-les-cooperatives-de-thouarce,
  distillerie-vignerons-d-oleron, distillerie-traditionnelle-gaec-du-riou-famille-gradian,
  alessandri-pierre-distillerie-u-mandriolu, braud-quenesson, cidrerie-distillerie-jouny,
  cooperative-cavale, domaine-distillerie-mabillot-sainte-lizaigne,
  famille-moutard-champagnes-vins-distillerie, ferme-distillerie-de-faronville,
  home-distillers-distillerie-des-bughes-whisky-auvergnat, hippodeodevie,
  jeevro-micro-distillerie, la-distillerie-des-achards, la-distillerie-du-ponant,
  la-distillerie-generale, la-fabrique-a-alcools-distillerie-chevreuse,
  les-distilleries-ideales, liqueur-du-berry, marie-louise-tissot,
  payet-riviere-sucrerie-distillerie, saveurs-du-charmant-som, swertia,
  terra-distillerie-gin-vodka-artisanaux, distillery-vitalba-essential-oils-of-corsica.
- Not spirits producers (26): lavender and essential-oil stills, brewery-distilleries, a
  hotel, a restaurant, an art gallery, a gîte, a rose garden, a function room:
  aroma-plantes-distillerie, artibrassage87-brasserie-distillerie-artisanale,
  biere-octopus-distillerie-o-spirit-cui-cui-soda,
  bleudiois-distillerie-de-lavande-huile-essentielle-de-lavande-et-de-lavandin,
  brasserie-distillerie-cordoeil-earl-cordoeil, brasserie-distillerie-de-vauclair-la-choue,
  brasserie-distillerie-dreum, brasserie-distillerie-du-pays-des-lacs,
  brasserie-distillerie-la-canya, brasserie-distillerie-veyrat,
  brasserie-et-distillerie-du-mouli, distillerie-d-huiles-essentielles, distillerie-de-lavande,
  distillerie-de-lavande-les-agnels, distillerie-gites-de-france, distillerie-les-essentielles,
  distillery-4-vallees-distillerie-de-lavande,
  domaine-la-distillerie-location-de-salle-dans-l-ain-rhone-alpes,
  galerie-d-art-la-distillerie-66, hotel-de-la-distillerie, la-brasserie-distillerie-de-dinan,
  microbrasserie-distillerie-artisanale-radwulf, microbrasserie-distillerie-soavenn,
  restaurant-la-distillerie-maison-faivre-cuisine-gastronomique-francaise-traiteur,
  terre-de-rose-distillerie-roseraie,
  un-mas-en-provence-distillerie-d-huiles-essentielles-bio-cosmetique-en-occitanie.

**Searched nationwide (no address on the pin), no plausible hit (40).** Without a
département the search is noisy and the grader refuses name-only hits with a non-drinks NAF
or several same-name companies: alambic-beauquis-pere-et-fils, blind-pig-distillers (the 64
pin "blind-pigs-distillers" did match: Esprit des Gaves), boutique-ite-laster,
chateau-pomes-peberere, cognac-couprie, cognac-seguinot, cuvee-des-dracs, damoiseau-distillery
(the 97160 pin "distillerie-rhum-damoiseau" matched), distillerie-associative,
distillerie-cusenier, distillerie-de-la-roche-saint-secret (a CUMA lavender still was
returned, 20.53Z, nothing to confirm it), distillerie-de-merxheim,
distillerie-de-pierre-et-suzanne, distillerie-des-chartreux-de-fourvoirie,
distillerie-le-claux-du-puits, distillerie-les-fontaines, distillerie-maurin-vey,
distillerie-tisserand, distillerie-vinicole-du-blayais (Société de Distilleries Vinicoles du
Blayais 587020066 was returned; no location on the pin to confirm), domaine-de-lassaubatju,
domaine-de-laubesse, domaine-du-berdet, domaine-du-capitaine, domaine-du-peto, dpso-ottrott,
espace-fernet-branca, ferme-distillerie-du-petit-fahys, gabarex-daniel-burte, habitation-routa,
l-herbier-sous-la-rochette, la-maison-ryst-dupeyron, le-maine-castay, les-vergers-d-auvillars,
maison-eulriet, marcel-michel-fils-successeur, paties-james-jackie, sucrerie-de-francieres,
thienot, txopinondo-cidrerie-artisanale-basque, verveine-du-forez-maison-forissier.

**Not searched: nothing distinctive in the name (9).** brasserie-distillerie-la-gueule-de-lgd,
distillerie, distillerie-19-25-rue-du-commandant-ren-mouchotte, distillerie-artisanale,
distillery-schnapsbud, domaine-de-pere, la-distillerie,
la-distillerie-lieu-de-fabrique-spectacle-vivant, micro-brasserie-distillerie-k-g-green-valley.
These are OSM labels, not businesses; several are venues named "La Distillerie".

## Caveats for review

- Sirene excludes non-diffusible sole traders (opt-out under the INSEE diffusion rules), so
  small bouilleurs registered as individuals can be genuinely absent from the API.
- Many pins are not spirits businesses (lavender and essential-oil stills under 20.53Z or
  01.28Z, brewery-distilleries under 11.05Z, cognac and armagnac growers under 01.21Z). Those
  rows are graded on name and location like the rest; the NAF in the note tells the reviewer
  what the company actually does.
- Three-site companies appear once per pin (Distillerie de la Tour: Pons, Jonzac, Merpins,
  Gondrin, all SIREN 351427604 with the site SIRET in the note).
- All data used is Licence Ouverte 2.0; no licence call is needed for John.
