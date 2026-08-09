/**
 * Global whiskey aging-inventory estimate.
 *
 * There is no world census of maturing whiskey. Every figure below is either a
 * published physical count, a conversion off a published official aggregate, a
 * dated private-report estimate, or an openly-labelled guess. The tier tells you
 * which — and the whole point of the page is that the guesses stay visible.
 *
 * HOUSE RULE, inherited from the source research and worth keeping:
 * never convert a monetary inventory value, a warehouse capacity, or a
 * cooperage's annual output into a barrel count. Diageo's $7.2bn of maturing
 * whisk(e)y and Kavalan's 300,000-barrel warehouse capacity are both real
 * numbers, and neither is a count of casks currently full.
 */

export type Tier = "counted" | "estimate" | "producer" | "dark";

export const TIERS: Record<Tier, { label: string; blurb: string; color: string }> = {
  counted: {
    label: "Officially counted",
    blurb:
      "A trade body, tax authority or regulator publishes a physical count of casks or barrels.",
    color: "#7a3f18",
  },
  estimate: {
    label: "Private-report estimate",
    blurb:
      "A named commercial report with a stated method, but no government or audited basis.",
    color: "#c47b2b",
  },
  producer: {
    label: "Published partial stock",
    blurb:
      "One or more producers, or a member body, publish actual filled stock. The national total still requires an inferred allowance.",
    color: "#d9a566",
  },
  dark: {
    label: "No published figure",
    blurb:
      "A known whisky nation that publishes nothing. The number here is an order-of-magnitude guess.",
    color: "#a99276",
  },
};

export type Entry = {
  id: string;
  name: string;
  /** Where the mound is drawn, in degrees. Often pulled off-country for room. */
  lon: number;
  lat: number;
  /** If the mound sits off-country, the real place it points back to. */
  anchorLon?: number;
  anchorLat?: number;
  /** Millions of casks / barrels. */
  central: number;
  low: number;
  high: number;
  tier: Tier;
  /** Label offset from the mound apex, in map units. */
  dx: number;
  dy: number;
  anchor: "start" | "end" | "middle";
  /** What the headline figure actually counts. */
  basis: string;
  source: string;
  sourceUrl?: string;
  asOf: string;
  /** The caveat a distiller would otherwise catch us on. */
  caveat: string;
};

export const ENTRIES: Entry[] = [
  {
    id: "usa",
    name: "United States",
    lon: -100,
    lat: 41,
    central: 25,
    low: 23,
    high: 27,
    tier: "counted",
    dx: 0,
    dy: -48,
    anchor: "middle",
    basis:
      "Converted from a national aggregate: ~1.5 billion proof gallons of American whiskey in inventory at end-2024, divided by 55–66 proof gallons per filled 53-gallon barrel.",
    source: "DISCUS national inventory; Kentucky Distillers' Association",
    sourceUrl: "https://distilledspirits.org/",
    asOf: "End 2024",
    caveat:
      "Kentucky's much-quoted 17.1m barrels is one state, and it counts all spirits, not just whiskey. It is roughly two-thirds of the national figure — not the national figure.",
  },
  {
    id: "scotland",
    name: "Scotland",
    lon: -31,
    lat: 60,
    anchorLon: -4.2,
    anchorLat: 57.2,
    central: 22,
    low: 21,
    high: 23,
    tier: "counted",
    dx: 0,
    dy: -48,
    anchor: "middle",
    basis: "Physical cask count published by the industry body.",
    source: "Scotch Whisky Association, Facts & Figures",
    sourceUrl: "https://www.scotch-whisky.org.uk/industry-insights/facts-figures/",
    asOf: "2025–26",
    caveat:
      "Scotch casks average larger than a US barrel — hogsheads and butts sit alongside 200-litre refills — so Scotland holds more liquid per cask than the mound implies.",
  },
  {
    id: "ireland",
    name: "Ireland",
    lon: -20,
    lat: 46.5,
    anchorLon: -8,
    anchorLat: 53.3,
    central: 4.5,
    low: 4,
    high: 5,
    tier: "estimate",
    dx: -52,
    dy: -4,
    anchor: "end",
    basis: "Independent supply study commissioned by a cask-market platform.",
    source: "LYQD, Irish Whiskey Supply Report 2026",
    asOf: "2026",
    caveat:
      "The strongest Irish number available, but privately commissioned. Sample frame, cut-off date and duplicate controls are not public. A good estimate, not a census.",
  },
  {
    id: "canada",
    name: "Canada",
    lon: -122,
    lat: 63,
    anchorLon: -97,
    anchorLat: 50.6,
    central: 4.5,
    low: 3.1,
    high: 5.5,
    tier: "producer",
    dx: 0,
    dy: -44,
    anchor: "middle",
    basis:
      "Published producer floor: Crown Royal states 1.5m barrels at Gimli; Hiram Walker/Pike Creek has twice been described publicly as aging more than 1.6m. The 4.5m central estimate adds 1.4m for Valleyfield, Alberta Distillers and the long tail.",
    source: "Crown Royal; Hiram Walker/Pike Creek public disclosures",
    sourceUrl: "https://www.crownroyal.com/story/our-home",
    asOf: "Accessed Aug 2026",
    caveat:
      "There is no Canadian national count. The 3.1m floor is public but mixes a current undated company page with a 2017 site visit and later brand-ambassador profile. Valleyfield's and Alberta's quoted capacities are not counted as inventory; they only bound the unmeasured allowance.",
  },
  {
    id: "japan",
    name: "Japan",
    lon: 139.5,
    lat: 37,
    central: 2.3,
    low: 1.3,
    high: 4,
    tier: "producer",
    dx: 26,
    dy: -2,
    anchor: "start",
    basis:
      "Suntory's Ōmi Aging Cellar is reported at ~600,000 stored casks on one site. The national total is modelled from NTA tax aggregates: ~99.5m litres of pure alcohol packaged as whisky in FY2024, less assumed filler spirit and imported bulk, times a 3.5–7 year residence window.",
    source: "NTA liquor statistics (酒のしおり / 統計年報); Japanese trade reporting on Ōmi Aging Cellar",
    sourceUrl: "https://www.nta.go.jp/taxes/sake/shiori-gaikyo/shiori/2025/index.htm",
    asOf: "FY2024, year to March 2025",
    caveat:
      "Japan measures whisky at bottling, not at distillation — maturing new-make is explicitly excluded from every official series, so no stock count exists. The filler-spirit share and average age are assumptions, and only 0.6m of the central figure is reported stock. The 500,000-barrel site Suntory abandoned in 2026 was in Ayrshire, Scotland — never part of Japan's inventory.",
  },
  {
    id: "india",
    name: "India",
    lon: 79,
    lat: 22.5,
    central: 0.5,
    low: 0.3,
    high: 0.9,
    tier: "producer",
    dx: 0,
    dy: -44,
    anchor: "middle",
    basis:
      "The Indian Malt Whisky Association publishes 300,000+ barrels across an industry it describes as 20+ distilleries. Its named members account for more than 75% of Indian malt-whisky revenue. The 0.5m central estimate treats 300,000 as a published floor and adds an explicit allowance for non-members and other domestically matured whisky.",
    source: "Indian Malt Whisky Association",
    sourceUrl: "https://indianmaltwhisky.org/",
    asOf: "Accessed Aug 2026",
    caveat:
      "The association does not say whether 300,000 is member stock or a national malt-whisky total, and revenue share is not barrel share. India still outsells every whisky nation because the broad FSSAI whisky category may include neutral or rectified spirit and does not require all whisky to mature; only a product labelled 'matured' triggers the one-year rule. IMWA's three-year, under-700L malt standard is voluntary and narrower.",
  },
  {
    id: "china",
    name: "China",
    lon: 103,
    lat: 36,
    central: 0.75,
    low: 0.6,
    high: 1,
    tier: "producer",
    dx: -6,
    dy: -46,
    anchor: "middle",
    basis:
      "Laizhou's listed parent reported nearly 600,000 filled maturation casks at end-2025. Trade reporting places Laizhou at roughly 80% of China's whisky production and oak-barrel supply: 0.6m / 0.80 = 0.75m.",
    source: "Bairun 2025 Annual Report; CADA 2023 industry survey",
    sourceUrl:
      "https://disc.static.szse.cn/disc/disk03/finalpage/2026-04-29/d2a6a20d-faa4-43eb-b652-417f8d039339.PDF",
    asOf: "End 2025",
    caveat:
      "This is a producer-led estimate, not a current census. CADA counted 450,000 oak casks in 2023; Laizhou alone passed that two years later. The 80% share is trade reporting, and the attached 2022 map mixes operating, planned, unverified and Taiwanese sites. Capacity and first-cask announcements are not added to the total.",
  },
  {
    id: "europe",
    name: "Continental Europe",
    lon: 14,
    lat: 49,
    central: 0.3,
    low: 0.2,
    high: 0.5,
    tier: "dark",
    dx: 24,
    dy: -6,
    anchor: "start",
    basis: "No aggregate exists. Summed order-of-magnitude across active producers.",
    source: "No published national figure",
    asOf: "—",
    caveat:
      "France, Germany, Sweden, Denmark and the Netherlands all have real whisky industries now. Not one publishes a maturing-stock total.",
  },
  {
    id: "taiwan",
    name: "Taiwan",
    lon: 121.5,
    lat: 23.7,
    central: 0.15,
    low: 0.1,
    high: 0.3,
    tier: "dark",
    dx: -20,
    dy: 8,
    anchor: "end",
    basis: "No inventory figure. Inferred from known warehouse footprint.",
    source: "No published national figure",
    asOf: "—",
    caveat:
      "Kavalan's widely-quoted 300,000 barrels is storage capacity, not stock. Capacity is a building; inventory is what is in it. We do not count capacity.",
  },
  {
    id: "southafrica",
    name: "South Africa",
    lon: 25,
    lat: -29,
    central: 0.15,
    low: 0.1,
    high: 0.2,
    tier: "producer",
    dx: 20,
    dy: 8,
    anchor: "start",
    basis:
      "James Sedgwick, Africa's major whisky distillery, has been described as holding 150,000 casks across five warehouses.",
    source: "Trade reporting on James Sedgwick Distillery",
    asOf: "2018",
    caveat:
      "Eight years old and single-sourced. Africa's whisky stock is effectively unmapped — this is the weakest figure here and we would happily be corrected.",
  },
  {
    id: "australia",
    name: "Australia & Tasmania",
    lon: 146,
    lat: -30,
    central: 0.1,
    low: 0.04,
    high: 0.2,
    tier: "producer",
    dx: -20,
    dy: 6,
    anchor: "end",
    basis:
      "Lark alone reported 2.5m litres under maturation at 30 June 2025 — about 12,500 200-litre equivalents, with a higher physical cask count because Lark uses smaller formats. The national estimate adds a broad allowance across a fragmented industry.",
    source: "Lark Distilling Co., ASX reporting",
    asOf: "2025",
    caveat:
      "The Australian Distillers Association publishes operator and economic data, not a national whisky-stock count. Most members also make other spirits. Cask-size choice makes 'barrels' and physical casks diverge sharply, so this remains a wide producer-led estimate.",
  },
  {
    id: "england",
    name: "England & Wales",
    lon: -1.6,
    lat: 52.4,
    central: 0.05,
    low: 0.05,
    high: 0.07,
    tier: "counted",
    dx: -20,
    dy: 64,
    anchor: "end",
    basis: "Trade-body forecast of casks maturing.",
    source: "English Whisky Guild",
    sourceUrl: "https://www.englishwhiskyguild.com/",
    asOf: "End 2024",
    caveat:
      "Fastest-growing category on this map and the only small producer that actually publishes. Drawn to true scale, which is why it is barely visible next to Scotland.",
  },
  {
    id: "restofworld",
    name: "Rest of world",
    lon: -58,
    lat: -18,
    central: 0.15,
    low: 0.1,
    high: 0.3,
    tier: "dark",
    dx: 18,
    dy: 6,
    anchor: "start",
    basis: "Order-of-magnitude allowance for everyone not listed above.",
    source: "No published figures",
    asOf: "—",
    caveat:
      "Mexico, Brazil, Argentina, New Zealand, Israel and the rest. Individually small, collectively not nothing, and entirely unmeasured.",
  },
];

/** Which tinted country belongs to which entry, for the map fill. */
export const ISO_TIER: Record<string, Tier> = {
  USA: "counted",
  GBR: "counted",
  IRL: "estimate",
  CAN: "producer",
  ZAF: "producer",
  AUS: "producer",
  JPN: "dark",
  IND: "producer",
  CHN: "producer",
  TWN: "dark",
};

const sum = (k: "central" | "low" | "high") =>
  ENTRIES.reduce((a, e) => a + e[k], 0);

export const TOTAL = {
  central: Math.round(sum("central") * 10) / 10,
  low: Math.round(sum("low")),
  high: Math.round(sum("high")),
};

const byId = (id: string) => ENTRIES.find((e) => e.id === id)!;

/** Share held by the two countries that actually publish counts. */
export const BIG_TWO_SHARE = Math.round(
  ((byId("usa").central + byId("scotland").central) / TOTAL.central) * 100
);

/**
 * India's share of world maturing stock, against its share of world sales.
 * The gap between the two is the single most counter-intuitive fact here.
 */
export const INDIA_SHARE =
  Math.round((byId("india").central / TOTAL.central) * 1000) / 10;

/** Share sitting in countries with no national count at all. */
export const DARK_SHARE = Math.round(
  (ENTRIES.filter((e) => e.tier === "dark" || e.tier === "producer").reduce(
    (a, e) => a + e.central,
    0
  ) /
    TOTAL.central) *
    100
);

/**
 * Years of American whiskey stock at current demand, on DISCUS's own published
 * figures: ~1.5bn proof gallons of inventory against 58m domestic + 45m export.
 */
export const US_YEARS_OF_SUPPLY =
  Math.round((1500 / (58 + 45)) * 10) / 10;

/**
 * Bottle equivalent. Deliberately conservative: ~450 70cl bottles per cask
 * blends Scotch cask sizes (the SWA's own ratio implies ~545) against smaller
 * US barrel yields. Rounded hard — an illustration, not a forecast.
 */
export const BOTTLE_EQUIVALENT_BN = Math.round((TOTAL.central * 450) / 1000);
