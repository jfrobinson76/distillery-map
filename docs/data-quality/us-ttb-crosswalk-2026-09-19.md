# US crosswalk: map pins to TTB spirits permittees

Data-quality note, 19 September 2026. Scope: every pin with `country: United States`.

## The register

The United States has no national company register. The federal record that names the
business behind a distillery is the TTB's FOIA list of basic permits for distilled spirits
plants: permit number, permittee legal name (`Owner_Name`), trading name (`Operating_Name`),
premises address. Public record, updated weekly, no key, one file.

- Index: https://www.ttb.gov/public-information/foia/list-of-permittees
- File: FRL_Spirits_Producers_and_Bottlers_List.csv, fetched 2026-09-19, 5,554 permits, 756 KB
- Cached at `data/enriched/ttb_spirits_permits.csv` (gitignored; `--fetch` restores it)

A permit is permission, not a working still (see `ttb-permit-type-research-2026-08-29.md`),
so the join only ever runs pin -> permit. No permit becomes a pin.

## Method

`scripts/match_ttb_permits.py`, stdlib only. Pass 1 matches the pin name against both
permittee names inside the pin's state (token Jaccard, city agreement lifts by 0.1). Pass 2,
for pins pass 1 could not place, matches the premises: same ZIP, same street number, street
tokens overlap. Pass 2 is what catches a permit held under a holding company or a brewery
that also distils. `build_company_crosswalk.py` folds `high` and `medium` rows into the
crosswalk; `low` rows stay in `ttb-candidates.csv` as leads.

## Result

| | Pins |
|---|---|
| US pins after the country fix | 1730 |
| Matched, name, high | 1093 |
| Matched, name, medium | 249 |
| Matched, premises (medium) | 153 |
| Leads, low (not in crosswalk) | 45 |
| Unmatched | 190 |

Relation: 1101 `self`, 439 `operator` (the permit is held under a name the pin does not carry).
38 permits are matched by more than one pin (a brand pin and its distillery, or two pins for one site); those are candidates for a merge, listed by the crosswalk itself.

Thirty pins carried the wrong country before this pass: 29 with Canadian addresses filed under United States, one (Port Chilkoot, AK) filed under Canada. Fixed in the geojson by address suffix in the same PR.

## What a permit row does and does not give

Gives: the legal entity, the premises, and a weekly presence signal (a permit that leaves the
list has been surrendered or revoked; keeping weekly snapshots turns that into a health
signal). Does not give: state incorporation number, status, filings, officers. Those live in
50 state registers. The second layer, not attempted here: which states publish free bulk or
API data must be checked state by state before anyone builds on it; do not assume.

## Unmatched pins by state

no address 47, PA 19, CA 10, NY 10, TX 9, KY 7, IN 6, CO 6, OR 6, MO 6, NM 5, WI 4, VT 4, WA 4, NC 3, NJ 3, MI 3, FL 3, AL 3, AZ 3, OH 3, GA 2, MT 2, AR 2, MS 2, SC 2, TN 2, MD 2, MN 2, ME 1, CT 1, LA 1, VA 1, KS 1, IL 1, RI 1, IA 1, NH 1, ID 1

Reasons seen in samples: no address on the pin (47), the pin is a bar or shop named 'Distillery', a brand pin at a visitor site with no plant, a permit held under a name and address neither pass can reach, or a plant that has closed.

## Unmatched slugs

- `1205-distillery` 1205 Distillery (120 Camilla Ct Suite A, Westfield, IN 46074, USA)
- `1879-distilling-company` 1879 Distilling Company (12239 Manchester Rd, Des Peres, MO 63131, USA)
- `1911-established-distillery` 1911 Established Distillery (4473 Cherry Valley Turnpike, Nedrow, NY 13120, USA)
- `all-points-west` All points West (73 Tichenor St, Newark, NJ 07105, USA)
- `american-distilling` American Distilling (31 E High St, East Hampton, CT 06424, USA)
- `american-reserve-distillers` American Reserve Distillers (9721 Artesia Blvd, Bellflower, CA 90706, USA)
- `angel-s-envy-distillery` Angel's Envy Distillery (no address)
- `anvil-distillery` Anvil Distillery (no address)
- `asw-distillery-at-the-battery-atlanta-home-of-fiddler-bourbon-hunker-vodka-more` ASW Distillery at The Battery Atlanta, home of Fiddler Bourbon, Hunker Vodka & more (900 Battery Ave SE Suite 1035, Atlanta, GA 30339, USA)
- `backdrop-distilling` BackDrop Distilling (70 SW Century Dr #100, Bend, OR 97702, USA)
- `backroads-distilling-company-the-stillhouse` Backroads Distilling Company; The Stillhouse (0185 W County Rd 68, Laotto, IN 46763, USA)
- `bahamas-distilling-co` Bahamas Distilling Co. (G7PV+FRW, 7 Oak St, Freeport, The Bahamas)
- `balcones-distilling` Balcones Distilling (no address)
- `barrel-head-distillery` Barrel Head Distillery (5317 Lomas Dr, Carlsbad, NM 88220, USA)
- `beach-time-distilling` Beach Time Distilling (no address)
- `bee-boyzz-honey` Bee Boyzz Honey (no address)
- `bluegrass-distillers-at-elkwood-farm` Bluegrass Distillers at Elkwood Farm (158 W Leestown Rd, Midway, KY 40347, USA)
- `bottom-of-the-barrel-winery-and-tc-distillery` Bottom of the Barrel Winery and TC Distillery (606 Main St, Tell City, IN 47586, USA)
- `bowens-whiskey` Bowen’s Whiskey (no address)
- `breckenridge-distillery-tasting-room-on-main-st` Breckenridge Distillery: Tasting Room on Main St. (137 S Main St suite a, Breckenridge, CO 80424, USA)
- `brewing-distilling-center` Brewing & Distilling Center (130 Bearden Pl, Knoxville, TN 37917, USA)
- `bud-light` Bud Light (no address)
- `bulleit-distilling-co` Bulleit Distilling Co. (no address)
- `bulleit-frontier-whiskey` Bulleit Frontier Whiskey (no address)
- `calistoga-depot-distillery` Calistoga Depot Distillery (1458 Lincoln Ave, Calistoga, CA 94515, USA)
- `can-bar-w-agrodolce-distilling-co` Can Bar w/ Agrodolce Distilling Co. (2225 E Burnside St, Portland, OR 97214, USA)
- `cathedral-of-rum` Cathedral of Rum (PR-165 KM 6.2, Cataño, 00949, Puerto Rico)
- `chattanooga-whiskey-riverfront-distillery` Chattanooga Whiskey Riverfront Distillery (765 W M.L.K. Blvd, Chattanooga, TN 37402, USA)
- `chef-life-brewery-distillery` Chef Life Brewery & Distillery (711 Thimble Shoals Blvd, Newport News, VA 23606, USA)
- `chicken-hill-distillery-at-gettysburg` Chicken Hill Distillery at Gettysburg (1863 Gettysburg Village Dr Suite 520, Gettysburg, PA 17325, USA)
- `chicken-hill-distillery-cook-forest` Chicken Hill Distillery Cook Forest (26 Great Bear Ln, Clarington, PA 15828, USA)
- `chicken-hill-distillery-lancaster-county-pa` Chicken Hill Distillery - Lancaster County PA (801 Stanley K Tanger Dr, Lancaster, PA 17602, USA)
- `citrus-distillers` Citrus Distillers (2222 Harper St, Jacksonville, FL 32204, USA)
- `codys-roadhouse-distillery` Cody’s Roadhouse Distillery (5605 Bensalem Blvd, Bensalem, PA 19020, USA)
- `colorado-mountain-distillers` Colorado Mountain Distillers (611 Canon St, Guffey, CO 80820, USA)
- `cooperstown-distillery-beverage-exchange` Cooperstown Distillery Beverage Exchange (73 Main St, Cooperstown, NY 13326, USA)
- `cooperstown-distillery-beverage-exchange-at-saratoga` Cooperstown Distillery Beverage Exchange at Saratoga (453 Broadway, Saratoga Springs, NY 12866, USA)
- `copper-moonshine-stills` Copper Moonshine Stills (2808 Coral Cir, Alma, AR 72921, USA)
- `country-hammer-moonshine` Country Hammer Moonshine (5846 Library Rd, Bethel Park, PA 15102, USA)
- `craft-distillers` Craft Distillers (108 W Clay St, Ukiah, CA 95482, USA)
- `crawford-distillery` Crawford Distillery (5 1st St W, Havre, MT 59501, USA)
- `creative-distillery` Creative Distillery (Ecoshed, 133 Commerce Park Dr #15, Jackson, MS 39213, USA)
- `cussewago-creek-distillery` Cussewago Creek Distillery (231 Chestnut St Ste 101, Meadville, PA 16335, USA)
- `dark-door-spirits` Dark Door Spirits (no address)
- `deep-eddy-distillery` Deep Eddy Distillery (2250 US-290, Dripping Springs, TX 78620, USA)
- `dells-distillery` Dells Distillery (206 Broadway, Wisconsin Dells, WI 53965, USA)
- `design-distillery` Design Distillery (1414 Key Hwy, Baltimore, MD 21230, USA)
- `distillerie-du-saint-laurent` Distillerie du Saint-Laurent (no address)
- `distillerie-fils-du-roy-quebec` Distillerie Fils du Roy Québec (no address)
- `distillers-technology-council` Distillers Technology Council (1190 9th Ave, Marion, IA 52302, USA)
- `distillery-244-old-town` Distillery 244 Old Town (244 N Mosley St, Wichita, KS 67202, USA)
- `distillery-pub-llc` Distillery Pub LLC (515 N Main St, Oshkosh, WI 54901, USA)
- `distillery-united-states` Distillery (301 Arizona Ave #250, Santa Monica, CA 90401, USA)
- `doc-howards-distillery` Doc Howard’s Distillery (3645 Ln Rd Ext STE 203, Perry, OH 44081, USA)
- `doc-jaks-bbq-bakery-distillery` Doc Jaks BBQ Bakery Distillery (Beth Dr, Slidell, LA 70458, USA)
- `doc-water-s-cidery` Doc Water's Cidery (no address)
- `donut-distillery` Donut Distillery (1107 E Jackson Ave, Oxford, MS 38655, USA)
- `dusty-road-distillery` Dusty Road Distillery (396 Davis School Rd, Carter, MT 59420, USA)
- `entrance-kiepersol-winery-distillery-restaurant-and-vineyard` Entrance - Kiepersol Winery, Distillery, Restaurant, and Vineyard (4120 Farm to Market 344 E, Tyler, TX 75703, USA)
- `etta-place-cider` Etta Place Cider (no address)
- `fabrika-kachka-distillery-zakuski-bar` Fabrika: Kachka Distillery & Zakuski Bar (Bindery Annex, 2117 NE Oregon St Suite 202, Portland, OR 97232, USA)
- `family-traditions-distillery-the-shine-shack` Family Traditions Distillery - The Shine Shack (476 Hugart St, Confluence, PA 15424, USA)
- `fernoz-distillery` Fernoz Distillery (900 S Preston Rd Ste 50, Prosper, TX 75078, USA)
- `flanigan-s-texas-wine-spirits-distillery` Flanigan's Texas Wine & Spirits Distillery (330 N Lampasas St, Bertram, TX 78605, USA)
- `four-roses-cox-s-creek-distillery` Four Roses Cox's Creek Distillery (no address)
- `foxtrail-distillery` Foxtrail Distillery (2225 S Bellview Rd Suite 101, Rogers, AR 72758, USA)
- `george-washington-s-distillery` George Washington's Distillery (no address)
- `gibson-distillery` Gibson Distillery (115 W Church St, Headland, AL 36345, USA)
- `gold-river-distillery` Gold River Distillery (no address)
- `green-bay-distillery` Green Bay Distillery (835 Mike McCarthy Way, Ashwaubenon, WI 54304, USA)
- `green-river-distilling-co` Green River Distilling Co. (10 Distillery Rd, Owensboro, KY 42301, USA)
- `greenport-distilling-one-woman-winery` Greenport Distilling @ One Woman Winery (5195 Old North Rd, Southold, NY 11971, USA)
- `haliimaile-distillery` Haliimaile Distillery (no address)
- `hercynian-distilling-co` Hercynian Distilling Co. (Elsbach 11A, 37449 Walkenried, Germany)
- `herman-buttner-distillery` Herman Buttner Distillery (2147 Bethabara Rd, Winston-Salem, NC 27106, USA)
- `holladay-distillery` Holladay Distillery (1 Mc Cormick Ln, Weston, MO 64098, USA)
- `honeoye-falls-distillery` Honeoye Falls Distillery (no address)
- `hudson-whiskey-tuthilltown` Hudson Whiskey (Tuthilltown) (no address)
- `idol-ridge-winery-alder-creek-distillery` Idol Ridge Winery & Alder Creek Distillery (9059 NY-414, Lodi, NY 14860, USA)
- `islamorada-brewery-distillery-fort-pierce` Islamorada Brewery & Distillery (Fort Pierce) (3200 St Lucie Blvd, Fort Pierce, FL 34946, USA)
- `jackazz-distilling-llc-millersburg` Jackazz Distilling, LLC.- Millersburg (311 Union St, Millersburg, PA 17061, USA)
- `jaxon-keys-winery-distillery` Jaxon Keys Winery & Distillery (10400 US-101, Hopland, CA 95449, USA)
- `jimmy-juice-distillery` Jimmy Juice - Distillery (58 S Duke St, Millersville, PA 17551, USA)
- `jones-von-drehle-vineyards` Jones von Drehle Vineyards (no address)
- `just-rum` Just Rum (17020 Ruben Ln, Sandy, OR 97055, USA)
- `kentucky-mist-distillery-orange-beach` Kentucky Mist Distillery Orange Beach (4790 Main St Suite F109, Orange Beach, AL 36561, USA)
- `la-barik` La Barik (no address)
- `la-chaufferie` La Chaufferie (no address)
- `lakeward-spirits-craft-distillery` Lakeward Spirits Craft Distillery (no address)
- `lawrenceburg-distillers-indiana` Lawrenceburg Distillers Indiana (652 Shipping St, Lawrenceburg, IN 47025, USA)
- `lazy-river-farm-distillery` LAZY RIVER FARM & Distillery (27010 78th Ave S, Kent, WA 98032, USA)
- `liquor-wine-moonshine` Liquor Wine & Moonshine (904 State Fair Blvd, Syracuse, NY 13209, USA)
- `little-water-distillery` Little Water Distillery (810 Lexington Ave. (entrance location, mailing address, 807 Baltic Ave unit b, Atlantic City, NJ 08401, USA)
- `mad-river-distillers-at-5th-quarter-butcher-provisions` Mad River Distillers at 5th Quarter Butcher & Provisions (89 Mad River Green, Waitsfield, VT 05673, USA)
- `maine-distilleries-cold-river-vodka` Maine Distilleries - Cold River Vodka (437 US-1, Freeport, ME 04032, USA)
- `mammoth-distilling-cocktail-lounge` Mammoth Distilling Cocktail Lounge (108 E Maumee St, Adrian, MI 49221, USA)
- `manitou-and-co-distilling` Manitou and Co Distilling (203 W River St, Leland, MI 49654, USA)
- `mb-roland-distillery-cave-du-bourbon` MB Roland Distillery-Cave Du Bourbon (109 Broadway St, Cave City, KY 42127, USA)
- `midstate-distillery-at-hershey-fresh-market` Midstate Distillery at Hershey Fresh Market (121 Towne Square Dr Suite 102, Kiosk 17, Hershey, PA 17033, USA)
- `mill-street-grains-gatherings-event-venue-and-distillery` Mill Street Grains & Gatherings Event Venue and Distillery (20 Mill St, Utica, OH 43080, USA)
- `mockingbird-distillery-smokehouse` Mockingbird Distillery & Smokehouse (2800 N Terminal Rd, Houston, TX 77032, USA)
- `montezuma-winery-hidden-marsh-distillery` Montezuma Winery & Hidden Marsh Distillery (2981 US-20, Seneca Falls, NY 13148, USA)
- `moonshine-distiller` Moonshine Distiller (78737 US-40 #1100, Winter Park, CO 80482, USA)
- `moonshine-drinkery` Moonshine Drinkery (103 W Santa Rosa St, Victoria, TX 77901, USA)
- `moss-beach-distillery` Moss Beach Distillery (140 Beach Way, Moss Beach, CA 94038, USA)
- `mount-rose-distillery` Mount Rose Distillery (no address)
- `mushroom-spirits-distillery-cayuga-lake` Mushroom Spirits Distillery Cayuga Lake (4055 NY-89, Seneca Falls, NY 13148, USA)
- `new-richmond-distilleries` New Richmond Distilleries (no address)
- `nippitaty-distillery` Nippitaty Distillery (1734 Signal Point Rd, Charleston, SC 29412, USA)
- `nomad-distilling-co-jim-thorpe` Nomad Distilling Co - Jim Thorpe (55 Broadway, Jim Thorpe, PA 18229, USA)
- `nomad-distilling-co-new-hope` Nomad Distilling Co. - New Hope (20 S Main St, New Hope, PA 18938, USA)
- `norden-distilling` Norden Distilling (2416 E Coon Lake Trail, Howell, MI 48843, USA)
- `oak-and-maple-whisky-and-waffle-co` Oak and Maple (Whisky and Waffle Co.) (123 E 5th St, Loveland, CO 80537, USA)
- `of-the-earth-farm-distillery` Of The Earth Farm Distillery (17190 MO-13, Richmond, MO 64085, USA)
- `ogle-brewery-arch-ray-winery-paul-bee-distillery-at-arch-ray-resort` Ogle Brewery, Arch Ray Winery, & Paul Bee Distillery at Arch Ray Resort (4160 US-290, Fredericksburg, TX 78624, USA)
- `old-herald-brewery-distillery` Old Herald Brewery & Distillery (115 E Clay St, Collinsville, IL 62234, USA)
- `oligan-distilling` Oligan Distilling (no address)
- `olympic-distillers` Olympic Distillers (356 Freshwater Bay Rd, Port Angeles, WA 98363, USA)
- `omega-gin-company` Omega Gin Company (no address)
- `orange-county-distillery-at-brown-barn-farms` Orange County Distillery at Brown Barn Farms (286 Maple Ave, New Hampton, NY 10958, USA)
- `ostrich-egg-distillery` Ostrich Egg Distillery (129 W Commonwealth Ave, Fullerton, CA 92832, USA)
- `ozan-winery-yh-distillery` Ozan Winery & YH Distillery (173 Co Rd 301, Calera, AL 35040, USA)
- `palmer-distilling-co` Palmer Distilling Co (220 Krams Ave, Philadelphia, PA 19127, USA)
- `pathfinder-farm-distillery-tasting-room-and-cocktail-bar` Pathfinder Farm Distillery Tasting Room and Cocktail Bar (14 S Main St, Boonsboro, MD 21713, USA)
- `prohibition-spirits-distillery` Prohibition Spirits Distillery (452 1st St E STE E, Sonoma, CA 95476, USA)
- `purple-toad-winery-and-distillery-bowling-green` Purple Toad Winery and Distillery Bowling Green (6245 Cemetery Rd, Bowling Green, KY 42103, USA)
- `raff-distilerie` Raff Distilerie (no address)
- `ransom-wine-co-distillery-production-facility` Ransom Wine Co. & Distillery Production Facility (23101 SW Houser Rd, Sheridan, OR 97378, USA)
- `rd1-spirits-distillery` RD1 Spirits Distillery (113 Turner Cmns Wy Suite 110, Lexington, KY 40508, USA)
- `red-locks-irish-whiskey` Red Locks Irish Whiskey (no address)
- `rhodium-room-distillery-bar-ri-spirits` Rhodium Room Distillery Bar @ RI Spirits (40 Bayley St, Pawtucket, RI 02860, USA)
- `richmand-rum` Richmand Rum (1406 Newcastle St, Brunswick, GA 31520, USA)
- `riverhead-ciderhouse` Riverhead Ciderhouse (no address)
- `rocheport-distilling-co` Rocheport Distilling Co. (12847 W Hwy Bb, Rocheport, MO 65279, USA)
- `route-40-distilling-co` Route 40 Distilling Co. (no address)
- `saxtons-distillery-tasting-room-and-cafe` Saxtons Distillery Tasting Room and Cafe (485 W River Rd, Brattleboro, VT 05301, USA)
- `scallywag-distilling` Scallywag Distilling (1474 PA-208, Pulaski, PA 16143, USA)
- `seven-troughs-distilling-co` Seven Troughs Distilling Co. (no address)
- `shelter-distilling-montrose-regional-airport` Shelter Distilling - Montrose Regional Airport (2100 Airport Rd, Montrose, CO 81401, USA)
- `skunk-hollow-distillery` Skunk Hollow Distillery (1642 Mt Cobb Rd, Jefferson Township, PA 18436, USA)
- `smith-creek-moonshine-tanger-outlets` Smith Creek Moonshine Tanger Outlets (300 Tanger Blvd #232, Branson, MO 65616, USA)
- `sonora-moonshine-company` Sonora Moonshine Company (124 E Broadway Blvd, Tucson, AZ 85701, USA)
- `sorrenti-family-estate-winery-distillery-pizzeria` Sorrenti Family Estate Winery, Distillery & Pizzeria (130 Lower Cherry Valley Rd, Saylorsburg, PA 18353, USA)
- `source-farmhouse-brewery` Source Farmhouse Brewery (NJ-34, Colts Neck, NJ 07722, USA)
- `south-texas-distillery-home-of-wild-rag-vodka` South Texas Distillery Home of Wild Rag Vodka (642 FM1540, Sandia, TX 78383, USA)
- `stillwagon-distillery-florence-oregon` Stillwagon Distillery Florence Oregon (1341 Bay St, Florence, OR 97439, USA)
- `stranahan-s-colorado-whiskey` Stranahan's Colorado Whiskey (no address)
- `studio-distilling` Studio Distilling (2380 Wycliff St #140, St Paul, MN 55114, USA)
- `suti-craft-distillery` SuTi Craft Distillery (528 W Kennedale Pkwy, Kennedale, TX 76060, USA)
- `takara-sake` Takara Sake (708 Addison St, Berkeley, CA 94710, USA)
- `taos-distillery` Taos Distillery (519 La Lomita Rd, Taos, NM 87571, USA)
- `the-audio-distillery` The Audio Distillery (936 N Batavia St, Orange, CA 92867, USA)
- `the-brow-distillery` The Brow Distillery (204 Crystal Grove Blvd, Lutz, FL 33548, USA)
- `the-conjure-bar-stage-at-inspired-by-spirits-distillery` The Conjure Bar & Stage (at Inspired by Spirits Distillery) (Inside the Inspired by Spirits Distillery, 753 E Warrington Ave, Pittsburgh, PA 15210, USA)
- `the-distillery-1812` The Distillery 1812 (1812 Bourbon St, Ashville, OH 43103, USA)
- `the-distillery-network-inc` The Distillery Network Inc (50 Bridge St, Nashua, NH 03060, USA)
- `the-distillery-united-states` The Distillery (101 Rand Mill Rd, Garner, NC 27529, USA)
- `the-hair-distillery` The Hair Distillery (621 E Lasalle Ave, South Bend, IN 46617, USA)
- `the-ingram-distillery` The Ingram Distillery (11217 KY-58, Columbus, KY 42032, USA)
- `the-lounge-at-taos-ski-valley-by-rolling-still-distillery` The Lounge at Taos Ski Valley by Rolling Still Distillery (200 Thunderbird Rd Unit 103B, Taos Ski Valley, NM 87525, USA)
- `the-perfect-gift-with-algodones-distillery` The Perfect Gift with Algodones Distillery (2501 Sudderth Dr Suite G, Ruidoso, NM 88345, USA)
- `the-reserve` The Reserve (400 Linden St, Fort Collins, CO 80524, USA)
- `the-skin-distillery` The Skin Distillery (4122 W Innovative Dr Ste 101, Anthem, AZ 85086, USA)
- `the-skyn-distillery` The Skyn Distillery (18283 Minnetonka Blvd Suite D, Wayzata, MN 55391, USA)
- `the-smoothie-distillery` The Smoothie Distillery (202 S 3rd St, Hamburg, PA 19526, USA)
- `the-water-distillery` The Water Distillery (25001 214th Pl SE, Maple Valley, WA 98038, USA)
- `thrasher-s-rum` Thrasher's Rum (no address)
- `tombstone-distillery` Tombstone Distillery (325 E Allen St, Tombstone, AZ 85638, USA)
- `tommy-rotter-distellery` Tommy Rotter Distellery (no address)
- `topo-distillery` TOPO Distillery (no address)
- `town-branch-distillery` Town Branch Distillery (no address)
- `travelers-point-distillery` Travelers Point Distillery (400 E Madison St, Kirklin, IN 46050, USA)
- `travis-hasse-distilling-co` Travis Hasse Distilling Co. (7071 Kickaboo Rd, Waunakee, WI 53597, USA)
- `tumbleroot-brewery-and-distillery-alegria-on-agua-fria` Tumbleroot Brewery and Distillery - Alegría on Agua Fria (2791 Agua Fria St, Santa Fe, NM 87507, USA)
- `ty-iechyd-da-distillery` Ty Iechyd Da Distillery (507 W Walnut St, Springfield, MO 65806, USA)
- `uncle-boojie-s-distilling-company` Uncle Boojie's Distilling Company (700 Vine St, Louisville, KY 40204, USA)
- `uncle-jumbo-s-distillery-inc` Uncle Jumbo's Distillery, Inc (8510 Roll Road 470 Elmwood Avenue, Buffalo, NY 14221, 8510 Roll Rd, Clarence Center, NY 14032, USA)
- `unicorn-distillery` Unicorn Distillery (920 S Holgate St UNIT 108, Seattle, WA 98134, USA)
- `upstate-distilling` Upstate Distilling (no address)
- `urbana-hill-distilling` Urbana Hill Distilling (no address)
- `vicario-micro-distillery-and-farm` VICARIO Micro-Distillery and Farm (840 State Rd S-42-653, Greer, SC 29651, USA)
- `village-garage-distillery-tasting-room-at-orvis` Village Garage Distillery Tasting Room at Orvis (4180 Main St, Manchester Center, VT 05255, USA)
- `village-garage-distillery-tasting-room-at-sugar-bob-s` Village Garage Distillery Tasting Room at Sugar Bob's (92 VT-11, Chester, VT 05143, USA)
- `white-tiger-distillery` White Tiger Distillery (no address)
- `whitefish-handcrafted-spirits` Whitefish Handcrafted Spirits (no address)
- `wild-roots-x-wyld-cbd` Wild Roots x Wyld CBD (no address)
- `yardley-distillery-production-site` Yardley Distillery Production Site (no address)
- `yardley-distillery-tex-mex-restaurant` Yardley Distillery Tex-Mex Restaurant (897 W Trenton Ave, Morrisville, PA 19067, USA)
- `young-hearts-distilling-restaurant-and-bar` Young Hearts Distilling, Restaurant and Bar (228 Fayetteville St Ste 201, Raleigh, NC 27601, USA)
- `young-living-st-maries-farm-distillery` Young Living St. Maries Farm & Distillery (701 N Fork Coon Creek Rd, Plummer, ID 83851, USA)

## Low leads (in `ttb-candidates.csv`, not in the crosswalk)

- `alaskan-spirts-distillery` Alaskan Spirts Distillery -> AK-S-20016 ALASKAN BREWING, LLC; jaccard 0.50 via operating; premises Juneau, AK; dba Alaskan Distilling Co.; pin has no address, matched nationwide
- `american-freedom-distillery` American Freedom Distillery -> FL-S-20084 AMERICAN CRAFT DISTILLERY CORPORATION; jaccard 0.50 via owner; premises Deland, FL
- `artisan-grain-distillery` Artisan Grain Distillery -> IA-S-1 GRAIN PROCESSING CORPORATION; jaccard 0.50 via owner; premises Muscatine, IA
- `aspen-sky-winery-distillery-event-center` Aspen Sky - Winery, Distillery & Event Center -> WI-S-20085 ASPEN SKY LLC; jaccard 0.50 via operating; premises Slinger, WI; dba Aspen Sky
- `astraluna-brands` AstraLuna Brands -> MA-S-20011 ASTRALUNA, LLC; jaccard 0.50 via owner; premises Medfield, MA; pin has no address, matched nationwide
- `barley-and-boar-restaurant-brewhouse-distillery` Barley and Boar - Restaurant • Brewhouse • Distillery -> CA-S-20453 BU BREWING LLC; jaccard 0.50 via operating; premises Atascadero, CA; dba Barley and Boar Kitchen and Distillery
- `bens-den-at-gulf-coast-distillers` Ben’s Den at Gulf Coast Distillers -> TX-S-20046 BUFFALO BAYOU DISTILLERIES, LLC; jaccard 0.50 via operating; premises Houston, TX; dba Gulf Coast Distillers
- `bismarck-brewing` Bismarck Brewing -> ND-S-20008 BISMARCK DISTILLERY LLC; jaccard 0.50 via operating; premises Lincoln, ND; dba Bismarck Distillery; pin has no address, matched nationwide
- `bomberger-s-distillery` Bomberger's Distillery -> WI-S-20058 S&S DISTILLING CO.; jaccard 0.50 via owner; premises Menasha, WI; dba Tight Barrel Distillery; pin has no address, matched nationwide
- `brain-brew-distillery` Brain Brew Distillery -> OH-S-20073 BRAIN BREW VENTURES 3.0, INC.; jaccard 0.50 via owner; premises Newtown, OH
- `carmichael-brother-s-distillery` Carmichael Brother's Distillery -> TN-S-20151 BROTHER'S BOND DISTILLING COMPANY, LLC; jaccard 0.50 via owner; premises Columbia, TN; pin has no address, matched nationwide
- `claremont-distillery` Claremont Distillery -> NJ-S-20007 CLAREMONT DISTILLED SPIRITS INC; jaccard 0.50 via owner; premises Hamburg, NJ
- `deep-roots-distillery-brimfield` Deep Roots Distillery Brimfield -> MA-S-20057 DEEP ROOTS DISTILLERY USA, LLC; jaccard 0.50 via operating; premises Fiskdale, MA; dba Deep Roots Distillery USA
- `duck-creek-winery-denmark-distilling-new-denmark-brewing-company` Duck Creek Winery/ Denmark Distilling/ New Denmark Brewing Company -> WI-S-20037 DUCK CREEK VINEYARD AND WINERY LLC; jaccard 0.53 via owner; premises Denmark, WI; dba Denmark Distilling
- `five-points-distilling-lone-elm-whiskey` Five Points Distilling / Lone Elm Whiskey -> TX-S-20006 FIVE POINTS DISTILLING, LLC.; jaccard 0.50 via operating; premises Forney, TX; dba Five Points Distilling
- `flatrock-distillery-bistro` Flatrock Distillery & Bistro -> OH-S-20029 FLATROCK BREWING COMPANY; jaccard 0.50 via operating; premises Toledo, OH; dba Flatrock Distilling Company
- `flying-leap-vineyards-distillery-winery-estate-elgin-az` Flying Leap Vineyards & Distillery (Winery Estate - Elgin, AZ) -> AZ-S-20011 FLYING LEAP VINEYARDS, INC.; jaccard 0.53 via owner; premises Elgin, AZ; dba Flying Leap Distillery
- `four-daughters-vineyard-winery-loon-juice-hard-cider-and-the-traditionalist-bourbon-distillery` Four Daughters Vineyard & Winery, Loon Juice Hard Cider, and The Traditionalist Bourbon Distillery -> MN-S-20053 FOUR DAUGHTERS VINEYARD AND WINERY LLC; jaccard 0.50 via operating; premises Spring Valley, MN; dba FOUR DAUGHTERS VINEYARD & WINERY
- `killdeer-distilling-newport` Killdeer Distilling Newport -> OR-S-20062 FIRST WATER SPIRITS LLC; jaccard 0.50 via operating; premises Newberg, OR; dba KILLDEER DISTILLING
- `little-toad-creek-brewery-distillery-las-cruces` Little Toad Creek Brewery & Distillery Las Cruces -> NM-S-20001 LITTLE TOAD CREEK LLC; jaccard 0.50 via operating; premises Silver City, NM; dba Little Toad Creek Distillery
- `local-cider` Local Cider -> CO-S-20001 LOCAL DISTILLING INC; jaccard 0.50 via owner; premises Golden, CO; dba Clean Man Products; pin has no address, matched nationwide
- `local-goat-distillery` Local Goat Distillery -> CO-S-20001 LOCAL DISTILLING INC; jaccard 0.50 via owner; premises Golden, CO; dba Clean Man Products; pin has no address, matched nationwide
- `long-road-distillers-grand-haven` Long Road Distillers - Grand Haven -> MI-S-20024 LONG ROAD DISTILLERS LLC; jaccard 0.50 via operating; premises Grand Rapids, MI; dba Long Road Distillers
- `manatawny-still-works` Manatawny Still Works -> PA-S-20120 COPPERGLEN STILL WORKS LLC; jaccard 0.50 via owner; premises Kennett Square, PA; pin has no address, matched nationwide
- `mastrogiannis-distillery-winery` Mastrogiannis Distillery & Winery -> WA-S-20089 MASTROGIANNIS DISTILLERY LLC; jaccard 0.50 via operating; premises Lakewood, WA; dba Mastrogiannis Distillery
- `mississippi-distilling-co` Mississippi Distilling Co -> IA-S-15005 MISSISSIPPI RIVER DISTILLING COMPANY, L.L.C.; jaccard 0.50 via operating; premises Leclaire, IA; dba Mississippi River Distilling Company
- `montana-distillery` Montana Distillery -> MT-S-20029 MONTANA WHISKEY COMPANY LLC; jaccard 0.50 via operating; premises Missoula, MT; dba Montana Whiskey Co.
- `montanya-distillers-cocktail-bar` Montanya Distillers | Cocktail Bar -> CO-S-15008 SYNTAX SPIRITS, LLC; jaccard 0.50 via operating; premises Greeley, CO; dba Syntax Distillery and Cocktail Bar
- `nashoba-valley-winery-distillery-brewery-and-restaurant` Nashoba Valley Winery, Distillery, Brewery and Restaurant -> MA-S-96 NASHOBA VALLEY SPIRITS, LTD.; jaccard 0.50 via owner; premises Bolton, MA
- `nashville-craft-distilery` Nashville Craft Distilery -> TN-S-20147 NASHVILLE DISTILLERY, INC; jaccard 0.50 via owner; premises Whites Creek, TN; pin has no address, matched nationwide
- `noble-grape` Noble Grape -> PA-S-20131 NOBLE DISTILLING COMPANY, LLC; jaccard 0.50 via operating; premises Wyomissing, PA; dba Noble Distilling Company; pin has no address, matched nationwide
- `northern-latitudes-distillery-suttons-bay` Northern Latitudes Distillery Suttons Bay -> MI-S-20001 NORTHERN LATITUDES DISTILLERY, LLC; jaccard 0.50 via owner; premises Lake Leelanau, MI
- `sauvage-distillery` Sauvage Distillery -> NY-S-20090 SAUVAGE BEVERAGES LLC; jaccard 0.50 via owner; premises Charloteville, NY
- `smith-creek-moonshine-nashville` Smith Creek Moonshine Nashville -> TN-S-20038 TRIPLE SSS VENTURES OF PIGEON FORGE, LLC; jaccard 0.50 via operating; premises Sevierville, TN; dba Smith Creek Distillery
- `tennessee-legend-distillery-winfield-dunn-parkway` Tennessee Legend Distillery - Winfield Dunn Parkway -> TN-S-20084 CRYSTAL FALLS SPIRITS GP; jaccard 0.50 via operating; premises Sevierville, TN; dba Tennessee Legend Distillery; owner is an individual
- `the-distillery-at-wolf-creek` The Distillery at Wolf Creek -> OH-S-15023 WOLF CREEK VINEYARDS, INC.; jaccard 0.50 via operating; premises Norton, OH; dba Wolf Creek Vineyards, Inc.
- `three-notch-d-brewery-distillery-craft-kitchen-nelson-county` Three Notch'd Brewery, Distillery & Craft Kitchen - Nelson County -> VA-S-20116 THREE NOTCH'D DISTILLING COMPANY, LLC; jaccard 0.53 via owner; premises Nellysford, VA; dba Three Notchd Distilling Company
- `twin-spirits-distillery-m-coffee-shop` Twin Spirits Distillery -> ID-S-20021 TWIN FALLS DISTILLERY, LLC.; jaccard 0.50 via operating; premises Twin Falls, ID; dba Twin Falls Distillery; pin has no address, matched nationwide
- `twisted-tap-distillery-downtown-gr` Twisted Tap Distillery Downtown GR -> MI-S-20296 TWISTED TAP DISTILLERY LLC; jaccard 0.50 via owner; premises Kentwood, MI; dba Wise Men Distillery
- `vara-winery-and-distillery` Vara Winery and Distillery -> NM-S-20013 VARA LLC; jaccard 0.50 via operating; premises Albuquerque, NM; dba VARA
- `warwick-valley-winery-distillery-orchard` Warwick Valley Winery, Distillery & Orchard -> NY-S-7 WARWICK VALLEY WINE CO., INC.; jaccard 0.50 via owner; premises Warwick, NY
- `whiskey-hollow-distillery` Whiskey Hollow Distillery -> NM-S-20016 HOLLOW SPIRITS LLC; jaccard 0.50 via operating; premises Albuquerque, NM; dba Hollow Spirits Distillery; pin has no address, matched nationwide
- `whistlepig-farm-distillery` WhistlePig Farm Distillery -> NY-S-15009 MAGNANINI FARM WINERY, INC.; jaccard 0.50 via operating; premises Wallkill, NY; dba THE FARM DISTILLERY; pin has no address, matched nationwide
- `wildcat-brothers-distilling-at-gator-cove` Wildcat Brothers Distilling at Gator Cove -> LA-S-15004 RANK WILDCAT SPIRITS, LLC; jaccard 0.50 via operating; premises Lafayette, LA; dba Wildcat Brothers Distilling
- `ye-old-grog-distillery` Ye Old Grog Distillery -> OR-S-15031 YOGD, LLC; jaccard 0.50 via operating; premises Saint Helens, OR; dba YE OL' GROG DISTILLERY; pin has no address, matched nationwide
