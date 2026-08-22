# Correction: China Target Is Baijiu Producers, Not Baidu Maps

## What changes

The China gap is not principally a map-provider problem. The intended missing category is **Chinese baijiu distilling producers**: physical sites that manufacture distilled baijiu. Baidu Maps should therefore be removed from the core data-acquisition design. It may be a future licensed geocoding or discovery supplement, but it is neither the target universe nor a lawful substitute for a producer registry.

Germany illustrates the right benchmark. The live map has **694 Germany records**, composed of 364 OSM-sourced records, 305 Google Places records, 14 Wikidata records, and 11 OSM/Wikidata records. The country’s large total reflects real coverage of small fruit distillers and producer-level mapping. China has only **10 records**—eight OSM and two Google Places—and one of those two is a Yanghe operating centre rather than an identified production distillery. The China total is therefore a severe **baijiu producer coverage gap**, not evidence of few Chinese distilleries.

| Market | Published mapped records | Main source mix | Interpretation |
|---|---:|---|---|
| Germany | 694 | 364 OSM; 305 Google Places; 25 Wikidata combinations | Broad producer mapping, including fruit distillers. |
| China | 10 | 8 OSM; 2 Google Places | Not a usable baijiu producer inventory. |

## Baijiu-specific candidate universe

The primary discovery key is China’s official industrial classification **GB/T 4754-2017, code 1512 (`白酒制造`)**. Its definition covers baijiu manufacture, including the distillation and ageing process. The source model should target businesses holding a food-production licence for baijiu manufacturing, then establish the physical production address, not simply identify nationally known brands. [1]

The State Administration for Market Regulation’s food-production-licence lookup states that it receives licence information from local issuing authorities and warns that data can be incomplete or wrong. The national portal is therefore a **licence-verification and provincial discovery gateway**, not proof of a complete nationwide count. [2]

| Source layer | Use in the pipeline | What it must not be used for |
|---|---|---|
| Provincial food-production licence records | Find and confirm licensed `白酒`/`白酒制造` producers and their registered sites. | A simple national total without provincial reconciliation. |
| GB/T 4754 code 1512 | Filter business and industry sources toward baijiu manufacturing. | Confirmation that a listed company has a current distillery at a particular address. |
| Producer website, licence notice, plant-tour/visitor page | Confirm product, plant address, and current operating status. | Sole discovery source. |
| OSM `craft=distillery` plus `product=*` | Add openly licensed coordinates and discover local producers. | Complete China coverage. |
| China Alcoholic Drinks Association / regional associations | Discover members, regional clusters, and corporate names. | A census of the entire producer base. |

## Correct integration design

Maintain a private baijiu candidate ledger rather than importing a raw list into public GeoJSON. Each candidate should carry the business name in Chinese, any transliteration, the province/city, exact licence or registry reference, raw registered address, separate production-address evidence, source URL, retrieval date, and a review decision.

| Field | Reason |
|---|---|
| `name_native` and `aliases` | Chinese brands, legal entities, and factory names often differ. |
| `industry_code` | Keep `1512` or another authoritative source classification. |
| `licence_number` and `licence_issuer` | Provides reproducible provenance. |
| `registered_address` and `production_address` | Prevents headquarters, operating centres, retail outlets, and brand offices being mapped as distilleries. |
| `spirit_types` | Record `baijiu` explicitly and distinguish it from other liquor categories. |
| `is_distilling_site` | Makes the public map’s inclusion rule enforceable. |
| `verification_level` and `reviewed_at` | Allows incomplete national coverage to be reported honestly. |

A record enters the public map only when the production address is confirmed. If only the legal entity address is known, keep it in the private candidate queue; if it is known to be a head office, distributor, operating centre, or shop, label it appropriately or exclude it from the distilling-site total.

## Suggested collection order

The first pilot should be a **single province or identified baijiu production region**, using the provincial food-production licence source, regional regulator notices, and company evidence. The output should be a reviewed candidate file, a deduplication report against the current ten China records, and a small published batch of verified physical distilleries. Only after the pilot demonstrates the relevant licence fields, address quality, and false-positive rate should the same pattern expand province by province.

This avoids the central failure mode: counting brands, sales offices, historic sites, or generic liquor businesses as baijiu distilleries.

## Bottom line

The corrected objective is to bring China towards the same **producer-level coverage** that makes Germany’s fruit-distiller count credible. The appropriate foundation is **baijiu-manufacturing licence and production-site data**, reinforced by local official sources and open geospatial data—not Baidu Maps scraping.

## References

[1]: https://www.stats.gov.cn/xxgk/tjbz/gjtjbz/201710/t20171017_1758922.html "National Bureau of Statistics: GB/T 4754-2017 Industrial Classification"

[2]: https://spaqjg.e-cqs.cn/spscxk/ "SAMR Food Production Licence Enterprise Information Lookup"
