# Regional-source research notes — 21 August 2026

## China

- Baidu Place Search 2.0 requires a Baidu account, developer registration, and a server-side AK. It supports city administrative-area, circle, and polygon POI search, returns up to 20 POIs per page, supports paging, and caps the `total` value at 150 for a single request. It can return POI name, location, address, province/city/area, telephone, UID, and optional detailed fields. Official sources: https://lbsyun.baidu.com/docs/webapi?title=placev2/guide/webservice-placeapi/prepare and https://lbsyun.baidu.com/docs/webapi?title=placev2/guide/webservice-placeapi/district.
- Baidu’s 5 August 2026 platform terms prohibit direct storage, caching, downloading, mirroring, or use of service-related data to create a database or derivatives without explicit written permission. Commercial use also requires an applicable paid authorisation. A public GeoJSON import therefore needs a written data licence/permission; unauthorised scraping is not a viable route. Official terms: https://lbsyun.baidu.com/index.php?title=open/law.
- The State Administration for Market Regulation (SAMR) food-production licence platform says its licence records come from local licensing authorities and can be incomplete or incorrect. The current national platform says it is under construction. It is a lawful discovery/verification layer but not yet a proven nationwide bulk feed. Official page: https://spaqjg.e-cqs.cn/spscxk/.
- National Standard GB/T 4754-2017 identifies Chinese industry code 1512 for baijiu manufacturing. Official classification: https://www.stats.gov.cn/xxgk/tjbz/gjtjbz/201710/t20171017_1758922.html.

## Eastern Europe / EU

- The OSM `craft=distillery` tag is intended for establishments distilling alcoholic liquors and can be supplemented by `product=*`. Overpass is a read-only query API suited to extracting selected OSM data. Official source: https://wiki.openstreetmap.org/wiki/Tag:craft%3Ddistillery and https://wiki.openstreetmap.org/wiki/Overpass_API.
- The European Commission’s eAmbrosia register exposes protected spirit-drink GIs, product specifications, recognised producer groups and a public API. It is a vocabulary and lead source rather than a directory of all physical production sites. Official source: https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/ and https://webgate.ec.europa.eu/eambrosia-api/.

## Baijiu correction — browser verification

The National Bureau of Statistics page confirms GB/T 4754-2017 remains marked effective. The SAMR food-production-licence portal confirms that its information comes from local issuing authorities and warns that licence information may be incomplete or erroneous. These findings support a baijiu-specific, province-by-province licensed-producer candidate strategy; they do not support claiming a complete national registry without further provincial reconciliation.
