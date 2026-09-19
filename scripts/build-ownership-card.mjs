/**
 * Build the "Who Runs the UK's Stills" ownership card.
 *
 * Reads the company crosswalk (high/verified UK rows only), joins the hand-checked
 * group table, computes the claim numbers, writes HTML / summary / PNG.
 *
 *   npm run ownership-card
 *
 * Does not write anything under data/company-crosswalk/.
 */
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, "..");

// Page slug is a variable: the public page does not exist yet.
const SOURCE_SLUG = "stillbound.ai/research/ownership";
const EDITION = "September 2026";

const CROSSWALK = join(ROOT, "data/company-crosswalk/company-crosswalk.csv");
const GROUPS_PATH = join(ROOT, "data/ownership/groups.json");
const GEOJSON = join(ROOT, "public/data/distilleries.geojson");
const OUT_DIR = join(ROOT, "docs/social/ownership");
const HTML_OUT = join(OUT_DIR, "ownership-card.html");
const PNG_OUT = join(OUT_DIR, "ownership-card-2400.png");
const SUMMARY_OUT = join(OUT_DIR, "ownership-summary.md");

const SB = {
  page: "#F7EEDA",
  paperSunk: "#E8DCC2",
  copper: "#9C4E20",
  copper2: "#A05A22",
  gold: "#D39A3D",
  amber: "#C8852E",
  ember: "#6E2F14",
  oak: "#2A1F17",
  stone: "#7F7262",
  rule: "#CDB994",
};

// One colour per hub, from the card palette plus three restrained extras. No primary blue or green.
const HUB_COLOURS = {
  diageo: SB.ember,
  "pernod-ricard": SB.copper,
  "whyte-mackay": SB.amber,
  bacardi: SB.gold,
  suntory: SB.copper2,
  "ian-macleod": "#8B5A3C",
  "william-grant": "#B87333",
  "inver-house": "#C4A574",
  lvmh: "#9A6B4F",
  nikka: "#A67C52",
  "brown-forman": "#7A4A2A",
};

const CONFIDENCE_OK = new Set(["high", "verified"]);

const CHROME_CANDIDATES = [
  process.env.CHROME,
  "/opt/google/chrome/chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/local/bin/google-chrome",
].filter(Boolean);

function findChrome() {
  return CHROME_CANDIDATES.find((p) => existsSync(p));
}

function parseCsv(text) {
  const rows = [];
  let i = 0;
  const field = () => {
    if (text[i] === '"') {
      i += 1;
      let out = "";
      while (i < text.length) {
        if (text[i] === '"' && text[i + 1] === '"') {
          out += '"';
          i += 2;
          continue;
        }
        if (text[i] === '"') {
          i += 1;
          break;
        }
        out += text[i];
        i += 1;
      }
      return out;
    }
    const start = i;
    while (i < text.length && text[i] !== "," && text[i] !== "\n" && text[i] !== "\r") i += 1;
    return text.slice(start, i);
  };
  const headers = [];
  while (i < text.length && text[i] !== "\n" && text[i] !== "\r") {
    headers.push(field());
    if (text[i] === ",") i += 1;
  }
  if (text[i] === "\r") i += 1;
  if (text[i] === "\n") i += 1;
  while (i < text.length) {
    if (text[i] === "\n" || text[i] === "\r") {
      if (text[i] === "\r") i += 1;
      if (text[i] === "\n") i += 1;
      continue;
    }
    const row = {};
    for (let h = 0; h < headers.length; h += 1) {
      row[headers[h]] = field();
      if (text[i] === ",") i += 1;
    }
    rows.push(row);
    if (text[i] === "\r") i += 1;
    if (text[i] === "\n") i += 1;
  }
  return rows;
}

function normName(s) {
  return (s || "").trim().toLowerCase().replace(/\s+/g, " ");
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a += 0x6d2b79f5;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hubRadius(count) {
  return 14 + 7.2 * Math.sqrt(count);
}

function ringRadius(hubR, n) {
  const nodeGap = 16;
  return Math.max(hubR + 26, (nodeGap * n) / (2 * Math.PI));
}

function clusterRadius(count) {
  return ringRadius(hubRadius(count), count) + 10;
}

function matchGroup(row, groups) {
  const num = (row.company_number || "").trim();
  const name = normName(row.company_name);
  for (const g of groups) {
    if (num && g.company_numbers.includes(num)) return g;
    if (name && g.company_names.map(normName).includes(name)) return g;
  }
  return null;
}

function loadUkRows() {
  const rows = parseCsv(readFileSync(CROSSWALK, "utf8"));
  const geo = JSON.parse(readFileSync(GEOJSON, "utf8"));
  const bySlug = new Map(geo.features.map((f) => [f.properties.slug, f]));
  return rows
    .filter((r) => r.country === "United Kingdom" && CONFIDENCE_OK.has(r.confidence))
    .map((r) => {
      const feat = bySlug.get(r.slug);
      return {
        slug: r.slug,
        name: feat?.properties?.name || r.distillery_name,
        company_name: r.company_name,
        company_number: r.company_number,
        relation: r.relation,
        confidence: r.confidence,
        note: r.note,
        lon: feat?.geometry?.coordinates?.[0] ?? null,
        lat: feat?.geometry?.coordinates?.[1] ?? null,
      };
    });
}

function compute(rows, groupTable) {
  const groupsById = new Map(groupTable.map((g) => [g.id, { ...g, sites: [] }]));
  const independents = [];

  for (const row of rows) {
    const g = matchGroup(row, groupTable);
    if (g) groupsById.get(g.id).sites.push(row);
    else independents.push(row);
  }

  // A mapped group with exactly one distillery is Independent by definition.
  for (const g of groupsById.values()) {
    if (g.sites.length === 1) {
      independents.push(g.sites[0]);
      g.sites = [];
    }
  }

  const activeGroups = [...groupsById.values()]
    .filter((g) => g.sites.length >= 2)
    .sort((a, b) => b.sites.length - a.sites.length || a.display.localeCompare(b.display));

  const hubs = activeGroups.slice(0, 8);
  const lesserGroups = activeGroups.slice(8);

  const total = rows.length;
  const independentCount = independents.length;
  const hubSiteCount = hubs.reduce((n, g) => n + g.sites.length, 0);
  const diageo = activeGroups.find((g) => g.id === "diageo");
  const independentShare = total ? independentCount / total : 0;

  const indByCo = new Map();
  for (const row of independents) {
    const key = `${row.company_number}||${normName(row.company_name)}`;
    if (!indByCo.has(key)) {
      indByCo.set(key, {
        company_name: row.company_name,
        company_number: row.company_number,
        sites: [],
      });
    }
    indByCo.get(key).sites.push(row.name);
  }
  const multiSiteIndependents = [...indByCo.values()]
    .filter((c) => c.sites.length > 1)
    .map((c) => ({ ...c, count: c.sites.length }))
    .sort((a, b) => b.count - a.count || a.company_name.localeCompare(b.company_name));

  return {
    total,
    independentCount,
    independentShare,
    hubSiteCount,
    diageoCount: diageo?.sites.length ?? 0,
    hubs,
    lesserGroups,
    independents,
    multiSiteIndependents,
    edition: EDITION,
    sourceSlug: SOURCE_SLUG,
  };
}

function placeLayout(data) {
  // Network lives in a 1200×1200 card; this box is the drawing area for nodes.
  const box = { x: 40, y: 120, w: 1120, h: 780 };
  const reserved = { x: 720, y: 760, w: 440, h: 320 };
  const rng = mulberry32(20260918);

  // Fixed slots, largest first. Keeps the bottom-right free for the number
  // and is stable across rebuilds. Tuned against the 393px feed crop.
  const SLOTS = [
    [300, 400],
    [530, 590],
    [500, 230],
    [860, 560],
    [820, 270],
    [640, 450],
    [1000, 400],
    [700, 155],
  ];

  const placedHubs = [];
  data.hubs.forEach((hub, i) => {
    const count = hub.sites.length;
    const r = hubRadius(count);
    const cR = clusterRadius(count);
    const slot = SLOTS[i] || [box.x + 120 + i * 90, box.y + 200];
    const x = slot[0];
    const y = slot[1];
    const ringR = ringRadius(r, count);
    // Leave a gap at the bottom of the ring so the hub label does not sit on a node.
    const gap = 0.95;
    const span = Math.PI * 2 - gap;
    const startAng = Math.PI / 2 + gap / 2;
    const sites = [...hub.sites].sort((a, b) => a.name.localeCompare(b.name));
    const spokes = sites.map((s, k) => {
      const ang = startAng + (k * span) / count;
      return {
        ...s,
        x: x + Math.cos(ang) * ringR,
        y: y + Math.sin(ang) * ringR,
        ang,
        label: null,
      };
    });
    placedHubs.push({
      ...hub,
      x,
      y,
      r,
      cR,
      ringR,
      colour: HUB_COLOURS[hub.id] || SB.copper,
      spokes,
    });
  });
  // Spoke names are unreadable at feed width (15px → ~5px). Hubs stay labelled.

  const obstacles = placedHubs.map((h) => ({ x: h.x, y: h.y, r: h.cR + 16 }));
  const lesserNodes = [];
  for (const g of data.lesserGroups) {
    const colour = HUB_COLOURS[g.id] || SB.stone;
    for (const s of g.sites) lesserNodes.push({ ...s, colour, alpha: 0.85 });
  }

  const field = [
    ...data.independents.map((s) => ({ ...s, colour: SB.stone, alpha: 0.55 })),
    ...lesserNodes,
  ];
  const fieldPts = [];
  let attempt = 0;
  while (fieldPts.length < field.length && attempt < field.length * 200) {
    attempt += 1;
    const x = box.x + 16 + rng() * (box.w - 32);
    const y = box.y + 16 + rng() * (box.h - 24);
    if (x > reserved.x && y > reserved.y - 40) continue;
    if (obstacles.some((o) => Math.hypot(x - o.x, y - o.y) < o.r)) continue;
    if (fieldPts.some((p) => Math.hypot(x - p.x, y - p.y) < 8.5)) continue;
    fieldPts.push({ x, y });
  }
  console.log(`independent field ${fieldPts.length}/${field.length}`);

  const fieldPlaced = field.map((s, i) => ({
    ...s,
    x: fieldPts[i]?.x ?? box.x + 20 + (i % 40) * 12,
    y: fieldPts[i]?.y ?? box.y + 20 + Math.floor(i / 40) * 12,
  }));

  return { box, placedHubs, fieldPlaced };
}

function svgNetwork(layout) {
  const { placedHubs, fieldPlaced } = layout;
  let out = "";

  for (const n of fieldPlaced) {
    const fill = n.colour || SB.stone;
    const op = n.alpha ?? 0.85;
    out += `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="3.2" fill="${fill}" fill-opacity="${op}"/>`;
  }

  for (const hub of placedHubs) {
    for (const s of hub.spokes) {
      out += `<line x1="${hub.x.toFixed(1)}" y1="${hub.y.toFixed(1)}" x2="${s.x.toFixed(1)}" y2="${s.y.toFixed(1)}" stroke="${SB.ember}" stroke-width="1.15" stroke-opacity="0.35"/>`;
    }
  }

  for (const hub of placedHubs) {
    for (const s of hub.spokes) {
      out += `<circle cx="${s.x.toFixed(1)}" cy="${s.y.toFixed(1)}" r="5.4" fill="${hub.colour}"/>`;
    }
  }

  for (const hub of placedHubs) {
    out += `<circle cx="${hub.x.toFixed(1)}" cy="${hub.y.toFixed(1)}" r="${hub.r.toFixed(1)}" fill="${hub.colour}"/>`;
    out += `<circle cx="${hub.x.toFixed(1)}" cy="${hub.y.toFixed(1)}" r="${(hub.r * 0.62).toFixed(1)}" fill="none" stroke="${SB.page}" stroke-width="1.4" stroke-opacity="0.35"/>`;
    const nameSize = hub.sites.length >= 10 ? 32 : 26;
    const countSize = hub.sites.length >= 10 ? 24 : 20;
    const nameY = hub.y + hub.ringR + 26;
    const countY = nameY + 26;
    const halo = `stroke="${SB.page}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"`;
    out += `<text x="${hub.x.toFixed(1)}" y="${nameY.toFixed(1)}" text-anchor="middle" font-family="Newsreader, Georgia, serif" font-size="${nameSize}" font-weight="500" fill="${SB.oak}" ${halo}>${esc(hub.short)}</text>`;
    out += `<text x="${hub.x.toFixed(1)}" y="${countY.toFixed(1)}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="${countSize}" fill="${hub.colour}" ${halo}>${hub.sites.length}</text>`;
  }

  for (const hub of placedHubs) {
    for (const s of hub.spokes) {
      if (!s.label) continue;
      const halo = `stroke="${SB.page}" stroke-width="8" stroke-linejoin="round" paint-order="stroke"`;
      out += `<text x="${s.labelX.toFixed(1)}" y="${s.labelY.toFixed(1)}" text-anchor="middle" font-family="'Instrument Sans', system-ui, sans-serif" font-size="15" fill="${SB.oak}" ${halo}>${esc(s.label)}</text>`;
    }
  }

  return out;
}

function esc(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function pct(share) {
  return Math.round(share * 100);
}

function renderHtml(data, layout) {
  const share = pct(data.independentShare);
  const svg = svgNetwork(layout);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Who Runs the UK's Stills — LinkedIn card</title>
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
    padding: 64px 72px 56px;
    font-family: 'Instrument Sans', system-ui, sans-serif;
    position: relative;
  }
  .sb { position: absolute; top: 52px; right: 64px; width: 72px; height: 72px; }
  .eyebrow {
    font-family: 'JetBrains Mono', monospace; font-size: 17px;
    text-transform: uppercase; letter-spacing: 0.24em; color: ${SB.stone};
    max-width: 42ch;
  }
  .network { position: absolute; inset: 0; pointer-events: none; }
  .stat {
    position: absolute; right: 64px; bottom: 168px; text-align: right;
    width: 420px;
  }
  .stat .num {
    font-family: Newsreader, Georgia, serif; font-weight: 400;
    font-size: 92px; line-height: 0.92; letter-spacing: -0.02em; color: ${SB.oak};
  }
  .stat .num i {
    display: block; font-style: italic; font-weight: 300;
    font-size: 52px; color: ${SB.copper}; margin-top: 2px;
  }
  .stat .line {
    font-size: 22px; line-height: 1.35; color: ${SB.stone}; margin-top: 16px;
  }
  .stat .line + .line { margin-top: 6px; }
  .foot { margin-top: auto; position: relative; z-index: 2; }
  .source { font-size: 16px; color: ${SB.stone}; margin-bottom: 12px; }
  .footer {
    display: flex; justify-content: space-between; align-items: baseline;
    border-top: 1px solid ${SB.rule}; padding-top: 22px;
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
    <div class="eyebrow">Who Runs the UK's Stills · ${esc(data.edition)}</div>
    <svg class="network" viewBox="0 0 1200 1200" width="1200" height="1200" role="img" aria-label="Network of UK distillery operating groups.">${svg}</svg>
    <div class="stat">
      <div class="num">${share}% <i>independent</i></div>
      <div class="line">${data.total} distilleries tied to a registered company at high confidence.</div>
      <div class="line">Eight groups run ${data.hubSiteCount}. Diageo runs ${data.diageoCount}.</div>
    </div>
    <div class="foot">
      <div class="source">Companies House and Wikidata, matched to the Distillery Map</div>
      <div class="footer">
        <span><span class="wm">Still<i>bound</i></span><span class="tagline">Liquid intelligence</span></span>
        <span class="site">${esc(data.sourceSlug)}</span>
      </div>
    </div>
  </div>
</body>
</html>
`;
}

function renderSummary(data) {
  const share = pct(data.independentShare);
  const lines = [];
  lines.push(`# Ownership card — computed numbers`);
  lines.push("");
  lines.push(`Edition: ${data.edition}. Built from \`data/company-crosswalk/company-crosswalk.csv\` (UK rows, confidence \`high\` or \`verified\`) and \`data/ownership/groups.json\`. Rebuild after pulling the crosswalk branch; do not copy these figures by hand onto the card.`);
  lines.push("");
  lines.push(`## Claim on the card`);
  lines.push("");
  lines.push(`- **${share}% independent** (${data.independentCount} / ${data.total})`);
  lines.push(`- **${data.total}** distilleries tied to a registered company at high confidence`);
  lines.push(`- **Eight groups run ${data.hubSiteCount}.** **Diageo runs ${data.diageoCount}.**`);
  lines.push("");
  lines.push(`Independent means the operating company is not in the group table, or the mapped group resolves to a single site. It is a register-company claim, not an ultimate-parent claim.`);
  lines.push("");
  lines.push(`## Top eight operating groups`);
  lines.push("");
  lines.push(`| Group | Sites | Company numbers |`);
  lines.push(`|---|---:|---|`);
  for (const g of data.hubs) {
    lines.push(`| ${g.display} | ${g.sites.length} | ${g.company_numbers.join(", ") || "—"} |`);
  }
  lines.push("");
  for (const g of data.hubs) {
    lines.push(`### ${g.display} (${g.sites.length})`);
    lines.push("");
    lines.push(g.note);
    lines.push("");
    for (const s of [...g.sites].sort((a, b) => a.name.localeCompare(b.name))) {
      lines.push(`- ${s.name} — ${s.company_name} (${s.company_number})`);
    }
    lines.push("");
  }
  if (data.lesserGroups.length) {
    lines.push(`## Mapped groups below the top eight`);
    lines.push("");
    lines.push("These are groups, not independents. They are not hubs on the card.");
    lines.push("");
    for (const g of data.lesserGroups) {
      lines.push(`- **${g.display}** (${g.sites.length}): ${g.sites.map((s) => s.name).join("; ")}`);
    }
    lines.push("");
  }
  lines.push(`## Companies left as Independent with more than one site`);
  lines.push("");
  if (!data.multiSiteIndependents.length) {
    lines.push("None. Every multi-site company in the high-confidence UK set is in the group table.");
  } else {
    lines.push("These are the ones a human should look at. They were not mapped because the group table does not guess ownership it cannot state from the register row.");
    lines.push("");
    for (const c of data.multiSiteIndependents) {
      lines.push(`- **${c.company_name}** (${c.company_number}) — ${c.count} sites: ${c.sites.join("; ")}`);
    }
  }
  lines.push("");
  lines.push(`## Independent count`);
  lines.push("");
  lines.push(`${data.independentCount} of ${data.total} high-confidence UK rows.`);
  lines.push("");
  return lines.join("\n");
}

function serveDir(dir) {
  const mime = {
    ".html": "text/html; charset=utf-8",
    ".png": "image/png",
    ".css": "text/css",
    ".js": "text/javascript",
    ".svg": "image/svg+xml",
  };
  const server = createServer((req, res) => {
    const url = new URL(req.url, "http://127.0.0.1");
    const name = url.pathname === "/" ? "ownership-card.html" : url.pathname.replace(/^\//, "");
    const file = join(dir, name);
    if (!file.startsWith(dir) || !existsSync(file)) {
      res.writeHead(404);
      res.end("not found");
      return;
    }
    res.writeHead(200, { "content-type": mime[extname(file)] || "application/octet-stream" });
    res.end(readFileSync(file));
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

function exportPng() {
  const chrome = findChrome();
  if (!chrome) {
    console.warn("no Chrome found; skipped PNG export");
    return Promise.resolve(false);
  }
  return serveDir(OUT_DIR).then(
    (server) =>
      new Promise((resolve, reject) => {
        const { port } = server.address();
        const profile = join("/tmp", `ownership-card-chrome-${process.pid}`);
        mkdirSync(profile, { recursive: true });
        const child = spawn(
          chrome,
          [
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            `--user-data-dir=${profile}`,
            "--force-device-scale-factor=2",
            "--window-size=1200,1200",
            `--screenshot=${PNG_OUT}`,
            `http://127.0.0.1:${port}/ownership-card.html?full`,
          ],
          { stdio: "inherit" }
        );
        const timer = setTimeout(() => {
          child.kill("SIGKILL");
          server.close();
          reject(new Error("Chrome screenshot timed out"));
        }, 20000);
        child.on("exit", () => {
          clearTimeout(timer);
          server.close();
          if (existsSync(PNG_OUT)) {
            console.log(`wrote ${PNG_OUT}`);
            resolve(true);
          } else {
            reject(new Error("Chrome exited without writing the PNG"));
          }
        });
        child.on("error", (err) => {
          clearTimeout(timer);
          server.close();
          reject(err);
        });
      })
  );
}

async function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  const groupTable = JSON.parse(readFileSync(GROUPS_PATH, "utf8")).groups;
  const rows = loadUkRows();
  const data = compute(rows, groupTable);
  const layout = placeLayout(data);
  writeFileSync(HTML_OUT, renderHtml(data, layout));
  writeFileSync(SUMMARY_OUT, renderSummary(data));
  console.log(`wrote ${HTML_OUT}`);
  console.log(`wrote ${SUMMARY_OUT}`);
  console.log(
    `${pct(data.independentShare)}% independent · ${data.total} high-confidence · eight groups ${data.hubSiteCount} · Diageo ${data.diageoCount}`
  );
  await exportPng();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
