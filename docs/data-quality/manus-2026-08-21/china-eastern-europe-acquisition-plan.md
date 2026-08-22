# Regional Distillery Data Acquisition: China and Eastern Europe

**Prepared:** 21 August 2026  
**Objective:** Expand the static global GeoJSON with missing Chinese distilling sites and Eastern European fruit-spirit producers without creating a licensing, provenance, or data-quality problem.

## Executive conclusion

**Do not scrape Baidu Maps.** Baidu’s current platform terms permit use of documented services within a product, but prohibit direct storage, caching, downloading, mirroring, or creating a database/derivative from service-related content without explicit permission. The terms also require applicable paid authorisation for commercial use. A public `distilleries.geojson` derived from Baidu POIs would therefore need a **written data licence that expressly allows persistent storage, deduplicated transformation, and public redistribution**. [1]

Baidu is technically capable of improving China coverage after a licence is in place. Its Place Search 2.0 supports city, circular, and polygon search; paged responses return POI names, coordinates, addresses, administrative areas, telephone numbers, UIDs, and selected detail fields. However, a request returns at most 20 results per page and reports no more than 150 results for a query, so a national collector would require a controlled province/city and geographic-tile strategy. It cannot be a single query for “distillery in China.” [2]

For immediate lawful progress, build an **official-register and open-data candidate pipeline**. Use China’s food-production-licence system and provincial licensing authorities for producer candidates; use OSM, the eAmbrosia API, national excise registers, and business registries for Eastern Europe; then verify physical production at the site before publishing. The current dataset should continue to be treated as the public curated output, not the raw-ingestion store.

> **Decision rule:** A source that merely finds a company, brand, shop, or licensee is a **candidate source**. A record becomes a public map feature only after evidence establishes a current physical location where spirits are distilled, plus an auditable provenance record.

## 1. Current implementation constraint

The product is a static Next.js site with **no database**. `public/data/distilleries.geojson` is the current source of truth, compiled from OSM, Wikidata, Google Places, and curated records. It already supports an `entity_role` field for non-distilling locations but does not yet carry a structured product taxonomy, verification level, source ID, or harvest history. [3]

A direct raw-import-to-GeoJSON workflow would therefore make a licensing and deduplication mistake hard to undo. Separate the system into three layers:

| Layer | Location and access | Purpose | May be published? |
|---|---|---|---|
| Raw acquisition | Private files or private database | Preserve source response, source ID, query, licence, and harvest date. | Only if the source licence permits it. |
| Candidate queue | Private review dataset | Normalised records, duplicate links, verification evidence, and reviewer decision. | No. |
| Published map | `public/data/distilleries.geojson` | Curated public points that meet the inclusion rule. | Yes. |

## 2. China: viable routes

### Route A — licensed Baidu POI integration

This is the highest-potential way to locate consumer-visible Chinese distilling places, but only after a written licence. The licence request should explicitly ask whether Distillery Map may: retain POI fields; transform coordinates; deduplicate against other sources; use data to create a private candidate store; publish selected name/address/coordinate attributes in a worldwide public GeoJSON; and use the data for a commercial service. Do not assume a standard API key grants these rights. [1]

If Baidu grants the necessary permissions, use its **documented API rather than browser or app scraping**. Request a server-side access key, keep it secret, observe quota and concurrency limits, and log every request. Use `scope=2`, `city_limit=true`, page size 20, POI UID, address, administrative fields, telephone, category/tag, and the source timestamp. Because the reported total is capped at 150, divide the collection by province/city and, where necessary, smaller tiles. [2]

| Collection component | Proposed authorised design |
|---|---|
| Geography | Province → prefecture-level city → bounded tile when the query reaches the 150-result ceiling. |
| Terms to evaluate | `酒厂`; `白酒厂`; `白酒制造`; `蒸馏厂`; `酿酒厂`; `威士忌酒厂`; `白兰地厂`; `果酒厂`. |
| Required raw fields | Baidu UID, Chinese name, aliases, BD-09 coordinates, returned address, province/city/area, phone, category, query, tile, response date, API licence reference. |
| Coordinate handling | Preserve native returned coordinates privately; transform only after the licence confirms this use and document the transformation to the map’s required coordinate reference system. |
| Publication gate | Official website, licence, or direct producer evidence confirms current alcohol distillation at the physical site. A shop, distributor, operating centre, warehouse, or brewery is not enough. |

### Route B — official China producer and licence candidates

The national SAMR food-production-licence lookup states that its records originate with local licensing authorities, but warns that licence information can be incomplete or erroneous; its national interface currently says it is under construction. It is consequently a useful **verification and province-by-province discovery route**, not a complete bulk source. [4]

China’s national industrial classification provides useful search vocabulary. GB/T 4754-2017 code **1512** covers baijiu manufacture, explicitly including production through distillation and ageing; it is the highest-value initial filter for the large domestic baijiu universe. Code 1511 and “other alcohol manufacture” are broader and should enter the candidate queue only with a product or process check. [5]

| Source tier | What it can contribute | Major limitation | Correct use |
|---|---|---|---|
| SAMR national and provincial licence records | Licensed food producers and licence details. | National interface is incomplete/under construction; no established nationwide bulk export. | Seed and confirm candidates, province by province. |
| Provincial market-regulation authority notices | New, renewed, amended, and cancelled production licences. | Fragmented formats and refresh cycles. | Build a provenance-rich incremental collector or review queue. |
| Official producer websites / industry bodies | Operating evidence, address, spirit type, tours or visitor status. | Not exhaustive and often brand-led. | Final verification. |
| OSM | Openly licensed coordinates and established `craft=distillery` sites. | Materially incomplete in China. | Supplementary discovery and coordinate validation. |

### China query vocabulary

The data dictionary should retain Chinese names and aliases rather than force English transliteration. Store `name_native`, `name_latin`, `aliases`, and a confidence level. Begin with **白酒厂** (baijiu distillery/factory), **酒厂** (liquor/winery/factory—broad), **蒸馏厂** (distillery), **酿酒厂** (brewing/wine-making factory—broad), **威士忌酒厂** (whisky distillery), **白兰地厂** (brandy factory), and **果酒厂** (fruit-wine factory—often not a distillery). A process check is mandatory for the broad terms.

## 3. Eastern Europe: a registry-first network

The strongest route is not one pan-European scraper. It is a shared candidate schema fed by country-specific official sources, then harmonised and verified. OSM is valuable across every country: `craft=distillery` is specifically intended for establishments distilling alcoholic liquor, and `product=*` can record spirits made. Overpass offers a read-only query interface that can extract selected OSM data in a controlled, reproducible way. [6]

The EU eAmbrosia service is an additional shared layer. Its public API provides geographical-indication records and details; the register exposes spirit-drink names, product specifications, and recognised producer groups. It is an excellent way to find regional vocabulary, GI producer bodies, and legitimate category leads, but it is **not a census of all production sites**. [7]

| Country | Highest-value source | Access route | Initial terms | Integration role |
|---|---|---|---|---|
| Hungary | National Tax and Customs Administration (NAV) register of licensed/registered excise operators | Public CSV download; the authority says website information can be freely distributed unchanged. [8] | `pálinkafőzde`; `szeszfőzde`; `jövedéki engedélyes` | **Best first pilot**: bulk candidate source with official addresses. |
| Poland | KOWR register for manufacture/bottling of spirit drinks | Government regulatory register; verify the register export or access route before bulk use. [9] | `wyrób napojów spirytusowych`; `destylowanie`; `rektyfikowanie` | Strong licensed-producer baseline; distinguish regulated producer/bottler from small exemptions. |
| Czech Republic | ARES Administrative Register of Economic Entities | Public API with request limits; query CZ-NACE and local terminology. [10] | `pěstitelská pálenice`; `ovocný lihovar`; `výroba lihovin` | Broad business-candidate source; require secondary production-site evidence. |
| Slovakia | Financial Administration / excise and tax-warehouse records | Public lookup/list route; bulk availability needs source-by-source confirmation. | `pálenica`; `liehovar`; `pestovateľská pálenica` | High-value licence verification and physical-site evidence. |
| Bulgaria | Customs Agency public excise/warehouse registers | Public register/lookup; confirm any structured export rights. | `дестилерия`; `производство на ракия`; `специализиран малък обект за дестилация` | Strong production-site signal. |
| Serbia | Ministry list of active strong-alcohol producers | Official published list, but the accessible document is dated November 2021; obtain an updated list before treating it as current. [11] | `proizvođač jakih alkoholnih pića`; `rakija`; `voćna rakija`; `destilerija` | Historical baseline and ministry-contact lead, not a current autonomous feed. |
| Croatia | Court Register plus activity and producer verification | Public corporate search; no established public bulk activity export. | `destilerija`; `rakija`; `viljamovka`; `slivovica` | Entity and legal-address discovery; verify factory site separately. |
| Slovenia | AJPES Slovenian Business Register and agricultural-side-activity sources | Public search; verify bulk rights before automated collection. | `žganje`; `žganjekuha`; `pridelava destiliranih pijač` | Business-unit discovery; watch for small agricultural exemptions. |
| Romania | ONRC company registry and CAEN 1101 candidates | Public lookup; detailed reports can be paid/manual. | `distilerie`; `țuică`; `pălincă`; `rachiu`; `CAEN 1101` | Legal-entity discovery; require site evidence. |

## 4. Common integration and validation design

Every source should land in a private candidate table with enough provenance to reproduce or remove it. Do not merge records into public GeoJSON based on a name match alone.

| Field group | Minimum fields |
|---|---|
| Source provenance | `source_name`, `source_url`, `source_record_id`, `source_licence`, `source_retrieved_at`, `source_query_or_filter`, `source_file_hash` |
| Identity | `name_native`, `name_latin`, `aliases`, `legal_entity_name`, `registration_or_licence_number`, `website`, `telephone` |
| Place | `country`, `admin1`, `city`, `address_raw`, `address_normalised`, `postal_code`, `latitude`, `longitude`, `coordinate_reference_system` |
| Scope | `is_distilling_site`, `entity_role`, `spirit_types`, `production_evidence`, `operational_status` |
| Decision | `candidate_status`, `duplicate_of`, `verification_level`, `reviewer`, `reviewed_at`, `publish_decision` |

Use this deterministic review order:

1. **Exact source-ID deduplication:** same source and same source record ID means the same candidate.
2. **Strong entity match:** same licence number, phone, website domain, or normalised address links sources.
3. **Spatial/name candidate:** normalised names plus a small distance threshold create a review relationship, not an automatic merge.
4. **Role check:** retain distilling sites; label tasting rooms, offices, shops, and bottling plants explicitly; exclude unrelated retailers or historic sites.
5. **Evidence gate:** publish only after at least one reliable source confirms distillation at that physical address, or two complementary sources agree on identity and address.

## 5. Implementation options

No unauthorised Baidu scraping route is presented because it conflicts with Baidu’s published conditions. These are the viable routes.

| Approach | Trade-offs | Cost | Setup complexity |
|---|---|---:|---:|
| **Licensed Baidu plus official-registry pipeline** | Best potential China discovery coverage and the most complete long-term approach. Requires written Baidu permission for persistent public data use, commercial authorisation, private ingestion storage, Chinese-language review, and a controlled collector. | Licence/commercial terms unknown; additional data-operations cost. | High. |
| **Official registers, OSM, eAmbrosia, and manual verification** | Lawful and immediately startable. Strong for Hungary, Poland, and country-by-country European expansion; China grows more slowly due to fragmented licence data. Does not depend on commercial POI data. | Low direct source cost; reviewer time. | Medium. |
| **Community-led submissions with an evidence queue** | Lightest launch path. Adds local knowledge, including small fruit distillers that registers may miss, but coverage grows slowly and needs careful verification. | Low. | Low. |

## 6. Recommended next actions

The most productive immediate decision is whether to pursue the **licensed Baidu route** or begin with the **official-register/open-data route** while Baidu licensing is explored. The two can coexist, but they should not be conflated: the former requires a formal data-rights answer before engineering begins; the latter can begin with a Hungary pilot and a private candidate-review process.

A practical first tranche for the open-data route is:

| Order | Work | Success criterion |
|---:|---|---|
| 1 | Build the private candidate schema and a provenance ledger. | No raw or unverified source data reaches public GeoJSON. |
| 2 | Import Hungary’s official excise CSV as a non-public candidate batch. | Fields, licence types, and address quality are profiled; duplicates are linked to existing map records. |
| 3 | Query OSM consistently across the nine target countries and link it to the candidate batch. | Reproducible country snapshots and source IDs. |
| 4 | Add eAmbrosia vocabulary, GI records, and producer-group leads. | Local-language query dictionary and country research queue. |
| 5 | Start Poland and Czechia with their official registers/API. | Country-specific candidate batches with audit logs. |
| 6 | Decide on Baidu only after written terms/permission answer the storage-and-redistribution question. | A signed or written authorisation on file, or a documented decision not to use Baidu data. |

## References

[1]: https://lbsyun.baidu.com/index.php?title=open/law "Baidu Maps Open Platform Service Terms"  
[2]: https://lbsyun.baidu.com/docs/webapi?title=placev2/guide/webservice-placeapi/prepare "Baidu Place Search 2.0: prerequisites"; https://lbsyun.baidu.com/docs/webapi?title=placev2/guide/webservice-placeapi/district "Baidu Place Search 2.0: administrative-area API"  
[3]: https://github.com/jfrobinson76/distillery-map/blob/b265f5d/CLAUDE.md#L32-L43 "Distillery Map project scope and static GeoJSON architecture"  
[4]: https://spaqjg.e-cqs.cn/spscxk/ "SAMR Food Production Licence Enterprise Information Lookup"  
[5]: https://www.stats.gov.cn/xxgk/tjbz/gjtjbz/201710/t20171017_1758922.html "GB/T 4754-2017 National Industrial Classification"  
[6]: https://wiki.openstreetmap.org/wiki/Tag:craft%3Ddistillery "OSM craft=distillery tag"; https://wiki.openstreetmap.org/wiki/Overpass_API "Overpass API"  
[7]: https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/ "European Commission eAmbrosia register"; https://webgate.ec.europa.eu/eambrosia-api/ "eAmbrosia API"  
[8]: https://nav.gov.hu/adatbazisok/jovedekei_engedelyesek_1417768231425 "Hungary NAV licensed and registered excise operators"  
[9]: https://www.gov.pl/web/kowr/prowadzenie-rejestru-dzialalnosci-w-zakresie-wyrobu-lub-rozlewu-napojow-spirytusowych "Poland KOWR spirit-drink manufacture/bottling register"  
[10]: https://ares.gov.cz/stranky/vyvojar-info "Czech ARES developer information and public API"  
[11]: https://minpolj.gov.rs/spisak-registrovanih-aktivnih-proizvodjaca-jakih-alkoholnih-pica/ "Serbia Ministry list of active strong-alcohol producers"
