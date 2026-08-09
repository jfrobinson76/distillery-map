// Generates aging-inventory-map-card.html — the LinkedIn social asset.
// Reuses the baked Natural Earth paths from src/lib/world-map-paths.ts and
// renders the cask mounds in Stillbound creative (paper-and-bronze).
// Run: node docs/social/build-map-card.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, "../../src/lib/world-map-paths.ts"), "utf8");
const WORLD_BASE_PATH = src.match(/WORLD_BASE_PATH = "([^"]+)"/)[1];
// Tinted countries live in their own paths — without these, the US, Canada,
// Australia, Japan et al. are literally missing from the land.
const COUNTRY_PATHS = JSON.parse(src.match(/COUNTRY_PATHS: Record<string, string> = (\{[\s\S]*?\});/)[1]);

const SB = {
  page: "#F7EEDA",
  paperSunk: "#E8DCC2",
  copper: "#9C4E20",
  gold: "#D39A3D",
  amber: "#C8852E",
  ember: "#6E2F14",
  oak: "#2A1F17",
  stone: "#7F7262",
  rule: "#CDB994",
};

const project = (lon, lat) => [(lon + 180) * 5.555555555555555, (84 - lat) * 5.555555555555555];
const K = 38;
const RATIO = 0.62;
const moundW = (m) => K * Math.sqrt(m);

// tier → treatment. counted = copper solid; estimate = gold; producer = amber;
// dark = dashed outline, no fill (nobody publishes anything).
const TIER_FILL = { counted: SB.copper, estimate: SB.gold, producer: SB.amber };

const ENTRIES = [
  { id: "usa", lon: -100, lat: 41, central: 25, tier: "counted" },
  { id: "scotland", lon: -13, lat: 62.5, central: 22, tier: "counted", aLon: -4.2, aLat: 57.2 },
  { id: "ireland", lon: -20, lat: 46.5, central: 4.5, tier: "estimate", aLon: -8, aLat: 53.3 },
  { id: "canada", lon: -112, lat: 60, central: 4.3, tier: "producer", aLon: -97, aLat: 50.6 },
  { id: "japan", lon: 139.5, lat: 37, central: 2.3, tier: "producer" },
  { id: "china", lon: 103, lat: 36, central: 0.75, tier: "producer" },
  { id: "india", lon: 79, lat: 22.5, central: 0.5, tier: "producer" },
  { id: "europe", lon: 14, lat: 49, central: 0.4, tier: "producer" },
  { id: "taiwan", lon: 121.5, lat: 23.7, central: 0.15, tier: "dark" },
  { id: "southafrica", lon: 25, lat: -29, central: 0.15, tier: "producer" },
  { id: "restofworld", lon: -58, lat: -18, central: 0.15, tier: "dark" },
  { id: "australia", lon: 146, lat: -30, central: 0.1, tier: "producer" },
  { id: "england", lon: -1.6, lat: 52.4, central: 0.05, tier: "counted" },
];

// Big five get the two-line treatment (mono name + serif number); everything
// else gets a small mono tag so no cask sits unexplained. dx/dy from mound
// apex (small tags: from cask base); anchor = text-anchor.
const LABELS = {
  usa: { name: "UNITED STATES", num: "~25m casks*", dx: 0, dy: 152, anchor: "middle" },
  scotland: { name: "SCOTLAND", num: "22m casks*", dx: 0, dy: -30, anchor: "middle" },
  ireland: { name: "IRELAND", num: "4.5m*", dx: -58, dy: 8, anchor: "end" },
  canada: { name: "CANADA", num: "~4.3m*", dx: 0, dy: -44, anchor: "middle" },
  japan: { name: "JAPAN", num: "~2.3m*", dx: -40, dy: -68, anchor: "end" },
  china: { small: "CHINA 0.75m*", dx: 22, dy: -16, anchor: "start" },
  india: { small: "INDIA 0.5m*", dx: 0, dy: 28, anchor: "middle" },
  europe: { small: "EUROPE 0.4m*", dx: 0, dy: 26, anchor: "middle" },
  taiwan: { small: "TAIWAN 0.15m*", dx: 16, dy: -4, anchor: "start" },
  southafrica: { small: "SOUTH AFRICA 0.15m*", dx: 16, dy: -8, anchor: "start" },
  australia: { small: "AUSTRALIA 0.1m*", dx: -10, dy: -20, anchor: "end" },
  england: { small: "ENGLAND 50k*", dx: 10, dy: -6, anchor: "start" },
  restofworld: { small: "REST OF WORLD 0.15m*", dx: 16, dy: -6, anchor: "start" },
};

/** One barrel seen end-on: staved circle with hoop rings and a bung dot. */
function barrel(cx, cy, r, fill, ghost) {
  if (ghost) {
    return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${SB.page}" fill-opacity="0.6" stroke="${SB.stone}" stroke-width="1.6" stroke-dasharray="4 3"/>`;
  }
  let out = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" stroke="${SB.ember}" stroke-width="1.2"/>`;
  if (r >= 5) {
    out += `<circle cx="${cx}" cy="${cy}" r="${r * 0.62}" fill="none" stroke="${SB.page}" stroke-width="1" stroke-opacity="0.5"/>`;
    out += `<circle cx="${cx}" cy="${cy}" r="${Math.max(1, r * 0.13)}" fill="${SB.page}" fill-opacity="0.55"/>`;
  }
  return out;
}

/**
 * A mound built from actual casks: pyramid rows of barrel ends, the way old
 * trade maps drew warehouse stocks. Footprint stays area-proportional (w x h
 * from the sqrt rule); barrel size adapts per mound so each stack stays legible.
 */
function mound(e) {
  const [x, baseY] = project(e.lon, e.lat);
  const w = moundW(e.central);
  const h = w * RATIO;
  const ghost = e.tier === "dark";
  const fill = TIER_FILL[e.tier];

  let out = `<ellipse cx="${x}" cy="${baseY + 1.5}" rx="${w / 2 + 2}" ry="${Math.max(2, w * 0.05)}" fill="${SB.oak}" opacity="0.12"/>`;

  // Barrel diameter: single barrel for tiny entries, else ~w/16-sized rows.
  if (w <= 20) {
    return out + barrel(x, baseY - w / 2, w / 2, fill, ghost);
  }
  const d = w / Math.max(3, Math.round(w / 17));
  const r = d / 2;
  const rowStep = d * 0.85; // rows nest into the gaps below
  const rows = Math.max(2, Math.round(h / rowStep));

  for (let k = 0; k < rows; k++) {
    const y = baseY - r - k * rowStep;
    const rowW = w * (1 - k / rows);
    const count = Math.max(1, Math.round(rowW / d));
    const startX = x - ((count - 1) * d) / 2;
    for (let j = 0; j < count; j++) {
      out += barrel(startX + j * d, y, r, fill, ghost);
    }
    if (count === 1) break;
  }
  return out;
}

function anchorLine(e) {
  if (e.aLon === undefined) return "";
  const [ax, ay] = project(e.aLon, e.aLat);
  const [mx, my] = project(e.lon, e.lat);
  return `<line x1="${mx}" y1="${my}" x2="${ax}" y2="${ay}" stroke="${SB.copper}" stroke-width="1.6" stroke-opacity="0.5" stroke-dasharray="5 4"/><circle cx="${ax}" cy="${ay}" r="4" fill="${SB.copper}"/>`;
}

function label(e) {
  const cfg = LABELS[e.id];
  if (!cfg) return "";
  const [x, baseY] = project(e.lon, e.lat);
  const apexY = baseY - moundW(e.central) * RATIO;
  const halo = `stroke="${SB.page}" stroke-width="10" stroke-linejoin="round" paint-order="stroke"`;
  if (cfg.small) {
    return `<text x="${x + cfg.dx}" y="${apexY + cfg.dy}" text-anchor="${cfg.anchor}" font-family="'JetBrains Mono', monospace" font-size="21" letter-spacing="2" fill="${SB.stone}" ${halo}>${cfg.small}</text>`;
  }
  const lx = x + cfg.dx;
  const ly = apexY + cfg.dy;
  const numFill = e.tier === "dark" ? SB.stone : SB.oak;
  const numStyle = e.tier === "dark" ? `font-style="italic" font-size="32"` : `font-size="44" font-weight="600"`;
  return (
    `<text x="${lx}" y="${ly}" text-anchor="${cfg.anchor}" font-family="'JetBrains Mono', monospace" font-size="22" letter-spacing="3" fill="${SB.stone}" ${halo}>${cfg.name}</text>` +
    `<text x="${lx}" y="${ly + 42}" text-anchor="${cfg.anchor}" font-family="Newsreader, Georgia, serif" ${numStyle} fill="${numFill}" ${halo}>${cfg.num}</text>`
  );
}

const ordered = [...ENTRIES].sort((a, b) => b.central - a.central);
// Crop empty Pacific both sides; keep room above Scotland's label.
const VB = { x: 150, y: -50, w: 1740, h: 828 };
const svg =
  `<svg viewBox="${VB.x} ${VB.y} ${VB.w} ${VB.h}" width="100%" role="img" aria-label="World map of maturing whiskey by country, cask mounds drawn to true scale.">` +
  `<path d="${WORLD_BASE_PATH}" fill="${SB.paperSunk}" stroke="${SB.rule}" stroke-width="0.6"/>` +
  Object.values(COUNTRY_PATHS)
    .map((d) => `<path d="${d}" fill="${SB.paperSunk}" stroke="${SB.rule}" stroke-width="0.6"/>`)
    .join("") +
  ordered.map(anchorLine).join("") +
  ordered.map(mound).join("") +
  ordered.map(label).join("") +
  `</svg>`;

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Aging inventory map — LinkedIn card</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&family=Instrument+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  body { margin: 0; background: #555; }
  body:not(.full) { height: 100vh; overflow: hidden; }
  body:not(.full) .card {
    position: fixed; left: 50%; top: 50%;
    transform: translate(-50%, -50%) scale(min(calc(100vw / 1240px), calc(100vh / 1240px)));
  }
  .card {
    width: 1200px; height: 1200px; box-sizing: border-box;
    background: ${SB.page}; color: ${SB.oak};
    display: flex; flex-direction: column;
    padding: 78px 84px 64px;
    font-family: 'Instrument Sans', system-ui, sans-serif;
    position: relative;
  }
  .sb { position: absolute; top: 64px; right: 76px; width: 72px; height: 72px; }
  .eyebrow {
    font-family: 'JetBrains Mono', monospace; font-size: 17px;
    text-transform: uppercase; letter-spacing: 0.24em; color: ${SB.stone};
  }
  h1 {
    font-family: Newsreader, Georgia, serif; font-weight: 400;
    font-size: 64px; line-height: 1.12; letter-spacing: -0.01em;
    margin: 22px 0 0; max-width: 21ch;
  }
  h1 .a { font-style: italic; font-weight: 300; color: ${SB.copper}; }
  .lede {
    font-size: 27px; line-height: 1.5; color: ${SB.stone};
    margin-top: 20px; max-width: 44ch;
  }
  .map { margin: 10px 0 0 -54px; width: calc(100% + 108px); }
  .kicker {
    font-family: Newsreader, Georgia, serif; font-style: italic; font-weight: 300;
    font-size: 34px; color: ${SB.copper}; margin: 10px 0 18px;
  }
  .legend {
    display: flex; gap: 34px; align-items: center;
    font-family: 'JetBrains Mono', monospace; font-size: 15px;
    text-transform: uppercase; letter-spacing: 0.14em; color: ${SB.stone};
    margin-top: 4px;
  }
  .sw { display: inline-block; width: 15px; height: 15px; margin-right: 9px; vertical-align: -2px; }
  .footnote {
    font-family: 'JetBrains Mono', monospace; font-size: 15px;
    text-transform: uppercase; letter-spacing: 0.12em; color: ${SB.stone};
    margin-top: 14px;
  }
  .footer {
    margin-top: auto; display: flex; justify-content: space-between; align-items: baseline;
    border-top: 1px solid ${SB.rule}; padding-top: 26px;
  }
  .tagline {
    font-family: 'JetBrains Mono', monospace; font-size: 14px;
    text-transform: uppercase; letter-spacing: 0.22em; color: ${SB.copper};
    margin-left: 22px;
  }
  .wm { font-family: Newsreader, Georgia, serif; font-size: 33px; color: ${SB.oak}; }
  .wm i { font-style: italic; font-weight: 300; color: ${SB.copper}; }
  .site {
    font-family: 'JetBrains Mono', monospace; font-size: 16px;
    text-transform: uppercase; letter-spacing: 0.18em; color: ${SB.stone};
  }
</style>
</head>
<body>
  <script>if (location.search.includes("full")) document.body.classList.add("full");</script>
  <div class="card">
    <svg class="sb" viewBox="0 0 100 100"><text x="50.5" y="59" text-anchor="middle" dominant-baseline="central" font-family="Newsreader, Georgia, serif" font-size="84" font-weight="400" letter-spacing="-3" fill="${SB.copper}">S<tspan font-style="italic" font-weight="300" fill="${SB.gold}">b</tspan></text></svg>
    <div class="eyebrow">Global Whiskey Aging Inventory · August 2026</div>
    <h1>60.4 million* casks of whiskey are aging <span class="a">right now.</span></h1>
    <div class="lede">We went looking for global aged whiskey stock levels. No world number existed. So we are building one.</div>
    <div class="map">${svg}</div>
    <div class="kicker">Two countries hold 78%* of it.</div>
    <div class="footnote">Solid casks: published or derived figures · dashed: no published figure</div>
    <div class="footnote">* Estimated on Stillbound research data · full sources &amp; caveats at distillerymap.org</div>
    <div class="footer">
      <span><span class="wm">Still<i>bound</i></span><span class="tagline">Liquid intelligence</span></span>
      <span class="site">distillerymap.org</span>
    </div>
  </div>
</body>
</html>
`;

writeFileSync(join(here, "aging-inventory-map-card.html"), html);
console.log("wrote aging-inventory-map-card.html");
