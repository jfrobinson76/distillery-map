// Generates kentucky-county-card.html — LinkedIn social asset for the
// Kentucky county spike map (companion to the aging-inventory card).
// Data: kentucky/ky-distilled-spirits-assessed-value-by-county.csv, from the
// Kentucky Department of Revenue "Statewide Certified Property Values 2007-2025"
// (column DISTILLED SPIRITS @.05, tax year 2025 = inventory at 1 Jan 2025).
// Geometry: kentucky/ky-counties.json (US Census county boundaries, FIPS 21xxx).
// Run: node docs/social/build-kentucky-card.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const YEAR = "2025";
const SB = { page:"#F7EEDA", paperSunk:"#E8DCC2", copper:"#9C4E20", gold:"#D39A3D", amber:"#C8852E", ember:"#6E2F14", oak:"#2A1F17", stone:"#7F7262", rule:"#CDB994" };

const rows = readFileSync(join(here, "kentucky/ky-distilled-spirits-assessed-value-by-county.csv"), "utf8").trim().split(/\r?\n/).map(l => l.split(","));
const yi = rows[0].indexOf(YEAR);
const y2010 = rows[0].indexOf("2010");
const value = {}; let total = 0; const key = n => n.toLowerCase().replace(/[^a-z]/g, ""); let nelson2010 = 0;
for (const r of rows.slice(1)) { if (r[0] === "Totals") { total = +r[yi]; continue; } value[key(r[0])] = +r[yi]; if (r[0] === "Nelson") nelson2010 = +r[y2010]; }
const counties = JSON.parse(readFileSync(join(here, "kentucky/ky-counties.json"), "utf8")).features;

// ---- projection: equirectangular at 38°N, then oblique squash for the 2.5D look
const LON0 = -89.6, LAT1 = 39.16, KX = 136, KY = KX / Math.cos(38 * Math.PI / 180), SQ = 0.62, TOP = 480;
const P = (lon, lat) => [(lon - LON0) * KX, TOP + (LAT1 - lat) * KY * SQ];
const rings = g => (g.type === "MultiPolygon" ? g.coordinates : [g.coordinates]).map(p => p[0]);
const path = g => rings(g).map(r => "M" + r.map(([a, b]) => P(a, b).map(n => n.toFixed(1)).join(",")).join("L") + "Z").join("");
const centroid = g => { const pts = rings(g).flat(); return [pts.reduce((s, p) => s + p[0], 0) / pts.length, pts.reduce((s, p) => s + p[1], 0) / pts.length]; };

const vmax = Math.max(...Object.values(value));
const HMAX = 500;
const spikes = counties.map(f => { const n = f.properties.NAME; const v = value[key(n)] || 0; const [lon, lat] = centroid(f.geometry); const [x, y] = P(lon, lat); return { n, v, x, y, h: v ? Math.max(4, HMAX * v / vmax) : 0, w: v ? 5 + 11 * Math.sqrt(v / vmax) : 0 }; })
  .filter(s => s.v > 0).sort((a, b) => a.y - b.y);

const fmt = v => v >= 1e9 ? "$" + (v / 1e9).toFixed(2) + "bn" : "$" + Math.round(v / 1e6) + "m";
// label placement: [dx, dy, anchor]
const LABELS = { Nelson:[22,4,"start"], Franklin:[20,-6,"start"], Bullitt:[-18,-4,"end"], Marion:[-70,74,"end"], Jefferson:[-18,-8,"end"], Woodford:[64,-34,"start"], Anderson:[70,34,"start"] };

let svg = `<svg class="map" viewBox="0 0 1040 ${TOP + 2.7 * KY * SQ + 30}" xmlns="http://www.w3.org/2000/svg">`;
svg += `<g fill="${SB.paperSunk}" stroke="${SB.page}" stroke-width="1.2">` + counties.map(f => `<path d="${path(f.geometry)}"/>`).join("") + `</g>`;
svg += `<path d="${counties.map(f => path(f.geometry)).join("")}" fill="none" stroke="${SB.rule}" stroke-width="0.6" opacity=".7"/>`;
for (const s of spikes) {
  const tip = s.y - s.h;
  svg += `<ellipse cx="${s.x}" cy="${s.y}" rx="${s.w * 1.3}" ry="${s.w * 0.5}" fill="${SB.ember}" opacity=".18"/>`;
  svg += `<polygon points="${s.x - s.w},${s.y} ${s.x},${tip} ${s.x},${s.y + s.w * 0.35}" fill="${SB.amber}"/>`;
  svg += `<polygon points="${s.x},${s.y + s.w * 0.35} ${s.x},${tip} ${s.x + s.w},${s.y}" fill="${SB.copper}"/>`;
}
for (const s of spikes) {
  const L = LABELS[s.n]; if (!L) continue; const tip = s.y - s.h; const [dx, dy, anchor] = L;
  const lx = s.x + dx, ly = tip + dy;
  svg += `<line x1="${s.x}" y1="${tip}" x2="${lx - (anchor === "end" ? -6 : 6)}" y2="${ly - 5}" stroke="${SB.stone}" stroke-width="1"/>`;
  svg += `<text x="${lx}" y="${ly}" text-anchor="${anchor}" font-family="'Instrument Sans',sans-serif" font-size="19" font-weight="500" fill="${SB.oak}">${s.n}</text>`;
  svg += `<text x="${lx}" y="${ly + 20}" text-anchor="${anchor}" font-family="'JetBrains Mono',monospace" font-size="15" fill="${SB.stone}">${fmt(s.v)}</text>`;
}
svg += `</svg>`;

const share = Math.round(100 * value.nelson / total);
const top10 = Object.values(value).sort((a, b) => b - a).slice(0, 10).reduce((a, b) => a + b, 0);
const html = `<!doctype html>
<html><head><meta charset="utf-8"><title>Kentucky county spike map — Stillbound</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&family=Instrument+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  body { margin:0; background:#555; }
  body:not(.full) { height:100vh; overflow:hidden; }
  body:not(.full) .card { position:fixed; left:50%; top:50%; transform:translate(-50%,-50%) scale(min(calc(100vw / 1240px), calc(100vh / 1540px))); }
  .card { width:1200px; height:1500px; box-sizing:border-box; background:${SB.page}; color:${SB.oak}; display:flex; flex-direction:column; padding:78px 80px 60px; font-family:'Instrument Sans',system-ui,sans-serif; position:relative; }
  .sb { position:absolute; top:64px; right:76px; width:72px; height:72px; }
  .eyebrow { font-family:'JetBrains Mono',monospace; font-size:17px; text-transform:uppercase; letter-spacing:.24em; color:${SB.stone}; }
  h1 { font-family:Newsreader,Georgia,serif; font-weight:400; font-size:66px; line-height:1.1; letter-spacing:-.01em; margin:22px 0 0; max-width:26ch; }
  h1 .a { font-style:italic; font-weight:300; color:${SB.copper}; }
  .lede { font-size:27px; line-height:1.5; color:${SB.stone}; margin-top:20px; max-width:46ch; }
  .map { margin:-60px 0 0; width:100%; display:block; }
  .kicker { font-family:Newsreader,Georgia,serif; font-style:italic; font-weight:300; font-size:36px; color:${SB.copper}; margin:6px 0 16px; line-height:1.25; }
  .footnote { font-family:'JetBrains Mono',monospace; font-size:15px; text-transform:uppercase; letter-spacing:.12em; color:${SB.stone}; margin-top:12px; line-height:1.6; }
  .footer { margin-top:auto; display:flex; justify-content:space-between; align-items:baseline; border-top:1px solid ${SB.rule}; padding-top:26px; }
  .tagline { font-family:'JetBrains Mono',monospace; font-size:14px; text-transform:uppercase; letter-spacing:.22em; color:${SB.copper}; margin-left:22px; }
  .wm { font-family:Newsreader,Georgia,serif; font-size:33px; color:${SB.oak}; }
  .wm i { font-style:italic; font-weight:300; color:${SB.copper}; }
  .site { font-family:'JetBrains Mono',monospace; font-size:16px; text-transform:uppercase; letter-spacing:.18em; color:${SB.stone}; }
</style></head>
<body>
  <script>if (location.search.includes("full")) document.body.classList.add("full");</script>
  <div class="card">
    <svg class="sb" viewBox="0 0 100 100"><text x="50.5" y="59" text-anchor="middle" dominant-baseline="central" font-family="Newsreader, Georgia, serif" font-size="84" font-weight="400" letter-spacing="-3" fill="${SB.copper}">S<tspan font-style="italic" font-weight="300" fill="${SB.gold}">b</tspan></text></svg>
    <div class="eyebrow">Stillbound Research · Kentucky · Inventory at 1 January 2025</div>
    <h1>Where Kentucky keeps <span class="a">its whiskey</span></h1>
    <div class="lede">Aging spirits on the books, by county, from distillers&rsquo; own filings with the Kentucky Department of Revenue. ${fmt(total).replace("$","$")} across ${spikes.length} counties. One county holds ${share}% of it.</div>
    ${svg}
    <div class="kicker">The only place on earth this map can be drawn.</div>
    <div class="footnote">Nelson County ${fmt(value.nelson)} · ${fmt(nelson2010)} in 2010 · Top 10 counties ${Math.round(100 * top10 / total)}% of the state</div>
    <div class="footnote">Assessed value, not barrels · spirit under two years old is exempt and not shown · KY Dept of Revenue, Statewide Certified Property Values 2007–2025</div>
    <div class="footer">
      <span><span class="wm">Still<i>bound</i></span><span class="tagline">Liquid intelligence</span></span>
      <span class="site">stillbound.ai/research</span>
    </div>
  </div>
</body></html>`;
writeFileSync(join(here, "kentucky-county-card.html"), html);
console.log("total", fmt(total), "counties", spikes.length, "nelson share", share + "%", "top10", Math.round(100 * top10 / total) + "%");
