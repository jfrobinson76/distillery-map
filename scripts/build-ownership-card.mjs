/**
 * Build both ownership slides on the same Scotch-whisky universe.
 *
 *   A  docs/social/ownership/ownership-card.html     (+ 2400 PNG)  — web
 *   B  docs/social/ownership/ownership-map.html      (+ 2400 PNG)  — map (lead)
 *
 *   npm run ownership-card
 *   npm run ownership-map
 *
 * Groups by psc-parents.csv ultimate controller. groups.json is display
 * names and colours only. Does not write data/company-crosswalk/.
 */
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { rmSync, statSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, "..");

const SOURCE_SLUG = "stillbound.ai/research/ownership";
const EDITION = "September 2026";
const TITLE = "Who Runs Scotland's Stills";

const CROSSWALK = join(ROOT, "data/company-crosswalk/company-crosswalk.csv");
const PSC_PATH = join(ROOT, "data/ownership/psc-parents.csv");
const GROUPS_PATH = join(ROOT, "data/ownership/groups.json");
const GEOJSON = join(ROOT, "public/data/distilleries.geojson");
const OUTLINE_PATH = join(ROOT, "data/ownership/scotland-outline.geojson");
const CATEGORIES_DIR = join(ROOT, "data/categories");
const OUT_DIR = join(ROOT, "docs/social/ownership");

const CARD_HTML = join(OUT_DIR, "ownership-card.html");
const CARD_PNG = join(OUT_DIR, "ownership-card-2400.png");
const MAP_HTML = join(OUT_DIR, "ownership-map.html");
const MAP_PNG = join(OUT_DIR, "ownership-map-2400.png");
const SUMMARY_OUT = join(OUT_DIR, "ownership-summary.md");

const SB = {
  page: "#F7EEDA",
  copper: "#9C4E20",
  gold: "#D39A3D",
  amber: "#C8852E",
  ember: "#6E2F14",
  oak: "#2A1F17",
  stone: "#7F7262",
  rule: "#CDB994",
};

const CONFIDENCE_OK = new Set(["high", "verified"]);
const SITE_LABELS = ["Talisker", "Lagavulin", "Caol Ila", "Cardhu", "Glenfiddich"];
const GROUP_FILL_NAMES = [
  "auchroisk",
  "kininvie",
  "dufftown",
  "allt-a-bhainne",
  "allt a bhainne",
  "lagg",
  "glen turner",
];
const SHETLAND_LAT = 59.5; // drop Shetland; Orkney tops out at ~59.4N

const CHROME_CANDIDATES = [
  process.env.CHROME,
  "/opt/google/chrome/chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
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

function esc(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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

function loadCategories() {
  const out = new Map();
  if (!existsSync(CATEGORIES_DIR)) return out;
  for (const name of readdirSync(CATEGORIES_DIR)) {
    if (!name.startsWith("out_") || !name.endsWith(".json")) continue;
    let data;
    try {
      data = JSON.parse(readFileSync(join(CATEGORIES_DIR, name), "utf8"));
    } catch {
      continue;
    }
    const items = [];
    if (Array.isArray(data)) items.push(...data);
    else if (data && typeof data === "object") {
      for (const [k, v] of Object.entries(data)) {
        if (v && typeof v === "object") items.push({ slug: k, ...v });
      }
    }
    for (const row of items) {
      const slug = row.slug;
      if (!slug || !row.spirits) continue;
      const prev = out.get(slug);
      if (!prev) out.set(slug, row);
    }
  }
  return out;
}

function spiritsOf(row) {
  const s = row?.spirits;
  if (Array.isArray(s)) return s.map((x) => String(x).toLowerCase());
  if (typeof s === "string") return [s.toLowerCase()];
  return [];
}

function descWhisky(desc) {
  const t = (desc || "").toLowerCase();
  return t.includes("malt") || t.includes("grain") || t.includes("whisk");
}

function catWhisky(cat) {
  return spiritsOf(cat).some((s) => s.includes("whisk"));
}

function isExcludedName(name) {
  const n = (name || "").toLowerCase();
  if (n.includes("johnnie walker") && (n.includes("prince") || n.includes("experience"))) return true;
  if (n.includes("distillers market")) return true;
  if (n.includes("gordon") && n.includes("macphail")) return true;
  if (n.includes("whisky lounge")) return true;
  if (/\bgin\b/.test(n)) return true;
  return false;
}

function matchDisplay(ultNumber, ultName, table) {
  const num = (ultNumber || "").trim();
  const name = normName(ultName);
  for (const g of table.groups) {
    if (num && (g.match_numbers || []).includes(num)) return g;
    if (name && (g.match_names || []).map(normName).includes(name)) return g;
  }
  return null;
}

function controllerKey(ultNumber, ultName, display) {
  if (display) return `g:${display.id}`;
  if ((ultNumber || "").trim()) return `n:${ultNumber.trim()}`;
  return `name:${normName(ultName)}`;
}


// ---------------------------------------------------------------------------
// Audited universe (19 Sep 2026). An independent audit (docs/research/ownership-audit-2026-09.md)
// replaced the category-verdict universe with the SWA's September 2026 list of operating
// Scotch whisky distilleries and resolved every group by an outside source. When the audit
// file is present the build uses it and ignores the category filter. Scope: SWA list
// (155 units; Loch Lomond's malt and grain plants count as two on one site).
// ---------------------------------------------------------------------------
const AUDIT_UNIVERSE = join(ROOT, "data", "ownership", "scotch-universe-audit-2026-09.csv");
const AUDIT_EXTRA_COLOURS = ["#7A5C3A", "#A8703A", "#8B5A2B", "#5E4A3A", "#B58A4A", "#6B6255", "#9A6B47", "#4E3B2E"];

function loadAuditedUniverse(table) {
  if (!existsSync(AUDIT_UNIVERSE)) return null;
  const geo = JSON.parse(readFileSync(GEOJSON, "utf8"));
  const bySlug = new Map();
  for (const f of geo.features) {
    const p = f.properties || {};
    const [lon, lat] = f.geometry?.coordinates || [];
    if (p.slug && lon != null) bySlug.set(p.slug, { name: p.name || p.slug, lon, lat, desc: p.description || "" });
  }
  const rows = parseCsv(readFileSync(AUDIT_UNIVERSE, "utf8"));
  const inScope = (r) => r.status.startsWith("operating (SWA)") || r.status.startsWith("operating list");
  const displayFor = (name, i) => {
    const hit = (table.groups || []).find((g) =>
      [g.display, g.short, ...(g.match_names || [])].some((n) => n && n.toLowerCase() === name.toLowerCase())
      || (name.startsWith("CVH") && g.id === "distell") || (name === "Isle of Arran" && g.id === "arran"));
    if (hit) return hit;
    return { id: name.toLowerCase().replace(/[^a-z0-9]+/g, "-"), display: name, short: name,
             colour: AUDIT_EXTRA_COLOURS[i % AUDIT_EXTRA_COLOURS.length], match_numbers: [], match_names: [name],
             note: "Group named by the September 2026 audit; see docs/research/ownership-audit-2026-09.md" };
  };
  const included = [];
  const jv = [];
  let units = 0;
  let extra = 0;
  const seenGroups = new Map();
  for (const r of rows) {
    if (!inScope(r)) continue;
    const u = Number(r.units || 0);
    if (!u) continue;
    const g = bySlug.get(r.slug);
    if (!g) continue;
    units += u;
    const group = (r.group || "residual").trim();
    const isJV = group === "JV";
    const matched = group !== "residual" && !isJV;
    let display = null;
    if (matched) {
      if (!seenGroups.has(group)) seenGroups.set(group, displayFor(group, extra++));
      display = seenGroups.get(group);
    }
    const site = {
      slug: r.slug, name: g.name, lon: g.lon, lat: g.lat, desc: g.desc, reason: "audit",
      matched, company_name: "", company_number: "", confidence: "audit", relation: "",
      ultNumber: "", ultName: group, display, key: matched ? `audit:${group}` : `unmatched:${r.slug}`,
      pscSource: r.source || "", stopped_because: "", units: u,
    };
    if (isJV) jv.push(site); else included.push(site);
  }
  return { included, jv, units, fillNames: [] };
}

function loadUniverse(table) {
  const geo = JSON.parse(readFileSync(GEOJSON, "utf8"));
  const cats = loadCategories();
  const cwRows = parseCsv(readFileSync(CROSSWALK, "utf8"));
  const cw = new Map();
  for (const r of cwRows) {
    if (r.registry !== "companies-house") continue;
    if (!CONFIDENCE_OK.has(r.confidence)) continue;
    cw.set(r.slug, r);
  }
  const psc = new Map();
  for (const r of parseCsv(readFileSync(PSC_PATH, "utf8"))) {
    psc.set((r.company_number || "").trim(), r);
  }

  const scotland = [];
  for (const f of geo.features) {
    const p = f.properties || {};
    if ((p.region || "").toLowerCase() !== "scotland") continue;
    const [lon, lat] = f.geometry?.coordinates || [];
    if (lon == null || lat == null || lat > SHETLAND_LAT) continue;
    const name = p.name || "";
    if (isExcludedName(name)) continue;
    const slug = p.slug;
    const desc = p.description || "";
    const cat = cats.get(slug);
    scotland.push({
      slug,
      name,
      desc,
      lon,
      lat,
      signal: descWhisky(desc) || catWhisky(cat),
      empty: !String(desc).trim(),
      cw: cw.get(slug) || null,
      cat,
    });
  }

  const resolve = (site) => {
    const row = site.cw;
    if (!row) return null;
    const num = (row.company_number || "").trim();
    const p = psc.get(num);
    const ultNumber = (p?.ultimate_number || num || "").trim();
    const ultName = (p?.ultimate_name || row.company_name || "").trim();
    const display = matchDisplay(ultNumber, ultName, table);
    return {
      ultNumber,
      ultName,
      display,
      key: controllerKey(ultNumber, ultName, display),
      company_name: row.company_name,
      company_number: num,
      confidence: row.confidence,
      relation: row.relation,
      psc: p || null,
    };
  };

  const signalKeys = new Set();
  for (const site of scotland) {
    if (!site.signal) continue;
    const c = resolve(site);
    if (c) signalKeys.add(c.key);
  }

  const included = [];
  const fillNames = [];
  for (const site of scotland) {
    let reason = null;
    if (site.signal) reason = "signal";
    else if (site.empty && site.cw) {
      const c = resolve(site);
      const named = GROUP_FILL_NAMES.some((n) => site.name.toLowerCase().includes(n));
      if (c && signalKeys.has(c.key) && named) {
        reason = "group-fill";
        fillNames.push(site.name);
      }
    }
    if (!reason) continue;
    const c = resolve(site);
    included.push({
      slug: site.slug,
      name: site.name,
      lon: site.lon,
      lat: site.lat,
      desc: site.desc,
      reason,
      matched: Boolean(site.cw),
      company_name: c?.company_name || "",
      company_number: c?.company_number || "",
      confidence: c?.confidence || "",
      relation: c?.relation || "",
      ultNumber: c?.ultNumber || "",
      ultName: c?.ultName || "",
      display: c?.display || null,
      key: c?.key || `unmatched:${site.slug}`,
      pscSource: c?.psc?.source || "",
      stopped_because: c?.psc?.stopped_because || "",
    });
  }

  return { included, fillNames };
}

function compute(included, table) {
  const buckets = new Map();
  const unmatched = [];
  for (const site of included) {
    if (!site.matched) {
      unmatched.push(site);
      continue;
    }
    if (!buckets.has(site.key)) {
      buckets.set(site.key, {
        key: site.key,
        display: site.display,
        ultNumber: site.ultNumber,
        ultName: site.ultName,
        sites: [],
      });
    }
    buckets.get(site.key).sites.push(site);
  }

  const groups = [];
  const independents = [...unmatched];
  for (const b of buckets.values()) {
    if (b.sites.length >= 2) {
      const g = b.display;
      groups.push({
        id: g?.id || b.key,
        display: g?.display || b.ultName,
        short: g?.short || g?.display || b.ultName,
        colour: g?.colour || SB.copper,
        note: g?.note || "Controller with more than one Scotch site; no display mapping.",
        match_numbers: g?.match_numbers || [b.ultNumber].filter(Boolean),
        ultNumber: b.ultNumber,
        ultName: b.ultName,
        sites: b.sites,
      });
    } else {
      independents.push(b.sites[0]);
    }
  }

  const priority = new Map((table.hub_priority || []).map((id, i) => [id, i]));
  groups.sort((a, b) => {
    if (b.sites.length !== a.sites.length) return b.sites.length - a.sites.length;
    const pa = priority.has(a.id) ? priority.get(a.id) : 50;
    const pb = priority.has(b.id) ? priority.get(b.id) : 50;
    if (pa !== pb) return pa - pb;
    return a.display.localeCompare(b.display);
  });

  const hubs = groups.slice(0, 8);
  const lesserGroups = groups.slice(8);
  const diageo = groups.find((g) => g.id === "diageo");
  const groupRun = groups.reduce((n, g) => n + g.sites.length, 0);

  const indByCo = new Map();
  for (const row of independents) {
    if (!row.matched) continue;
    const key = `${row.company_number}||${normName(row.company_name)}`;
    if (!indByCo.has(key)) {
      indByCo.set(key, { company_name: row.company_name, company_number: row.company_number, sites: [] });
    }
    indByCo.get(key).sites.push(row.name);
  }
  const multiSiteIndependents = [...indByCo.values()]
    .filter((c) => c.sites.length > 1)
    .map((c) => ({ ...c, count: c.sites.length }))
    .sort((a, b) => b.count - a.count || a.company_name.localeCompare(b.company_name));

  const fill = included.filter((s) => s.reason === "group-fill");

  return {
    total: included.length,
    matched: included.filter((s) => s.matched).length,
    unmatched,
    independentCount: independents.length,
    groupRun,
    groupCount: groups.length,
    diageoCount: diageo?.sites.length ?? 0,
    hubs,
    lesserGroups,
    groups,
    independents,
    multiSiteIndependents,
    fill,
    lesserColour: table.lesser_colour || "#8A735A",
    edition: EDITION,
    sourceSlug: SOURCE_SLUG,
    title: TITLE,
  };
}

function wordNumber(n) {
  const words = {
    8: "Eight",
    12: "Twelve",
    13: "Thirteen",
    14: "Fourteen",
    15: "Fifteen",
    16: "Sixteen",
  };
  return words[n] || String(n);
}

function claimLines(data) {
  const pctGroup = Math.round((data.groupRun / data.total) * 100);
  const pctIndep = Math.round((data.independentCount / data.total) * 100);
  const pctDiageo = Math.round((data.diageoCount / data.total) * 100);
  const twoThirds = pctGroup >= 62 && pctGroup <= 71;
  return {
    headline: twoThirds ? "Two-thirds group-run." : `${pctGroup}% group-run.`,
    body: data.universe
      ? `${data.total} operating Scotch whisky distilleries.`
      : `${data.total} Scotch whisky distilleries.`,
    groups: `${data.groupCount} groups run ${data.groupRun} of them (${pctGroup}%).`,
    indep: `At most ${data.independentCount} are independent (${pctIndep}%).`,
    compact: `${data.total} operating distilleries. ${data.groupCount} groups run ${data.groupRun}. Diageo ${data.diageoCount}.`,
    diageo: `Diageo alone runs ${data.diageoCount} (${pctDiageo}%).`,
    caveat: "By number of distilleries, not by litres.",
  };
}

function hubRadius(count) {
  return 13 + 6.4 * Math.sqrt(count);
}

function ringRadius(hubR, n) {
  return Math.max(hubR + 24, (15.5 * n) / (2 * Math.PI));
}

function clusterRadius(count) {
  return ringRadius(hubRadius(count), count) + 10;
}

function placeWeb(data) {
  const box = { x: 40, y: 150, w: 1120, h: 740 };
  const reserved = { x: 690, y: 730, w: 480, h: 360 };
  const rng = mulberry32(20260918);
  const SLOTS = [
    [280, 390],
    [520, 580],
    [500, 240],
    [860, 540],
    [820, 280],
    [640, 440],
    [1000, 400],
    [700, 165],
  ];

  const placedHubs = data.hubs.map((hub, i) => {
    const count = hub.sites.length;
    const r = hubRadius(count);
    const cR = clusterRadius(count);
    const slot = SLOTS[i] || [box.x + 120 + i * 90, box.y + 200];
    const [x, y] = slot;
    const ringR = ringRadius(r, count);
    const gap = 0.95;
    const span = Math.PI * 2 - gap;
    const startAng = Math.PI / 2 + gap / 2;
    const sites = [...hub.sites].sort((a, b) => a.name.localeCompare(b.name));
    const spokes = sites.map((s, k) => {
      const ang = startAng + (k * span) / count;
      return { ...s, x: x + Math.cos(ang) * ringR, y: y + Math.sin(ang) * ringR, ang, label: null };
    });
    return { ...hub, x, y, r, cR, ringR, colour: hub.colour, spokes };
  });

  const obstacles = placedHubs.map((h) => ({ x: h.x, y: h.y, r: h.cR + 16 }));
  const field = [
    ...data.independents.map((s) => ({ ...s, colour: SB.stone, alpha: 0.6 })),
    ...data.lesserGroups.flatMap((g) => g.sites.map((s) => ({ ...s, colour: data.lesserColour, alpha: 0.85 }))),
  ];
  const fieldPts = [];
  let attempt = 0;
  while (fieldPts.length < field.length && attempt < field.length * 240) {
    attempt += 1;
    const x = box.x + 16 + rng() * (box.w - 32);
    const y = box.y + 16 + rng() * (box.h - 24);
    if (x > reserved.x && y > reserved.y - 40) continue;
    if (obstacles.some((o) => Math.hypot(x - o.x, y - o.y) < o.r)) continue;
    if (fieldPts.some((p) => Math.hypot(x - p.x, y - p.y) < 8.5)) continue;
    fieldPts.push({ x, y });
  }

  const fieldPlaced = field.map((s, i) => ({
    ...s,
    x: fieldPts[i]?.x ?? box.x + 20 + (i % 40) * 12,
    y: fieldPts[i]?.y ?? box.y + 20 + Math.floor(i / 40) * 12,
  }));

  return { placedHubs, fieldPlaced };
}

function svgWeb(layout) {
  const { placedHubs, fieldPlaced } = layout;
  let out = "";
  for (const n of fieldPlaced) {
    out += `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="3.2" fill="${n.colour}" fill-opacity="${n.alpha}"/>`;
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
    const nameSize = hub.sites.length >= 10 ? 30 : 24;
    const countSize = hub.sites.length >= 10 ? 22 : 18;
    const nameY = hub.y + hub.ringR + 24;
    const countY = nameY + 24;
    const halo = `stroke="${SB.page}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"`;
    out += `<text x="${hub.x.toFixed(1)}" y="${nameY.toFixed(1)}" text-anchor="middle" font-family="Newsreader, Georgia, serif" font-size="${nameSize}" font-weight="500" fill="${SB.oak}" ${halo}>${esc(hub.short)}</text>`;
    out += `<text x="${hub.x.toFixed(1)}" y="${countY.toFixed(1)}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="${countSize}" fill="${hub.colour}" ${halo}>${hub.sites.length}</text>`;
  }
  return out;
}

function flattenRings(geom) {
  const rings = [];
  const walk = (coords, depth) => {
    if (!coords?.length) return;
    if (typeof coords[0][0] === "number") rings.push(coords);
    else coords.forEach((c) => walk(c, depth + 1));
  };
  walk(geom.coordinates, 0);
  return rings;
}

function pointInRing(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0];
    const yi = ring[i][1];
    const xj = ring[j][0];
    const yj = ring[j][1];
    const intersect = yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi + 0.0) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

function pointOnLand(lon, lat, rings) {
  return rings.some((ring) => pointInRing(lon, lat, ring));
}

// Spherical transverse Mercator centred on the Highlands. Albers was
// stretching the north–south mass east–west; this is the map people know.
function rawProject(lon, lat) {
  const rad = (d) => (d * Math.PI) / 180;
  const φ = rad(lat);
  const λ = rad(lon);
  const φ0 = rad(57.0);
  const λ0 = rad(-4.2);
  const B = Math.cos(φ) * Math.sin(λ - λ0);
  const x = 0.5 * Math.log((1 + B) / (1 - B));
  const y = Math.atan(Math.tan(φ) / Math.cos(λ - λ0)) - φ0;
  return [x, y];
}

function fitProjection(points, box, align = "center") {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const [x, y] of points) {
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  }
  const sx = box.w / (maxX - minX);
  const sy = box.h / (maxY - minY);
  const s = Math.min(sx, sy);
  const ox = align === "topleft" ? box.x : box.x + (box.w - (maxX - minX) * s) / 2;
  const oy = align === "topleft" ? box.y : box.y + (box.h - (maxY - minY) * s) / 2;
  return (lon, lat) => {
    const [x, y] = rawProject(lon, lat);
    return [ox + (x - minX) * s, oy + (maxY - y) * s];
  };
}

function mstEdges(sites) {
  const n = sites.length;
  if (n < 2) return [];
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = (i) => {
    while (parent[i] !== i) {
      parent[i] = parent[parent[i]];
      i = parent[i];
    }
    return i;
  };
  const pairs = [];
  for (let i = 0; i < n; i += 1) {
    for (let j = i + 1; j < n; j += 1) {
      pairs.push({
        a: i,
        b: j,
        d: Math.hypot(sites[i].x - sites[j].x, sites[i].y - sites[j].y),
      });
    }
  }
  pairs.sort((p, q) => p.d - q.d);
  const edges = [];
  for (const p of pairs) {
    const ia = find(p.a);
    const ib = find(p.b);
    if (ia === ib) continue;
    parent[ia] = ib;
    edges.push([sites[p.a], sites[p.b]]);
    if (edges.length === n - 1) break;
  }
  return edges;
}

function labelKey(name) {
  const n = name.toLowerCase();
  return SITE_LABELS.find((lab) => n.includes(lab.toLowerCase())) || null;
}

function boxesOverlap(a, b, pad = 6) {
  return !(a.x + a.w + pad < b.x || b.x + b.w + pad < a.x || a.y + a.h + pad < b.y || b.y + b.h + pad < a.y);
}

function placeMap(data, outline) {
  // Left rail + masthead + footer + the number. Map fills what remains.
  // St Kilda (west of 8°W) is dropped from the fit so the mainland can grow.
  // Fixed grid on the 1200 frame (2400 at export), set 19 Sep 2026 after two passes of
  // relative instructions went wrong: rail x 48-300; map box x 340-1150, y 110-830, map
  // centred in it; headline block sits below y 850 on the right. Nothing but the map,
  // sites, webs and five labels may be drawn inside the map box.
  const box = { x: 330, y: 60, w: 840, h: 1020 };
  const reserved = { x: 0, y: 0, w: 0, h: 0 };
  const rings = flattenRings(outline.geometry).filter((ring) => {
    const lons = ring.map((p) => p[0]);
    const lats = ring.map((p) => p[1]);
    if (Math.min(...lats) > SHETLAND_LAT) return false;
    if (Math.max(...lons) < -8.0) return false;
    return true;
  });
  const projPts = [];
  for (const ring of rings) {
    for (const [lon, lat] of ring) {
      if (lat > SHETLAND_LAT) continue;
      projPts.push(rawProject(lon, lat));
    }
  }
  const project = fitProjection(projPts, box, "center");

  const outlinePaths = rings
    .map((ring) => {
      const pts = ring.map(([lon, lat]) => project(lon, lat));
      return pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + "Z";
    });

  const groups = data.groups.map((g) => {
    const sites = g.sites.map((s) => {
      const [x, y] = project(s.lon, s.lat);
      return { ...s, x, y, label: labelKey(s.name) };
    });
    return { ...g, sites, edges: mstEdges(sites) };
  });

  const independents = data.independents.map((s) => {
    const [x, y] = project(s.lon, s.lat);
    return { ...s, x, y };
  });

  const collisions = [
    { x: reserved.x, y: reserved.y, w: reserved.w, h: reserved.h },
    { x: 24, y: 36, w: 230, h: 110 },
    { x: 36, y: 150, w: 200, h: 520 },
  ];
  const siteLabels = [];
  const candidates = [];
  for (const g of groups) {
    for (const s of g.sites) {
      if (s.label) candidates.push({ ...s, colour: g.colour });
    }
  }
  candidates.sort((a, b) => SITE_LABELS.indexOf(a.label) - SITE_LABELS.indexOf(b.label));
  for (const s of candidates) {
    const w = s.label.length * 7.4;
    const trials = [
      { x: s.x - w / 2, y: s.y - 22, labelX: s.x, labelY: s.y - 10, anchor: "middle" },
      { x: s.x + 8, y: s.y - 8, labelX: s.x + 8, labelY: s.y + 4, anchor: "start" },
      { x: s.x - w - 8, y: s.y - 8, labelX: s.x - 8, labelY: s.y + 4, anchor: "end" },
    ];
    const hit = trials.find((t) => !collisions.some((c) => boxesOverlap(c, { x: t.x, y: t.y, w, h: 16 }, 4)));
    if (!hit) continue;
    collisions.push({ x: hit.x, y: hit.y, w, h: 16 });
    siteLabels.push({ ...s, ...hit });
  }

  return { outlinePaths, groups, independents, siteLabels: [] };
}

function svgMap(layout) {
  let out = "";
  for (const d of layout.outlinePaths) {
    out += `<path d="${d}" fill="${SB.ember}" fill-opacity="0.04" stroke="${SB.ember}" stroke-width="1.35" stroke-linejoin="round"/>`;
  }

  // Independents are half the story, so they must read: a ring in oak on a paper core,
  // drawn on top of the land and under the group webs.
  for (const n of layout.independents) {
    out += `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="4.4" fill="${SB.page}" stroke="${SB.oak}" stroke-width="1.6" stroke-opacity="0.9"/>`;
  }

  for (const g of layout.groups) {
    for (const [a, b] of g.edges) {
      out += `<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="${g.colour}" stroke-width="1.15" stroke-opacity="0.5"/>`;
    }
  }
  for (const g of layout.groups) {
    for (const s of g.sites) {
      out += `<circle cx="${s.x.toFixed(1)}" cy="${s.y.toFixed(1)}" r="5.2" fill="${g.colour}" stroke="${SB.page}" stroke-width="1.1"/>`;
    }
  }
  for (const s of layout.siteLabels) {
    const halo = `stroke="${SB.page}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"`;
    out += `<text x="${s.labelX.toFixed(1)}" y="${s.labelY.toFixed(1)}" text-anchor="${s.anchor}" font-family="'Instrument Sans', system-ui, sans-serif" font-size="15" fill="${SB.oak}" ${halo}>${esc(s.label)}</text>`;
  }
  return out;
}

function railHtml(data) {
  const rows = data.groups
    .map(
      (g) =>
        `<div class="rail-row" style="color:${g.colour}"><span>${esc(g.short)}</span><span class="n">${g.sites.length}</span></div>`
    )
    .join("");
  const indep = `<div class="rail-row rail-indep" style="color:${SB.oak}"><span><svg width="12" height="12" viewBox="0 0 12 12" style="vertical-align:-1px;margin-right:6px"><circle cx="6" cy="6" r="4.2" fill="${SB.page}" stroke="${SB.oak}" stroke-width="1.5"/></svg>Independent</span><span class="n">${data.independentCount}</span></div>`;
  const jv = data.jv && data.jv.length
    ? `<div class="rail-row" style="color:${SB.oak}"><span>Joint venture</span><span class="n">${data.jv.length}</span></div>` : "";
  return `<div class="rail">${rows}${indep}${jv}</div>`;
}

function cardChrome(data, svg, aria, extras = {}) {
  const claim = claimLines(data);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${esc(data.title)} — LinkedIn card</title>
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
    padding: 56px 64px 52px;
    font-family: 'Instrument Sans', system-ui, sans-serif;
    position: relative;
  }
  .sb { position: absolute; top: 48px; right: 56px; width: 72px; height: 72px; }
  .eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px; text-transform: uppercase; color: ${SB.stone};
    line-height: 1.45; max-width: 34em;
  }
  .eyebrow .title { display: block; letter-spacing: 0.06em; font-size: 17px; }
  .eyebrow .ed { display: block; margin-top: 0.35em; letter-spacing: 0.16em; }
  .network { position: absolute; inset: 0; pointer-events: none; }
  .stat {
    position: absolute; right: 56px; bottom: 148px; text-align: right;
    width: 500px;
  }
  .card.map .stat {
    right: auto; left: 48px; bottom: 168px; width: 270px; text-align: left;
  }
  .card.map .stat .num { font-size: 50px; }
  .card.map .stat .line { font-size: 17px; margin-top: 8px; }
  .card.map .stat .caveat { font-size: 14px; margin-top: 8px; }
  .stat .num {
    font-family: Newsreader, Georgia, serif; font-weight: 400;
    font-size: 68px; line-height: 0.96; letter-spacing: -0.02em; color: ${SB.oak};
  }
  .stat .line {
    font-family: Newsreader, Georgia, serif; font-weight: 400;
    font-size: 23px; line-height: 1.35; color: ${SB.oak}; margin-top: 12px;
  }
  .stat .line + .line { margin-top: 4px; }
  .stat .caveat {
    font-size: 20px; line-height: 1.35; color: ${SB.stone}; margin-top: 12px;
  }
  .foot { margin-top: auto; position: relative; z-index: 2; }
  .source { font-size: 16px; color: ${SB.stone}; margin-bottom: 12px; }
  .footer {
    display: flex; justify-content: space-between; align-items: baseline;
    border-top: 1px solid ${SB.rule}; padding-top: 20px;
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
  .rail {
    position: absolute; left: 48px; top: 160px; width: 240px; z-index: 2;
  }
  .rail-row {
    display: flex; justify-content: space-between; align-items: baseline;
    font-size: 15px; font-weight: 500; line-height: 1.45;
  }
  .rail-indep { margin-top: 10px; padding-top: 8px; border-top: 1px solid ${SB.rule}; }
  .rail-row .n {
    font-family: 'JetBrains Mono', monospace; font-size: 15px; margin-left: 14px;
  }
</style>
</head>
<body>
  <script>if (location.search.includes("full")) document.body.classList.add("full");</script>
  <div class="card${extras.cardClass ? ` ${extras.cardClass}` : ""}">
    <svg class="sb" viewBox="0 0 100 100"><text x="50.5" y="59" text-anchor="middle" dominant-baseline="central" font-family="Newsreader, Georgia, serif" font-size="84" font-weight="400" letter-spacing="-3" fill="${SB.copper}">S<tspan font-style="italic" font-weight="300" fill="${SB.gold}">b</tspan></text></svg>
    <div class="eyebrow"><span class="title">${esc(data.title)}</span><span class="ed">${esc(data.edition)}</span></div>
    ${extras.rail || ""}
    <svg class="network" viewBox="0 0 1200 1200" width="1200" height="1200" role="img" aria-label="${esc(aria)}">${svg}</svg>
    <div class="stat">
      <div class="num">${esc(claim.headline)}</div>
      ${extras.compact
        ? `<div class="line">${esc(claim.compact)}</div>`
        : `<div class="line">${esc(claim.body)}</div>
      <div class="line">${esc(claim.groups)}</div>
      <div class="line">${esc(claim.indep)}</div>
      <div class="line">${esc(claim.diageo)}</div>`}
      <div class="caveat">${esc(claim.caveat)}</div>
    </div>
    <div class="foot">
      <div class="source">SWA operating list (Sept 2026), Companies House PSC filings, operators' own sites</div>
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

function renderSummary(data, mapLayout) {
  const claim = claimLines(data);
  const lines = [];
  lines.push(`# Ownership card — computed numbers`);
  lines.push("");
  lines.push(
    `Edition: ${data.edition}. Scotch whisky only. Built from \`data/company-crosswalk/company-crosswalk.csv\` (high/verified, Companies House), \`data/ownership/psc-parents.csv\` (ultimate controller), \`data/categories/out_*.json\`, and \`public/data/distilleries.geojson\`. \`groups.json\` is display names and colours only. Rebuild after pulling the crosswalk branch; do not copy these figures by hand onto the card.`
  );
  lines.push("");
  lines.push(`## Claim on both slides`);
  lines.push("");
  lines.push(`- **${claim.headline}**`);
  lines.push(`- ${claim.body} ${claim.groups} ${claim.indep} ${claim.diageo}`);
  lines.push(`- ${claim.caveat}`);
  lines.push("");
  lines.push(`| | |`);
  lines.push(`|---|---:|`);
  lines.push(`| Scotch whisky sites | ${data.total} |`);
  lines.push(`| Matched high/verified | ${data.matched} |`);
  lines.push(`| Unmatched (drawn as independent) | ${data.unmatched.length} |`);
  lines.push(`| Independent (controller has one site, plus unmatched) | ${data.independentCount} |`);
  lines.push(`| Group-run | ${data.groupRun} |`);
  lines.push(`| Groups >1 site | ${data.groupCount} |`);
  lines.push(`| Diageo | ${data.diageoCount} |`);
  lines.push("");
  lines.push(
    `Independent means the ultimate controller in \`psc-parents.csv\` runs exactly one site in this universe. Unmatched Scotch sites are treated as independent dots — they are small, mostly post-2005 plants. Counts, not litres.`
  );
  lines.push("");
  lines.push(`## Universe`);
  lines.push("");
  lines.push(
    `Map region \`scotland\`, excluding Shetland (lat > 59.85), visitor (Johnnie Walker Princes Street), the Gordon & MacPhail bottler, Distillers Market, whisky lounges, and gin-named sites. A site is in if the map description says malt/grain/whisky or the category verdict includes whisky. Empty-description high-confidence sites are added only when their controller already has a whisky-signal site (the group-fill that restores Auchroisk, Dufftown, Allt-A-Bhainne, Kininvie, Lagg, Glen Turner).`
  );
  lines.push("");
  if (data.fill.length) {
    lines.push(`Group-fill sites: ${data.fill.map((s) => s.name).join("; ")}.`);
    lines.push("");
  }
  lines.push(`README on this branch dated the denominator 178 ±5. This rebuild is ${data.total}.`);
  lines.push("");
  lines.push(`## Top eight operating groups (hubs on both slides)`);
  lines.push("");
  lines.push(`| Group | Sites | Ultimate |`);
  lines.push(`|---|---:|---|`);
  for (const g of data.hubs) {
    lines.push(`| ${g.display} | ${g.sites.length} | ${g.ultName}${g.ultNumber ? ` (${g.ultNumber})` : ""} |`);
  }
  lines.push("");
  for (const g of data.hubs) {
    lines.push(`### ${g.display} (${g.sites.length})`);
    lines.push("");
    lines.push(g.note);
    lines.push("");
    for (const s of [...g.sites].sort((a, b) => a.name.localeCompare(b.name))) {
      lines.push(`- ${s.name} — ${s.company_name} (${s.company_number}) → ${s.ultName}`);
    }
    lines.push("");
  }
  if (data.lesserGroups.length) {
    lines.push(`## Mapped groups below the top eight`);
    lines.push("");
    lines.push(
      "These are groups, not independents. On the map they use their own colour and join their sites with the same MST web. They appear in the left rail."
    );
    lines.push("");
    for (const g of data.lesserGroups) {
      lines.push(`- **${g.display}** (${g.sites.length}): ${g.sites.map((s) => s.name).join("; ")}`);
    }
    lines.push("");
  }
  lines.push(`## Map`);
  lines.push("");
  lines.push(
    `No hub discs. Each group's sites stay at real coordinates and are joined by a minimum-spanning tree in the group colour at 50% alpha. Group names and counts sit in a left rail, sorted by count. Projection is a spherical transverse Mercator centred on 4.2°W, 57°N. The map is 12% smaller than the first top-left fit and anchored top-left so the Borders sit above the headline.`
  );
  lines.push("");
  lines.push(`Site labels on the map: ${(mapLayout.siteLabels || []).map((s) => s.label).join(", ") || "none"}.`);
  lines.push("");
  lines.push(`## Companies left as Independent with more than one site`);
  lines.push("");
  if (!data.multiSiteIndependents.length) {
    lines.push("None. Every multi-site controller in the matched Scotch set is a group.");
  } else {
    lines.push("These are the ones a human should look at.");
    lines.push("");
    for (const c of data.multiSiteIndependents) {
      lines.push(`- **${c.company_name}** (${c.company_number}) — ${c.count} sites: ${c.sites.join("; ")}`);
    }
  }
  lines.push("");
  lines.push(`## Unmatched Scotch sites (independent dots)`);
  lines.push("");
  for (const s of [...data.unmatched].sort((a, b) => a.name.localeCompare(b.name))) {
    lines.push(`- ${s.name} (${s.slug})`);
  }
  lines.push("");
  lines.push(`## Human look`);
  lines.push("");
  lines.push(
    `- **Macdonald & Muir / Ardbeg / Glenmorangie.** The corrected PSC file now stops at LVMH. They are their own two-site group, not Diageo.`
  );
  lines.push(
    `- **Newbridge Bond** is a Brown-Forman warehouse row, not a still. It is in the Brown-Forman four because the crosswalk row is high-confidence and the controller already has whisky-signal sites. A human may drop it.`
  );
  lines.push(
    `- **Ian Macleod Distillers Ltd** is a name-match HQ row with an empty description and a whisky category verdict. Same treatment.`
  );
  lines.push(
    `- **Speymalt / Gordon & MacPhail.** Benromach is a matched one-site controller (independent). The Cairn is empty-description and was not group-filled — it is not one of the six named malt restorations. Including it would invent a fifteenth group the README does not carry.`
  );
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
    const name = url.pathname === "/" ? "ownership-map.html" : url.pathname.replace(/^\//, "");
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

function exportOnePng(server, htmlName, pngPath) {
  const chrome = findChrome();
  if (!chrome) {
    console.warn("no Chrome found; skipped PNG export");
    return Promise.resolve(false);
  }
  const { port } = server.address();
  const profile = join("/tmp", `ownership-card-chrome-${process.pid}-${htmlName.replace(/\W/g, "")}`);
  mkdirSync(profile, { recursive: true });
  return new Promise((resolve, reject) => {
    // Remove any previous export first, or the poll below sees the old file and returns
    // before Chrome has written the new one.
    try { rmSync(pngPath, { force: true }); } catch {}
    const child = spawn(
      chrome,
      [
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        `--user-data-dir=${profile}`,
        "--force-device-scale-factor=2",
        "--window-size=1200,1200",
        "--virtual-time-budget=8000",
        `--screenshot=${pngPath}`,
        `http://127.0.0.1:${port}/${htmlName}?full`,
      ],
      { stdio: "inherit", env: { ...process.env, DISPLAY: process.env.DISPLAY || ":1" } }
    );
    // On macOS, headless Chrome writes the PNG and then never exits (CVDisplayLink
    // errors). Poll for a stable file instead of waiting on exit, then kill it.
    let settled = false;
    let lastSize = -1;
    const finish = (ok, err) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      clearInterval(poll);
      try { child.kill("SIGKILL"); } catch {}
      ok ? resolve(true) : reject(err);
    };
    const poll = setInterval(() => {
      if (!existsSync(pngPath)) return;
      const size = statSync(pngPath).size;
      if (size > 0 && size === lastSize) {
        console.log(`wrote ${pngPath}`);
        finish(true);
      }
      lastSize = size;
    }, 700);
    const timer = setTimeout(() => {
      finish(false, new Error(`Chrome screenshot timed out for ${htmlName}`));
    }, 90000);
    child.on("exit", () => {
      if (existsSync(pngPath)) {
        console.log(`wrote ${pngPath}`);
        finish(true);
      } else {
        finish(false, new Error(`Chrome exited without writing ${pngPath}`));
      }
    });
    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

async function exportPngs() {
  const chrome = findChrome();
  if (!chrome) {
    console.warn("no Chrome found; skipped PNG export");
    return;
  }
  const server = await serveDir(OUT_DIR);
  try {
    await exportOnePng(server, "ownership-map.html", MAP_PNG);
    await exportOnePng(server, "ownership-card.html", CARD_PNG);
  } finally {
    server.close();
  }
}

async function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  const table = JSON.parse(readFileSync(GROUPS_PATH, "utf8"));
  const outline = JSON.parse(readFileSync(OUTLINE_PATH, "utf8"));
  const audited = loadAuditedUniverse(table);
  const { included, fillNames } = audited || loadUniverse(table);
  const data = compute(included, table);
  if (audited) {
    // SWA scope: units (Loch Lomond malt + grain = 2), JV counted once and shown separately.
    data.total = audited.units; // JV units are already inside audited.units
    data.jv = audited.jv;
    data.universe = "SWA September 2026 operating list";
    data.independentCount = data.independents.reduce((n, s) => n + (s.units || 1), 0);
    data.groupRun = data.groups.reduce((n, g) => n + g.sites.reduce((m, s) => m + (s.units || 1), 0), 0);
  }
  const web = placeWeb(data);
  const map = placeMap(data, outline);

  writeFileSync(
    CARD_HTML,
    cardChrome(data, svgWeb(web), "Network of Scotch whisky operating groups.")
  );
  writeFileSync(
    MAP_HTML,
    cardChrome(
      data,
      svgMap(map),
      "Map of Scotland with Scotch whisky distilleries by controlling group.",
      { rail: railHtml(data), cardClass: "map", compact: true }
    )
  );
  writeFileSync(SUMMARY_OUT, renderSummary(data, map));

  const claim = claimLines(data);
  console.log(`wrote ${CARD_HTML}`);
  console.log(`wrote ${MAP_HTML}`);
  console.log(`wrote ${SUMMARY_OUT}`);
  console.log(claim.headline, claim.body);
  console.log(`fill: ${fillNames.join("; ") || "none"}`);
  console.log(
    `groups ${data.groupCount} · group-run ${data.groupRun} · independent ${data.independentCount}/${data.total} · unmatched ${data.unmatched.length}`
  );
  for (const g of data.groups) {
    console.log(`  ${String(g.sites.length).padStart(2)}  ${g.display}`);
  }
  await exportPngs();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
