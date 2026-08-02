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
    label: "One producer only",
    blurb:
      "A single company discloses its own stock. No national total exists, so the country figure is inferred.",
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
    central: 3,
    low: 2,
    high: 4.5,
    tier: "producer",
    dx: 0,
    dy: -44,
    anchor: "middle",
    basis:
      "One site is documented: Crown Royal states 1.5m barrels across 51 warehouses at Gimli, Manitoba. The national figure adds an inferred allowance for Valleyfield, Hiram Walker and the Alberta distillers.",
    source: "Crown Royal (undated company site); Diageo Annual Report 2025",
    asOf: "Accessed Aug 2026",
    caveat:
      "There is no Canadian national count. Gimli alone would outrank all of England thirtyfold — the rest of the country is genuinely unmeasured.",
  },
  {
    id: "japan",
    name: "Japan",
    lon: 139.5,
    lat: 37,
    central: 1.5,
    low: 0.8,
    high: 2.5,
    tier: "dark",
    dx: 26,
    dy: -2,
    anchor: "start",
    basis:
      "No aggregate exists. Scaled from known distillery count and output against comparable markets.",
    source: "No published national figure",
    asOf: "—",
    caveat:
      "The largest hole on this map. Suntory, Nikka and Kirin publish nothing usable; a Suntory maturation site abandoned in 2026 would alone have held 500,000 barrels.",
  },
  {
    id: "india",
    name: "India",
    lon: 79,
    lat: 22.5,
    central: 0.9,
    low: 0.4,
    high: 2,
    tier: "dark",
    dx: 0,
    dy: -44,
    anchor: "middle",
    basis:
      "No aggregate exists. Sized from bottled volume: eight Indian brands sit in the world's top twenty, together shifting roughly 141m nine-litre cases a year. Applying a small matured fraction and a short residence time gives the widest range on this map.",
    source: "No published national figure",
    asOf: "\u2014",
    caveat:
      "The most misread market here. India outsells everyone \u2014 McDowell's No. 1 alone shifts more cases than any Scotch \u2014 but sales volume is not maturing stock. Most Indian whisky is molasses-based spirit that never sees oak, and several of the big blends import their malt already matured from Scotland, where it is counted. Add a tropical angel's share of 8\u201312% a year against Scotland's 2%, and stock turns over in two or three years rather than twelve. Amrut, Paul John, Rampur and Indri are real, aged and growing fast \u2014 but they are a fraction of the volume. If any figure here deserves to be overturned by someone with better data, it is this one.",
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
    central: 0.06,
    low: 0.04,
    high: 0.1,
    tier: "producer",
    dx: -20,
    dy: 6,
    anchor: "end",
    basis:
      "Lark alone reports 2.4m litres maturing — about 12,000 barrel-equivalents at 200 litres, though Lark fills far smaller casks, so the physical cask count is roughly double that.",
    source: "Lark Distilling Co., ASX reporting",
    asOf: "2025",
    caveat:
      "Tasmania punches above its weight but the numbers are small: the whole island is a rounding error against a single Kentucky rickhouse. Cask-size choice makes 'barrels' and 'casks' diverge sharply here.",
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
      "Mexico, Brazil, Argentina, New Zealand, Israel, China and the rest. Individually small, collectively not nothing, and entirely unmeasured.",
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
  IND: "dark",
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
