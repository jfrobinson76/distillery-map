# Jamaica sweep, 30 August 2026

Bar: `inclusion-rules.md`. A pin needs a real address and either a working still or an `entity_role`.

## What the map has now

Two Jamaica pins: **Innswood Distillery** (source google-places) and **Hampden Estate** (source wikidata).

## Expected list

Jamaica has six operating rum distilleries. All six are Spirits Pool Association members and all six
wrote the Jamaica Rum GI code of practice. No seventh has been found.

- SPA members named: Appleton Estate, New Yarmouth (both J. Wray & Nephew), Long Pond, Clarendon
  (both National Rums of Jamaica), Hampden (Everglades Farms), Worthy Park.
  Proof: https://jamaica-gleaner.com/article/business/20250425/rum-fight-getting-more-spirited
- All six reported operating after Hurricane Melissa, Dec 2025. Long Pond "minor structural damage",
  New Yarmouth "resumed operations within days", Clarendon "minimal damage".
  Proof: https://jamaica-gleaner.com/article/business/20251224/rum-industry-takes-shot
- Searches for craft, gin, cane-spirit or new-entrant distilleries (2020 to 2026) returned nothing.
  The Rum Wonk distillery map and the Jamaican Rum Authority reference list the same six.
  Proof: https://www.rumwonk.com/p/jamaica-rum-distillery-map-and-notes

Five of the six are missing. Hampden is on the map.

## Missing distilleries (5) and one head office

| # | Name | Parish | Trading? | Address | Lat | Lng | Coord source | Website | Description | Operator | entity_role | Proof URL |
|---|------|--------|----------|---------|-----|-----|--------------|---------|-------------|----------|-------------|-----------|
| 1 | Appleton Estate | St Elizabeth | Yes | Appleton Estate, Nassau Valley, Siloah P.O., St Elizabeth | 18.16507 | -77.72604 | OSM node 4237499393 "Appleton Sugar and Rum Factory" | https://www.appletonestate.com/ | Jamaica's oldest working rum distillery, pot and column stills, aged rums. Tours Tue to Sat at the distillery. | J. Wray & Nephew Ltd (Campari Group) | none | https://www.appletonestate.com/en-us/visit-our-estate/ |
| 2 | Clarendon Distillers (Monymusk) | Clarendon | Yes | Monymusk, Lionel Town P.O., Clarendon | 17.80979 | -77.24948 | OSM way 746501575 "Monymusk Rum Distillery" | https://monymuskrums.com/ | Large pot and column still distillery making Monymusk rum and bulk rum for Captain Morgan. No public tours. | National Rums of Jamaica (73%) and Diageo (27%) | none | https://monymuskrums.com/contact/ |
| 3 | Long Pond Distillery | Trelawny | Yes | Long Pond, Clark's Town P.O., Trelawny | 18.42736 | -77.54720 | OSM node 3721456696 "Long Pond Sugar Factory" (industrial relation 18531318 at same spot) | https://monymuskrums.com/ | Heavy pot-still rum distillery. Distilling resumed 2019 after a 2018 fire, still on reduced capacity. No public tours. | National Rums of Jamaica | none | https://www.rumwonk.com/p/revisiting-jamaicas-long-pond-rum |
| 4 | New Yarmouth Distillery | Clarendon | Yes | New Yarmouth Estate, Hayes, Clarendon | 17.87921 | -77.27610 | OSM node 7024431643, place hamlet "New Yarmouth" (approximate, no industrial polygon mapped) | https://www.wrayandnephew.com/ | Pot and column still distillery behind Wray & Nephew White Overproof. Closed to visitors. | J. Wray & Nephew Ltd (Campari Group) | none | https://en.wikipedia.org/wiki/J._Wray_%26_Nephew_Ltd. |
| 5 | Worthy Park Estate | St Catherine | Yes | Worthy Park Estate, Factory Road, Lluidas Vale, Ewarton P.O., St Catherine | 18.14499 | -77.14674 | OSM way 308892677, industrial polygon on Factory Road, Lluidas Vale | https://worthyparkestate.com/ | Estate distillery, 100% pot still since 2005, Rum-Bar and Worthy Park brands. Tours Tue to Sat. | Worthy Park Estate Ltd | none | https://worthyparkestate.com/rum-tour/ |
| 6 | J. Wray & Nephew Ltd | Kingston | Yes | 234 Spanish Town Road, Kingston 11 | 18.00971 | -76.83992 | OSM way 264692596 "J. Wray and Nephew" (Nominatim house no. 18.01061, -76.83935) | https://www.wrayandnephew.com/ | Head office, blending and bottling plant for Wray & Nephew and Appleton. Nothing distilled here. | J. Wray & Nephew Ltd (Campari Group) | head_office | https://jis.gov.jm/pod/j-wray-nephew/ |

Rows 1 to 5: PASS with coordinates. Row 6: PASS as `head_office`.

Coordinate notes. Rows 1, 2, 3, 6 sit on named OSM features for the plant itself. Row 5 is the OSM
industrial polygon on Factory Road at Lluidas Vale, which is the Worthy Park factory site. Row 4 is the
hamlet node; the distillery is the only industrial site at New Yarmouth but OSM has no polygon for it,
so treat as accurate to a few hundred metres.

Visitor centres. The Joy Spence Appleton Estate Rum Experience, the Hampden tour and the Worthy Park
tour all run at the distillery itself. No separate pin. Neither Campari nor NRJ has a permanent
Kingston brand home (see rejected list).

## Already on map, status

- **Hampden Estate.** Keep. Wikidata Q138827507 gives 18.4401, -77.7457; OSM attraction node
  7080206220 gives 18.44008, -77.74384. They agree within 200 m. Operator is Everglades Farms Ltd
  (Hussey family). Tours Mon to Fri at the distillery. Reduced capacity after Hurricane Melissa,
  full restoration expected late Jan 2026. Proof: https://hampdenestaterum.com/hampden-estate-tours-contacts/
- **Innswood Distillery.** Remove, or retag if John wants a new role value. Not a distillery.
  NRJ's own history page: "Distilling operations at this plant ceased in 1993." Since 2000 it is an
  ageing and blending facility for Clarendon and Long Pond rum. Not open to the public.
  Proof: https://monymuskrums.com/history/ and https://www.wirspa.com/caribbean-rum-trail/national-rums-of-jamaica-monymusk-rums/
  Two more problems. The address "W.I, Innswood Dr" is Google Places junk. The pin at 17.9826, -77.0197
  reverse-geocodes to SilverSun Estates, a housing scheme west of Spanish Town, not an NRJ site.
  No `entity_role` fits (it is not a head office, shop or tasting room). Recommendation: remove.
  If kept, it needs a new role (for example `warehouse`) and a re-sourced coordinate; the OSM
  industrial polygon 579964104 at 17.98829, -76.98872 beside Innswood Estates is the likely site but
  is unverified.

## Rejected

- **Appleton Estate Rum Museum, 23 Dominica Drive, New Kingston.** Pop-up only, open May to June 2025.
  Not a permanent place. Proof: https://www.jamaicaobserver.com/2025/05/21/appleton-estate-launches-premium-rum-museum-new-kingston/
- **National Rums of Jamaica head office.** Real company, but three sources give three addresses:
  its own site says Suite 402, 218 Mountain View Ave, Kingston 10; WIRSPA says 10 Ardenne Road;
  a directory says 3 Ardenne Road. Hold until one address is confirmed. Proof: https://monymuskrums.com/contact/
- **Innswood as a distillery.** See above. Closed 1993.
- **Any seventh distillery.** None found. my-island-jamaica.com lists Innswood as an operating
  distillery; that page is wrong and was not used.

## Summary

Missing: 5 distilleries, all PASS with coordinates. One head office PASS (J. Wray & Nephew, Kingston).
One existing pin to remove or retag (Innswood). Hampden stays as is.
