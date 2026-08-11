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

export type Tier = "counted" | "derived" | "estimate" | "producer" | "dark";

export const TIERS: Record<Tier, { label: string; blurb: string; color: string }> = {
  counted: {
    label: "Officially counted",
    blurb:
      "A trade body, tax authority or regulator publishes a physical count of casks or barrels.",
    color: "#7a3f18",
  },
  // Added 11 Aug 2026. The US was tiered "counted" while its own basis said
  // "converted from a national aggregate", which is Rule 3 applied to everyone
  // but ourselves: an official total in another unit, divided by an assumed
  // per-barrel fill, is not a physical count. Flagged independently three times
  // in one day, which is how often a sharp reader will find it.
  derived: {
    label: "Official aggregate, converted",
    blurb:
      "A government or trade body publishes a national total, but in another unit. The cask count is converted with a stated divisor and a visible assumption band, not counted.",
    color: "#a05a22",
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
    tier: "derived",
    dx: 0,
    dy: -48,
    anchor: "middle",
    basis:
      "Converted from a national aggregate: ~1.5 billion proof gallons of American whiskey in inventory at end-2024, divided by 55–66 proof gallons per filled 53-gallon barrel.",
    source: "DISCUS national inventory; Kentucky Distillers' Association",
    sourceUrl: "https://distilledspirits.org/",
    asOf: "End 2024",
    caveat:
      "Kentucky's much-quoted 17.1m barrels is one state, and it counts all spirits: 16.1m barrels of bourbon plus ~1m of other spirits, per the KDA release of 8 Oct 2025, from inventories reported to the Kentucky Department of Revenue as of 1 Jan 2025. It is a state total, not the national one. Do not express it as a fraction of the US figure — an all-spirits state number over a whiskey-only national number is not a real ratio.",
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
    basis:
      "Independent supply study commissioned by a cask-market platform (analysis Oct 2025), corroborated by two lines that share none of its inputs: Drinks Ireland's published count of over 3.1m casks maturing in 2020, rolled forward on production-minus-withdrawals arithmetic to ~4.1m; and a producer bottom-up — Irish Distillers 1.7m casks (2021, company blender), Great Northern 500k (company site), Bushmills 500k+ (trade, 2026), Waterford 70k+ (receivership sale) — that brackets 3.8–4.2m with an itemised allowance for Tullamore, Cooley, West Cork and the long tail.",
    source: "LYQD Irish Whiskey Supply Report 2026; Drinks Ireland; producer disclosures",
    sourceUrl: "https://exchange.lyqd.io/lyqd-irish-whiskey-supply-report-2026/",
    asOf: "Analysis Oct 2025, published May 2026",
    caveat:
      "Privately commissioned and unaudited, but no longer standing alone: two independent derivations land within ten percent of it. Both centre slightly below 4.5m, so the residual risk points down, not up — and with most Irish distilleries pausing or cutting production since 2025, this is a plateau figure, not a growth path. Ireland publishes no official stock series.",
  },
  {
    id: "canada",
    name: "Canada",
    lon: -122,
    lat: 63,
    anchorLon: -97,
    anchorLat: 50.6,
    central: 4.3,
    low: 3.9,
    high: 5.2,
    tier: "producer",
    dx: 0,
    dy: -44,
    anchor: "middle",
    basis:
      "Published producer floor of 3.9m across four sites: Crown Royal states 1.5m barrels at Gimli, Hiram Walker/Pike Creek is publicly reported at more than 1.6m, Alberta Distillers' own site states 447k, and Heaven Hill puts Black Velvet/Lethbridge at ~340k. The central adds an itemised ~0.6m allowance for Valleyfield, the Sazerac sites and the long tail, disciplined by a withdrawal-times-residence model on US consumption (~16.9m 9-litre cases) and domestic sales.",
    source: "Crown Royal, Hiram Walker, Alberta Distillers, Black Velvet company and trade disclosures",
    sourceUrl: "https://www.crownroyal.com/story/our-home",
    asOf: "Site figures 2016–2026, accessed Aug 2026",
    caveat:
      "There is no current Canadian national count — the only official stock series (StatCan 16-10-0091, spirits in bond) was terminated in 1996. The Hiram Walker and Black Velvet figures are 2016–2019 vintage, and a flow model built on sales centres lower, at 3.2m; the central leans on reported filled stock. Quoted warehouse capacities are never counted as inventory.",
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
      "Japan publishes no usable national maturing-stock aggregate. The NTA's public series excludes whisky new-make, although manufacturers report it separately to the tax authority. The filler-spirit share and average age are assumptions, and only 0.6m of the central figure is reported stock. The 500,000-barrel site Suntory abandoned in 2026 was in Ayrshire, Scotland — never part of Japan's inventory.",
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
      "Two sites are independently anchored: NSE-listed Piccadily Agro told investors in April 2026 it holds ~85,000 barrels at Indri, and Paul John is trade-reported at ~33,500 casks in Goa. A producer bottom-up across the 20+ malt distilleries lands at ~235k malt casks, bracketing the Indian Malt Whisky Association's 300,000+ barrel figure. The 0.5m central is ~0.3m domestically maturing malt plus an allowance for matured grain whisky and non-members.",
    source: "Piccadily Agro investor disclosures; Paul John trade reporting; Indian Malt Whisky Association",
    sourceUrl: "https://indianmaltwhisky.org/",
    asOf: "Piccadily Apr 2026; IMWA accessed Aug 2026",
    caveat:
      "IMWA's figure is labelled simply 'Barrels' — it does not say stock or capacity, member or national, and its flagship member uses the same convention for warehouse capacity. India still outsells every whisky nation because the broad FSSAI whisky category may include neutral or rectified spirit and does not require all whisky to mature; only a product labelled 'matured' triggers the one-year rule, and tropical evaporation of 8–12% a year turns what is laid down over in 2–4 years.",
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
    central: 0.4,
    low: 0.25,
    high: 0.55,
    tier: "producer",
    dx: 24,
    dy: -6,
    anchor: "start",
    basis:
      "Bottom-up across published stock: Spain's DYC trade-reported at 170,000 aging casks, High Coast publishes 20,000+, St. Kilian ~10,500 counted, plus a flow model on the INAO's official French production series (~100 distilleries, 20,000 hl pure alcohol in 2020).",
    source: "Alimarket (DYC); INAO Whisky Français note; producer disclosures",
    sourceUrl:
      "https://www.alimarket.es/alimentacion/noticia/295757/beam-suntory-eleva-su-capacidad-en-espana-e-inicia-la-exportacion-de--dyc--a-latinoamerica",
    asOf: "2019–2026, mixed",
    caveat:
      "About 40% of this hangs on one 2019 Spanish trade figure that may describe DYC's cellar complement rather than filled casks. France is a model, not a count; Germany, Denmark and the rest are allowances. No European body publishes a maturing-stock total.",
  },
  {
    id: "taiwan",
    name: "Taiwan",
    lon: 121.5,
    lat: 23.7,
    central: 0.15,
    low: 0.1,
    high: 0.25,
    tier: "dark",
    dx: -20,
    dy: 8,
    anchor: "end",
    basis:
      "Withdrawal × residence model: Kavalan's 10m+ bottles a year at 4–6 years' subtropical residence implies ~90,000–200,000 filled casks. Nantou/Omar adds a reported ~4,500-cask floor from a 2017 site visit.",
    source: "Derived; no producer publishes filled stock",
    asOf: "2026 model on 2024–25 disclosures",
    caveat:
      "Kavalan's widely-quoted 300,000 barrels is storage capacity, not stock — we still refuse to count capacity, and the model says the warehouses are roughly half full. Bottle volumes and residence are assumptions, so the grade stays dark.",
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
      "James Sedgwick, Africa's major whisky distillery, reported at 150,000+ casks — five warehouses in a dated 2018 visit, seven in post-Heineken-merger trade profiles.",
    source: "Trade reporting on James Sedgwick Distillery",
    asOf: "2018, corroborated post-2023",
    caveat:
      "The 150,000 recurs on both sides of the 2023 Distell–Heineken merger but has never been company-published, and may be a recycled talking-point. The craft tail is an allowance. Still the entry we would most like to be corrected on.",
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
  // Epsilon guards the half-up convention: the entry sum can land exactly on a
  // .x5 boundary (60.35 in Aug 2026) and float error would otherwise round it down.
  central: Math.round(sum("central") * 10 + 1e-6) / 10,
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
