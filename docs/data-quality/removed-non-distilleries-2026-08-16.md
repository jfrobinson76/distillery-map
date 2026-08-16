# Non-distilleries removed — 16 August 2026

Second pruning pass over `public/data/distilleries.geojson`. The first pass
(12 rows, `scripts/prune_non_distilleries.py`, August 2026) took out a hiking
trailhead, an office park, an art gallery and a startup incubator. This pass
goes after the rest.

**Rule applied.** If an entry is not a distillery, it comes out. Spirit category
is never grounds for removal — a distillery that makes only gin, vodka,
schnapps, grappa or liqueur stays, because the product's remit is widening
beyond whiskey. The only question asked of each row was *does anything get
distilled here*.

**Bar for removal.** Evidence, not pattern match. Removing a real producer from
a public map is worse than leaving a bad row, so every removal below was checked
against its own website or an independent source, and the URL consulted is
recorded. Where the evidence was ambiguous the row was left in and listed in the
review section instead.

**Result.** 6,186 features → **6,131**. 55 removed, 35 flagged for review.

Machine-readable ledger: `data/audit/pruned_non_distilleries.json` (now 67 rows,
this pass appended to the first pass rather than replacing it).

---

## How the candidates were found

Not by guesswork. Four sweeps over all 6,186 features:

1. **Name markers** — brewery / brewing / Brauerei / brasserie, flat, cottage,
   apartment, holiday, guesthouse, hostel, hotel, inn, motel, museum, visitor
   centre, shop, store, boutique, bar, pub, restaurant, office, head office,
   agency, equipment, supplies, manufacturer, ruins, former, closed. 331 rows
   hit at least one.
2. **Distilling-evidence filter** — of those, the ones with no distilling token
   anywhere in name, description, website or slug. This cut 331 to a workable
   shortlist and is what stopped the brewery sweep from deleting eight real
   distillers.
3. **Booking-site domains** — `website` pointing at booking.com, bluepillow,
   despegar, vrbo, airbnb and similar. This found nine holiday rentals that no
   name pattern would have caught, including three whose names read as perfectly
   ordinary distilleries.
4. **Parent-presence check** — for every office, agency and brand shop, whether
   the producing site is separately on the map, compared by coordinates and
   address. Only rows with a mapped parent were treated as duplicate pins.

### False positives the sweep caught and did not act on

Worth recording, because each one would have been a real producer deleted from a
public map:

- **"SpA" is Società per Azioni, not a spa.** Distillerie Camel SpA (Bepi
  Tosolini), D'Auria Distillerie & Energia SpA and Distilleria Varnelli Spa are
  all working Italian distilleries.
- **"Ronera" contains "club" only via Havana Club.** Ronera San José is a rum
  distillery.
- **Eight brewery-named rows distil.** Braunstein (Denmark's first whisky
  micro-distillery), Brouwerij Wilderen (jenever, gin, whisky, rum), Bourgogne
  des Flandres (trades as *brouwerij & stokerij*, distils two beer-based
  genevers), Brauerei Gasthaus Seitz / Elch-Bräu (fruit brandies, Master-Class
  Distillery 2014), Brauerei Neunspringe (two pot stills), Tagohinke (shochu
  since 2001), TTL Puli Brewery (vacuum-distilled Ailan white spirit), Source
  Farmhouse Brewery (Colts Neck Stillhouse on the same property).
- **Depot Brewery** carries `findersdistillery.com` and is the only pin Finders
  Distillery has. Kept.
- **Hôtel de la Distillerie, Pietracorbara** looked like the same case as
  Garrigae. It is not — the property runs a working distillery and farm shop.
- **Rittmeister** and **Die Post** are German hotels with their own in-house
  Destille and Obstbrennerei respectively.
- **Warehouse Distillery**, **Bakery Hill**, **Church of Oak**, **Burnt Church**,
  **Mad Laboratory** — names only.

---

## Removed — 55 rows

### 1. Breweries with no distilling (9)

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `71-brewery` | 71 Brewery | United Kingdom | 71 Brewing, Dundee. Core range is five beers; the tour covers brewing only. No spirits or distillery mention on the site. | https://71brewing.com |
| `madrugada-brewing-company-brewpub` | Madrugada Brewing Company - Brewpub | Portugal | Brewpub in Sernancelhe with an all-beer range across its own socials and Untappd. No still referenced anywhere. | https://untappd.com/MadrugadaBrewingCompany |
| `wuri-brewery` | Wuri Brewery | Taiwan | One of TTL's three beer plants, producing roughly 25% of Taiwan Beer output. TTL's distilling sits in its separate distilleries. | https://en.wikipedia.org/wiki/Taiwan_Tobacco_and_Liquor_Corporation |
| `talisman-brewing-company` | Talisman Brewing Company | United States | Small-batch craft brewery with a beer-only taproom, Ogden UT. Visit Ogden's own brewery/distillery guide names Ogden's Own as the city's distillery, not Talisman. | https://talismanbrewingco.com/ |
| `bent-river-brewing-company` | Bent River Brewing Company | United States | 1997 craft brewery, brewpub plus a Rock Island brewery. Its only spirits connection is buying used barrels from Mississippi River Distilling. | https://www.bentriverbrewing.com/aboutus |
| `ivory-bill-brewing` | Ivory Bill Brewing | United States | Craft brewery and taproom, vintage British brewing kit and open fermentation, no still. Also now permanently closed. | https://www.theivorybill.com/ |
| `eureka-springs-brewery` | Eureka Springs Brewery | United States | Small-batch brewery; everything brewed on site is beer. | https://eurekaspringsbrewery.com/ |
| `coachella-valley-brewing-company` | Coachella Valley Brewing Company | United States | Brewery and taproom. No distilling, spirits or still anywhere on the site. | https://cvbco.com/ |
| `roughhouse-brewing` | Roughhouse Brewing | United States | Family ranch brewery making farmhouse ales, lagers and cave-aged beers in oak foeders. No distilling on site. | https://www.roughhousebrewing.com/about-us |

### 2. Holiday rentals, guesthouses and hostels (14)

Nine of these were found by their `website` field pointing at a booking site.

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `plockton-distillery-flat` | Plockton Distillery Flat | United Kingdom | Self-catering flat; website is a rental listing on isleofskyerentals.com. | bookings.isleofskyerentals.com/listings/372673 |
| `seaside-cottage-at-steinhart-distillery-with-ocean-views-cottage-1` | Seaside Cottage at Steinhart Distillery, Cottage 1 | Canada | Holiday cottage on the Steinhart property, listed as a hotel on despegar. Steinhart's distillery is mapped separately as `steinhart-s-distillary`. | us.despegar.com/hotels/h-6957653 |
| `seaside-cottage-at-steinhart-distillery-with-ocean-views-pet-friendly` | Seaside Cottage at Steinhart Distillery, Pet-friendly | Canada | Second listing for the same cottage, this one on bluepillow. | bluepillow.com/search/67a4c0a5064d51dcdc929769 |
| `grand-canyon-brewery-and-distillery-cabin-historic-tack-house` | Grand Canyon Brewery and Distillery Cabin - Historic Tack House | United States | Rental cabin. The brewery-distillery itself is mapped as `the-grand-canyon-brewing-distillery`. | us.despegar.com/hotels/h-6466937 |
| `mama-bear-s-retreat-near-water-park-distillery-great-for-families` | Mama Bear's Retreat - Near Water Park, Distillery | United States | Family holiday rental; the name describes what it is *near*. | bluepillow.com/search/65cb61293e6d928972f5906c |
| `the-distillery-at-hocking-hills-retreats` | The Distillery at Hocking Hills Retreats | United States | Named cabin in a holiday-retreat complex. Hocking Hills Moonshine is mapped separately. | bluepillow.com/search/67a4c392064d51dcdc944005 |
| `rustic-luxury-w-horses-historic-whiskey-distillery` | Rustic Luxury w/Horses - Historic Whiskey Distillery | United States | Holiday rental on a property with a historic distillery building. | us.despegar.com/hotels/h-6769338 |
| `the-little-distillery-three-bedroom-house` | The Little Distillery - Three-Bedroom House | Australia | Three-bedroom holiday house. | bluepillow.com/search/6486208e7f7e24c1923105cf |
| `distillery-4-federow-distillery` | Distillery 4 - Federow distillery | Germany | Vrbo holiday-rental listing. | vrbo.com/pdp/lo/119227421 |
| `art-douro-historic-distillery` | Art Douro - Historic Distillery | Portugal | Airbnb listing. | airbnb.com/h/art-douro |
| `palmse-distillery-guesthouse-double-room` | Palmse Distillery Guesthouse - Double Room | Estonia | A single bookable room, listed on bluepillow. | bluepillow.com/search/62deff42ba4544849389452b |
| `palmse-distillery-guesthouse-viinavabriku-kulalistemaja` | Palmse distillery guesthouse / Viinavabriku külalistemaja | Estonia | Seasonal guesthouse in the former distillery building at Palmse manor, run by Virumaa Museums. Rooms €70-95 with breakfast, open 1 May to 30 Sept. No active distilling. | virumaamuuseumid.ee/palmse-mois/majutus/viinavabriku-kulalistemaja |
| `nynas-hostel-distillery` | Nynas Hostel distillery | Sweden | STF hostel in an 1801 building that "was until the mid-19th century used as a farm distillery". Now 25 beds, shared kitchen and canoe hire. | svenskaturistforeningen.se/boende/stf-branneriet-vid-nynas-slott/ |
| `the-distillery-studio-room` | The Distillery - studio Room | New Zealand | A named guest room at Mountain Road Estate. The farm does distil, but lavender essential oil in a copper alembic, not spirits, and the pin is the accommodation. | mountainroadestate.com |

### 3. Hotel in a converted distillery (1)

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `garrigae-distillerie-de-pezenas-hotellerie-et-spa` | Garrigae Distillerie de Pézenas - Hôtellerie et Spa | France | Self-described as "a former distillery, rehabilitated into a hotel with spa, wine bar, restaurant, pool and seminar facilities". No production. | garrigae.fr/etablissements/distillerie-de-pezenas |

### 4. Restaurants and venues that do not distil (5)

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `the-distillery-restaurant-mt-hope` | The Distillery Restaurant Mt. Hope | United States | Rochester NY sports bar and grill chain — "Rochester's favorite place to eat, drink and socialize". No spirits production at any of its three sites. | https://thedistillery.com |
| `the-distillery-restaurant-henrietta` | The Distillery Restaurant Henrietta | United States | Same chain, second location. | https://thedistillery.com |
| `the-distillery-restaurant-victor` | The Distillery Restaurant Victor | United States | Same chain, third location. | https://thedistillery.com |
| `la-distillerie-restaurant-brasserie` | La Distillerie \| Restaurant Brasserie | France | Brasserie inside the Domaine de la Chartreuse hotel complex at Gosnay. A restaurant on a hotel/seminar domain, not a producer. | lachartreuse.com/en/ladistillerie/ |
| `rj-cinema-distillery-taproom` | RJ Cinema Distillery & Taproom | United States | Cinema and taproom. Its own copy puts production "in bulk at our production distillery in nearby Norwood", a different site. | ohio.org — RJ Cinema Distillery & Taproom listing |

### 5. Equipment, supplies and plant vendors (9)

They sell to distilleries. They are not distilleries. This follows the first
pass, which removed Madan Singh Anand & Sons on the same reasoning.

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `mile-hi-distilling` | Mile Hi Distilling | United States | "Your one stop shop for home distilling needs" — stills, kits, grains and parts, Wheat Ridge CO. Sells no spirits. | https://milehidistilling.com |
| `affordable-distillery-equipment-llc` | Affordable Distillery Equipment, LLC | United States | Storefront selling distillery apparatus. | shop.distillery-equipment.com |
| `5-star-brewing-distilling-supplies-qld` | 5 Star Brewing & Distilling Supplies QLD | Australia | "Suppliers of modular distilling equipment available throughout Australia", retail premises in Capalaba. | 5stardistilling.com/about-us/ |
| `moonshine-distillery-supplies` | Moonshine Distillery Supplies | South Africa | Own about page: "there were no reasonably priced distillery equipment suppliers in South Africa. This motivated us to start importing our own equipment." | moonshinesupplies.co.za/about-us/ |
| `millside-craft-distilling-supplies-online-store` | Millside Craft Distilling Supplies Online Store | South Africa | Online store in Benoni stocking stills, botanicals and fermentation gear as a KegLand distributor; premises by appointment only. | millside.co.za/shopcraftdistillingsupplies |
| `micet-distillery-equipment-manufacturer` | Micet Distillery Equipment Manufacturer | France | Sells brewhouses, fermentation tanks and turnkey distillery systems to other producers. | micetcraft.com |
| `procient-engineering-pvt-ltd-distillery-plant-manufacturers-corporate-office` | Procient Engineering Pvt. Ltd. - Distillery Plant Manufacturers | India | "One stop solution for Complete Distillery plants" — supplies fermentation, distillation and dehydration modules to plant owners. | procient.in |
| `larco-india-pvt-ltd-etp-stp-wtp-plant-manufacturer-and-supplier-in-maharashtra-cpu-for-sugar-and-distillery` | Larco India Pvt. Ltd. - ETP, STP, WTP Plant Manufacturer | India | "A distinguished leader in the field of Solid and Water Pollution Control Systems". Effluent treatment; distilleries are its clients. | larcoindia.in |
| `distiller-warehouse-ltd` | Distiller Warehouse Ltd | Canada | Water distillers and water purification — RO systems, softeners, coolers. "First company in Western Canada to offer water distillers to the public." Nothing to do with spirits. | distillerwarehouse.com |

### 6. Other businesses (1)

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `the-distillery-studio-s-modyrts-music` | The Distillery Studio's - modyrts music | South Africa | "The Distillery Recording Studio" — composes music, TV and radio ads and jingles, run after hours from 8 Sibelius Road, Walmer Heights, Port Elizabeth. | modyrts.co.za |

### 7. Historic ruin (1)

| Slug | Name | Country | Evidence | Source consulted |
|---|---|---|---|---|
| `chevalier-de-villarcon-distillery-ruins` | Chevalier de Villarçon distillery ruins | France | Listed as "Ancienne Distillerie Chevalier de Villarçon", a ruin among the sugar and rum estate remains at Sainte-Anne, Martinique. Not an operating producer. | mapcarta.com/fr/19487954 |

### 8. Second pins on a producer already mapped (15)

Administrative offices, sales agencies and off-site brand shops, each at a
different address from the working site, where the producer is separately on the
map. Removing these loses nothing. The parent slug is recorded so any one of
them can be put back.

**Offices with no parent on the map were deliberately left in** — see the review
list. Deleting those would take the producer off the map entirely, which is the
opposite of the point.

| Slug | Name | Country | Evidence | Parent still mapped |
|---|---|---|---|---|
| `o-donnell-moonshine-hq-kein-verkauf` | O'Donnell Moonshine HQ - kein Verkauf! | Germany | Brand head office at Zimmerstraße 16, Berlin-Mitte. The row's own name says "kein Verkauf". Production and bottling are at a separate Berlin-Spandau site. | `o-donnell-moonshine` (Erfurt) |
| `office-range-and-proof-house-royal-lochnagar-distillery` | Office Range and Proof House, Royal Lochnagar Distillery | United Kingdom | A Wikidata listed-building record for a building inside the distillery, not a separate site. | `royal-lochnagar-distillery` |
| `adinco-distillery-office` | Adinco Distillery Office | India | Office pin 1.8 km from the plant at Baga Cotombi, Chandor, Goa. | `adinco-distilleries` |
| `grainfuel-distilleries-private-limited-head-office` | Grainfuel Distilleries Private Limited (Head Office) | India | Corporate office, Pinnacle Business Park, Ahmedabad. The plant is at Matar, Gujarat, ~45 km away. | `grainfuel-distilleries-private-limited` |
| `rockland-distilleries-head-office` | Rockland Distilleries Head Office | Sri Lanka | Head office at Kirimandala Mawatha, Colombo. Production is at Seethawakapura. | `rockland-distillery-bottling-plant` |
| `monument-distillers-nigeria-factory-office` | Monument Distillers Nigeria (Factory office) | Nigeria | Office pin 21 km from the mapped company site, and its `website` points at kensingtondistillers.co.uk, an unrelated UK distiller. | `monument-distillers-nigeria-ltd` |
| `forgood-distillery-franchise-store` | Forgood Distillery Franchise Store | China | Franchise retail outlet. | `forgood-distillery` |
| `forgood-distillery-general-agency` | Forgood Distillery General Agency | China | Sales agency, Guangzhou. | `forgood-distillery` |
| `forgood-distillery-liyang-general-agency` | Forgood Distillery Liyang General Agency | China | Sales agency, Liyang. | `forgood-distillery` |
| `aura-distillery-shop-zagreb` | Aura Distillery Shop Zagreb | Croatia | Brand shop, Mesnička ul. 1, Zagreb — ~200 km from the producer. | `aura`, `destilerija-aura`, `aura-family-distillery` |
| `aura-distillery-shop-krk` | Aura Distillery Shop Krk | Croatia | Brand shop, Krk. | same |
| `distillery-aura-shop` | Distillery AurA Shop | Croatia | Brand shop, Rovinj. | same |
| `distilleries-et-domaines-de-provence-store-museum` | Distilleries et Domaines de Provence Store & Museum | France | Town-centre store and museum, 9 Av. Saint-Promasse, Forcalquier. Production is at Z.A. Les Chalus. | `distilleries-et-domaines-de-provence` |
| `la-boutique-by-d4f-distillerie-des-4-freres` | La BOUTIQUE BY D4F (Distillerie des 4 Frères) | France | Brand boutique, 6 Rue de la Guisane; the distillery is at 8 Rte de Briançon. | `distillerie-des-4-freres` |
| `distillerie-bonollo-shop-anagni-fr` | Distillerie Bonollo Shop - Anagni (FR) | Italy | Brand shop in Anagni, separate address from the plant. | `distillerie-bonollo-s-p-a` |

---

## Left in for review — 35 rows

None of these were removed. They are recorded so they get reviewed rather than
forgotten.

### A. Tasting rooms — a product-scope question, not a data defect (14)

The site describes itself as "a community-built dataset of distilleries,
**tasting rooms**, and spirit producers worldwide" (`CLAUDE.md`). An off-site
tasting room is therefore in scope by the product's own definition, even though
nothing is distilled there. That conflict is John's to settle, not a pruning
script's.

If the answer is "tasting rooms stay", nothing needs doing. If it is "only
distilling sites", these come out in one batch:

`village-garage-distillery-tasting-room-at-orvis` (VT, inside an Orvis store,
parent `village-garage-distillery` in Bennington) ·
`village-garage-distillery-tasting-room-at-sugar-bob-s` (VT, same parent) ·
`mad-river-distillers-at-5th-quarter-butcher-provisions` (VT, inside a butcher's,
parent `mad-river-distillers-burlington`) ·
`breckenridge-distillery-tasting-room-on-main-st` (CO) ·
`detroit-city-distillery-tasting-room` (MI, parent
`the-whiskey-factory-detroit-city-distillery`) ·
`hood-river-distillers-tasting-room` (OR, parent `hood-river-distillers-inc`) ·
`saxtons-distillery-tasting-room-and-cafe` (parent `saxtons-distillery`) ·
`speakeasy-motors-whiskey-co-tasting-room-at-liquid-mercantile-distillery` ·
`black-shire-distillery-tasting-room` · `covalent-spirits-distillery-tasting-room` ·
`bella-loma-tasting-room-and-distillery` ·
`the-distillery-infusion-room-at-kiepersol` ·
`left-coast-brewing-co-tasting-room-smokehouse-distillery-irvine` and
`-ontario` (Left Coast Brewing; whether the "distillery" in the name is real was
not established, and there is no separate Left Coast pin to fall back on).

### B. Brand shops and offices with NO parent on the map (16)

Each of these is the only pin its producer has. Removing the shop or office row
removes the producer from the map, which is a worse outcome than a slightly
wrong label. The right fix is a rename, not a delete.

`wyoming-whiskey-distillery-shop` (US) · `hastings-distillers-bottle-shop-and-refillery` (NZ) ·
`boutique-distillerie-louis-couderc` (FR) · `distillerie-larusee-boutique` (CH) ·
`berryshka-distillery-and-chocolate-manufactory-shop` (SI) ·
`imagine-spirits-distillery-taste-shop` (HR) ·
`saint-bernard-distillery-alpine-spirits-store` (IT) ·
`samai-distillery-brand-house-bar-shop` (KH) ·
`twin-spirits-distillery-m-coffee-shop` (US) ·
`the-bond-store-fine-spirits-and-liqueurs` (NZ) ·
`zuisen-distillery-co-ltd-head-office` (JP) · `hogback-distillery-office` (US) ·
`rock-and-storm-distilleries-pvt-ltd-head-office` (IN) ·
`allianz-distillery-limited-corporate-office` (IN) ·
`west-midlands-distillery-waterfront-hq` (UK) ·
`rockland-distillery-bottling-plant` (LK — bottling is not distilling, but it is
now Rockland's only pin after the head office came out).

**Verified and kept:** `st-nicolaus-distillery-shop` (SK) — the shop is at
1. mája 113, Liptovský Mikuláš, which is the production address of Slovakia's
largest spirits producer, founded 1867. `nigeria-distilleries-limited-hq` (NG) —
the HQ address on the Lagos-Abeokuta Expressway *is* the main plant.

### C. Genuinely ambiguous (5)

| Slug | Country | Why it was not removed |
|---|---|---|
| `bismarck-brewing` | United States | The named brewery closed in March 2025 and does not distil. But Bismarck Distillery, a sister company, shares the same building and tasting room at 1100 Canada Ave and makes bourbon, gin, vodka and single malt. The pin is at a real distilling address under the wrong name. Rename to "Bismarck Distillery", do not delete. |
| `boutique-ite-laster` | France | A 1938 Art Deco antiques shop in Vichy that titles itself "L'Antiquaire Distillateur" and sells own-branded Absinthe de Vichy. Could not confirm whether distilling happens at the address. |
| `motel-restaurant-and-distillery-sabor-de-minas` | Brazil | Hotel, restaurant and cachaçaria on the BR-251 outside Salinas, MG. Cachaça Sabor de Minas is genuinely distilled in Salinas in copper stills, but the alambique could not be confirmed at this roadside address. |
| `doc-jaks-bbq-bakery-distillery` | United States | Markets "award-winning craft spirits from Slidell, Louisiana" alongside BBQ sauce and a bakery line, but the site foregrounds food. Low-confidence keep. |
| `distillery-museum` (地酒博物館) | Taiwan | Instagram-only presence, no website to check. Reads as a jizake museum or shop rather than a producer, but unverifiable. |

### D. Not checked, worth a later pass

Off-site tasting rooms aside, the sweep only interrogated rows whose *name*
carried a non-distillery marker. Rows that are misclassified with a clean-looking
name would not have surfaced. Two known shapes to check next time:

- **Beer-only sites not named "brewery"** — e.g. a German *Bräu* or a Japanese
  sake house tagged into the set by OSM. The categorisation sweep's `spirits:
  ["beer"]` verdicts are the fastest handle on this.
- **Bottling plants and blenders** with no still of their own.

---

## Dataset consistency

**Files that carry the same entities.** Removed slugs were also purged from the
US enrichment set, which is built from the same Google Places pull:

- `data/enriched/us_distilleries_seed.csv` — 11 rows removed
- `data/enriched/unmatched.csv` — 10 rows removed
- `data/enriched/matched_review.csv` — 1 row removed (Mile Hi Distilling, which
  had been fuzzy-matched at 80% to *Marble Distilling Company's* TTB permit
  CO-S-20128 — a bad match on a row that should not have been in the set at all)
- `data/enriched/matched_high_confidence.csv` — no rows affected

**Files deliberately not touched.** The spirit-categorisation sidecars in
`data/categories/` still hold verdict entries for removed slugs:
`rules.json` (`71-brewery`), `out_fetch.json`, `out_p003.json`, `out_p008.json`,
`fetch_cache.json` and several `batch_*.json` inputs.

They were left alone for two reasons. They are derived working artifacts, and
`scripts/categorise_merge.py` looks verdicts up *by slug against the geojson*, so
an entry for a feature that no longer exists is never read — it is inert, not a
defect. More importantly, `data/categories/out_fetch.json` had uncommitted
changes from a parallel session at the time of this pass, and a 15-file edit
across someone else's in-flight branch is not worth the collision. **Action for
whoever lands `data/spirit-categories`:** drop these 55 slugs from the
categorisation outputs at merge.

**No hardcoded totals to update.** The homepage count is derived at runtime
(`src/lib/data.ts:19`, `data.features.length`), per the standing rule in
`CLAUDE.md`.
