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

> **Resolved 16 August 2026.** Sections A, B and the `bismarck-brewing` row in
> section C were worked through the same day. What was decided and done is in
> **Actions taken** at the foot of this document. The lists below are left as
> they were written, as the record of what was reviewed.

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

**Files that carry the same entities.** The US enrichment set is built from the
same Google Places pull and held eight of the removed entities. It was purged to
match:

- `data/enriched/us_distilleries_seed.csv` — 1,919 → 1,911
- `data/enriched/unmatched.csv` — 597 → 590
- `data/enriched/matched_review.csv` — 140 → 139. The row was Mile Hi Distilling,
  fuzzy-matched at 80% to *Marble Distilling Company's* TTB permit CO-S-20128 —
  a bad match on a row that should not have been in the set at all
- `data/enriched/matched_high_confidence.csv` — no rows affected

Note that `/data/enriched/` is gitignored (`.gitignore:44`), so this purge is
local to the working copy and does not appear in the commit. Anyone regenerating
that set from the Google Places pull will reintroduce the eight rows unless the
seed step is filtered against `data/audit/pruned_non_distilleries.json`. Worth
wiring in — the ledger now exists for exactly that.

The three US tasting-room rows in the seed set (`village_garage_..._at_orvis`,
`village_garage_..._at_sugar_bob_s`, `mad_river_distillers_at_5th_quarter...`)
were deliberately left, matching the geojson.

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

---

## Actions taken — 16 August 2026

Everything below happened the same day as the pass above, after the review lists
were written. Feature count is unchanged at **6,131** — no row was added or
removed in this stage. Every action was checked against the producer's own
website first, and the finding is recorded whether or not it matched what the
review list assumed.

**No `slug` was changed.** Every rename below changes `name` only. Slugs are the
stable key and stay put even where the new name no longer matches the slug
(`zuisen-distillery-co-ltd-head-office` now reads "Zuisen Distillery", and so on).

### 1. Tasting rooms — section A closed

Twelve of the fourteen were marked `entity_role: "tasting_room"` in an earlier
commit. The remaining two were checked and **deliberately left unmarked**:

| Slug | Finding | Source consulted |
|---|---|---|
| `left-coast-brewing-co-tasting-room-smokehouse-distillery-irvine` | Distils on site. Location menu carries a "Craft Spirits Produced on Site" section (vodka, gin, spiced rum, malt whiskey, bourbon, blanco agave); the team page lists a Head Brewer/Distiller at Irvine; the OC Weekly piece on the opening quotes the owner on building the distillery and says the brewer would be "brewing and distilling on the new system". | leftcoastbrewing.com/location/left-coast-brewing-irvine/ · leftcoastbrewing.com/about/ · ocweekly.com/what-the-ale-left-coast-brewing-bbq-and-a-distillery/ |
| `left-coast-brewing-co-tasting-room-smokehouse-distillery-ontario` | Same "Craft Spirits Produced on Site" menu section on its own location page. | leftcoastbrewing.com/location/ontario/ |

The review list flagged these two as unresolved — "whether the 'distillery' in
the name is real was not established". It is real. Marking them `tasting_room`
would have been wrong, so the count of marked tasting rooms stays at 12, not 14.

### 2. Section B — the 16 with no parent on the map, renamed

The review list assumed all sixteen were offices or shops standing in for an
unmapped production site. **Nine of the sixteen turned out to be the producer's
actual distilling site** with a shop, tasting counter or head office attached, so
they carry no `entity_role` — only a corrected name. That is the reason the
`entity_role` is set from the website and never from the pin's name.

Every rename is `name` only. Format is `slug | old name → new name`.

**Distils at this address — renamed, no `entity_role`:**

| Slug | old name → new name | Evidence | Source consulted |
|---|---|---|---|
| `hastings-distillers-bottle-shop-and-refillery` | Hastings Distillers Bottle Shop and Refillery → **Hastings Distillers** | 231 Heretaunga St East is "an elegant 1930s tasting room and distillery space"; NZ's first certified organic artisan spirits producer, licensed there as a gin distillery. | hastingsdistillers.com · nzspiritguide.com/distilleries/hastings-distillers · hastingsdc.govt.nz alcohol licence notice |
| `boutique-distillerie-louis-couderc` | Boutique Distillerie Louis Couderc → **Distillerie Louis Couderc** | The distillery founded 1908 at 14 rue Victor Hugo, inventor of Avèze. The tourist board sells a workshop tour and tasting *at that address*. | distillerie-couderc.com · paysaurillactourisme.com |
| `distillerie-larusee-boutique` | Distillerie Larusée & Boutique → **Distillerie Larusée** | "Fenin abrite depuis 2012 la distillerie Larusée." Company is Larusée Sàrl; visits and tastings at the same address. | larusee.com |
| `berryshka-distillery-and-chocolate-manufactory-shop` | Berryshka - distillery and chocolate manufactory & shop → **Berryshka Distillery** | Obrh 17a is the *destilarna, čokoladnica, kavarna, trgovina* — production plus visitor rooms. The retail-only site is the other one, at Škrjanče, Ivančna Gorica, which is not on the map. | berryshka.com |
| `imagine-spirits-distillery-taste-shop` | IMAGINE SPIRITS distillery - TASTE&SHOP → **Imagine Spirits Distillery** | Marasi 60 is the distillery — customised handmade copper pot still, single-shot 200-bottle batches, built to eco standards, tastings on site. Listed on Tripadvisor as Imagine Spirits Distillery, Vrsar. | imagine-spirits.com · tripadvisor.com/…Imagine_Spirits_Distillery-Vrsar_Istria |
| `samai-distillery-brand-house-bar-shop` | Samai Distillery - Brand House, Bar & Shop → **Samai Distillery** | #9b Street 830 is Cambodia's first boutique rum distillery, founded 2014, distilling in the heart of Phnom Penh. The bar is the distillery's own, open Thursdays and Saturdays. | samaidistillery.com · spiritedasia.com/2024/06/visit-samai-distillery-phnom-penh/ · rumgeography.com |
| `twin-spirits-distillery-m-coffee-shop` | Twin Spirits Distillery &M Coffee Shop → **Twin Spirits Distillery** | 2931 Central Ave NE, Minneapolis — woman-founded distillery making gin, vodka, rum, whiskey and honey moonshine, with the M coffee shop inside the same building. | distillerytrail.com directory · Yelp listing |
| `the-bond-store-fine-spirits-and-liqueurs` | The Bond Store - Fine Spirits and Liqueurs → **The Bond Store** | Family-owned Kāpiti Coast distillery at Paraparaumu — matches the pin's coordinates — with its own chief distiller and distillery tours. `website` was empty and was set to `https://thebondstore.co.nz/`. | thebondstore.co.nz · nzspiritguide.com/distilleries/the-bond-store |
| `zuisen-distillery-co-ltd-head-office` | Zuisen Distillery Co., Ltd. Head Office → **Zuisen Distillery** | 瑞泉酒造株式会社, awamori since 1887. Its own Japanese sources give 首里崎山町1-35 as 本社・蒸留所 — head office *and* distillery at one address, with factory tours 9:00–17:00. Not an office pin at all. | zuisen.co.jp · zuisen.co.jp/factory · ja.wikipedia.org/wiki/瑞泉酒造 |

**Genuinely not a distilling site — renamed and given an `entity_role`:**

| Slug | old name → new name | `entity_role` | Evidence | Source consulted |
|---|---|---|---|---|
| `wyoming-whiskey-distillery-shop` | Wyoming Whiskey Distillery Shop → **Wyoming Whiskey** | `brand_shop` | The Whiskey Shop is the tasting room and gift shop on Main Street, "a few hundred yards away from the distillery building". Distillery tours have not resumed since Covid. Their own term for it is the shop, so `brand_shop`. | whiskeylore.org/distilleries/us/wyoming/wyoming-whiskey · thermopolis.com (Hot Springs County tourism) |
| `saint-bernard-distillery-alpine-spirits-store` | Saint Bernard Distillery Alpine Spirits Store → **Saint Bernard Distillery** | `brand_shop` | Località Champagne 23, Chambave is a shop the company opened — *"Apre a Chambave il nuovo negozio Saint Bernard Distillery"*. The company's own registered address is Frazione Predumaz Farcoz 31, Saint-Rhémy-en-Bosses, which is not on the map. | saintbernarddistillery.com/chi-siamo · aostasera.it |
| `hogback-distillery-office` | Hogback Distillery Office → **Hogback Distillery** | `tasting_room` | 857 Moraine Ave, Estes Park is the tasting room and bottle shop opened 2023. The distillery is in Boulder (Western Ave, near Arapahoe and 55th) and is not on the map. Their own phrase is "tasting room & bottle shop", so `tasting_room`. | hogbackdistillery.com · visitestespark.com/blog/post/estes-parks-craft-beverage-boom/ |
| `rock-and-storm-distilleries-pvt-ltd-head-office` | Rock and Storm Distilleries Pvt. Ltd. (Head Office) → **Rock and Storm Distilleries** | `head_office` | Sector 51, Chandigarh is the head office. The distilling unit is at Village Chhajli, Jhakhal-Lehragaga Road, Sunam, Sangrur, Punjab 148030, ~150 km away and not on the map. | rockandstorm.com · zaubacorp.com company record U51909PB2008PTC031788 · indiamart.com/rock-storm-distilleries |
| `west-midlands-distillery-waterfront-hq` | West Midlands Distillery Waterfront HQ → **West Midlands Distillery** | `head_office` | Their contact page lists two addresses: "Distillery HQ and Visitor Centre, Unit 22-24, Waterfront East, Brierley Hill" (the pin) and "Distillery, Unit 1, 153 Powke Lane, Rowley Regis B65 0AD" (not on the map). The stills are at the second. | westmidlandsdistillery.co.uk/contact-us |
| `allianz-distillery-limited-corporate-office` | allianz distillery limited corporate office → **Allianz Distillery** | `head_office` | An ethanol and DDGS manufacturer whose site gives only a Noida office address. Nothing on the site or elsewhere puts production in Noida. Role taken from the pin's own name; the plant location could not be established. | allianzdistillery.com |
| `rockland-distillery-bottling-plant` | Rockland Distillery Bottling Plant → **Rockland Distilleries** | `bottling_plant` | Rockland Distilleries Pvt Ltd, family distillers since 1924. **Not fully verified** — the company's own site gives only its Colombo address and says nothing about Seethawakapura. The `bottling_plant` role is carried over from the pin's own Google Places name rather than confirmed by the company, which is weaker evidence than every other row here. Worth a recheck. | rockland.lk · rockland.lk/our-story · srilankabusiness.com exporter profile |

### 3. Sliabh Liag Distillers and Ardara — one business, two real sites

The map carried `sliabh-liag-distillery` (Line Road, Carrick, F94 X9DX) and
`ardara-distillery` (Ardara, F94 EH7X), 20 km apart, both pointing at
sliabhliagdistillers.com. The question was whether that is one location
duplicated.

It is not. The company's own contact page lists both, with different roles:

- **Ardara Distillery**, The Show Field, Ardara, Co Donegal F94 EH7X — the
  distillery. Makes the Ardara and Silkie whiskeys and An Dúlamán gin, and runs
  the tours.
- **Sliabh Liag Distillers, Bottling and Administration Centre**, Line Road,
  Carrick, Co Donegal F94 X9DX — the original 2017 site, where An Dúlamán gin was
  distilled before Ardara was completed. Now bottling and administration, about
  10 full-time jobs.

Both pins stay. A tourism map should show both places. What was missing was any
way to tell they are one business, so a minimal, neutral `operator` property was
added and documented in `entity-roles.md`. **Nothing was merged and no slug was
removed.**

| Slug | Change |
|---|---|
| `ardara-distillery` | Name unchanged. `operator: "Sliabh Liag Distillers"`. `description` was empty, now "Co. Donegal — Sliabh Liag Distillers' whiskey and gin distillery, tours available". |
| `sliabh-liag-distillery` | **Renamed: Sliabh Liag Distillery → Sliabh Liag Distillers Bottling & Administration Centre.** `entity_role: "bottling_plant"`. `operator: "Sliabh Liag Distillers"`. `description` was "Co. Donegal — tours available", which was wrong on this pin (the tours are at Ardara) and is now "Co. Donegal — bottling and administration; the distillery and tours are at Ardara". |

Sources consulted: sliabhliagdistillers.com and its contact page ·
thewhiskeywash.com on the first spirit distilled at Ardara.

### 4. `bismarck-brewing` — not renamed, and why

The review list said to rename this to "Bismarck Distillery" on the basis that a
sister company distils in the same building at 1100 Canada Ave. **Checking the
distillery's own website overturned that, so the rename was not made and the row
was left exactly as it is.**

Bismarck Distillery's site gives one address and no others: "PRODUCTION FACILITY,
2730 Paintball Way, Lincoln, ND 58504 — NOT OPEN TO PUBLIC". Its 2021 grand
opening was at 1100 Canada Ave, so it has moved. Bismarck Brewing, at 1100 Canada
Ave, closed in March 2025. The pin's coordinates are 1100 Canada Ave.

So the pin is a closed brewery that never distilled, and renaming it would have
put Bismarck Distillery at an address it has left. Two defensible fixes, neither
taken here because both go beyond a rename:

1. **Move it.** Rename to "Bismarck Distillery" *and* correct the coordinates and
   address to 2730 Paintball Way, Lincoln ND. Needs a geocode — coordinates on a
   public map should not be guessed at. Note the site is closed to the public,
   which makes it a thin tourism pin.
2. **Remove it.** Under the rule at the top of this document a closed brewery
   that does not distil comes out, and the only reason it was kept was the sister
   company premise that has now failed.

Sources consulted: bismarckdistillery.com · kfyrtv.com/2025/03/14/bismarck-brewing-closes-due-industry-challenges/
· bismarcknd.gov agenda item, April 2021 · Yelp listings for both businesses.

### 5. Left over

- **`twin-spirits-distillery-m-coffee-shop` may be closed.** Renamed on the
  evidence that it is a real distillery, but Yelp shows it closed as of April
  2026 and `twinspirits.us` refused connection when checked. A closure check, not
  a naming question, so it was not acted on here.
- **Section C rows other than `bismarck-brewing`** (`boutique-ite-laster`,
  `motel-restaurant-and-distillery-sabor-de-minas`, `doc-jaks-bbq-bakery-distillery`,
  `distillery-museum`) were not revisited and stay as written.
- **Section D** — the "not checked, worth a later pass" shapes are still not
  checked.
- `data/categories/*` sidecars were again left untouched, for the reasons given
  above.
