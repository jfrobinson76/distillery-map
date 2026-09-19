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
import { statSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
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
const SITE_LABELS = ["Lagavulin", "Caol Ila", "Talisker", "Cardhu", "Glenfiddich", "Laphroaig"];
const GROUP_FILL_NAMES = [
  "auchroisk",
  "kininvie",
  "dufftown",
  "allt-a-bhainne",
  "allt a bhainne",
  "lagg",
  "glen turner",
];
const SHETLAND_LAT = 59.85;

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
  return {
    headline: "Half independent.",
    body: `${data.total} Scotch whisky distilleries.`,
    groups: `${wordNumber(data.groupCount)} groups run ${data.groupRun}.`,
    diageo: `Diageo runs ${data.diageoCount}, one in five.`,
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

function albers(lon, lat) {
  const rad = (d) => (d * Math.PI) / 180;
  const φ = rad(lat);
  const λ = rad(lon);
  const φ0 = rad(57.05);
  const φ1 = rad(55.15);
  const φ2 = rad(58.7);
  const λ0 = rad(-4.15);
  const n = (Math.sin(φ1) + Math.sin(φ2)) / 2;
  const θ = n * (λ - λ0);
  const C = Math.cos(φ1) ** 2 + 2 * n * Math.sin(φ1);
  const ρ = Math.sqrt(C - 2 * n * Math.sin(φ)) / n;
  const ρ0 = Math.sqrt(C - 2 * n * Math.sin(φ0)) / n;
  return [ρ * Math.sin(θ), ρ0 - ρ * Math.cos(θ)];
}

function fitProjection(points, box) {
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
  const ox = box.x + (box.w - (maxX - minX) * s) / 2;
  const oy = box.y + (box.h - (maxY - minY) * s) / 2;
  return (lon, lat) => {
    const [x, y] = albers(lon, lat);
    return [ox + (x - minX) * s, oy + (maxY - y) * s];
  };
}

function centroidLonLat(sites) {
  const lon = sites.reduce((n, s) => n + s.lon, 0) / sites.length;
  const lat = sites.reduce((n, s) => n + s.lat, 0) / sites.length;
  return [lon, lat];
}

function nudgeOntoLand(lon, lat, sites, rings) {
  if (pointOnLand(lon, lat, rings)) return [lon, lat, false];
  const nearest = [...sites].sort((a, b) => {
    const da = Math.hypot(a.lon - lon, a.lat - lat);
    const db = Math.hypot(b.lon - lon, b.lat - lat);
    return da - db;
  })[0];
  for (let t = 0.15; t <= 1.001; t += 0.05) {
    const x = lon + (nearest.lon - lon) * t;
    const y = lat + (nearest.lat - lat) * t;
    if (pointOnLand(x, y, rings)) return [x, y, true];
  }
  return [nearest.lon, nearest.lat, true];
}

function labelKey(name) {
  const n = name.toLowerCase();
  return SITE_LABELS.find((lab) => n.includes(lab.toLowerCase())) || null;
}

function boxesOverlap(a, b, pad = 6) {
  return !(a.x + a.w + pad < b.x || b.x + b.w + pad < a.x || a.y + a.h + pad < b.y || b.y + b.h + pad < a.y);
}

function separateHubs(hubs) {
  const origin = hubs.map((h) => ({ x: h.x, y: h.y }));
  for (let iter = 0; iter < 80; iter += 1) {
    for (let i = 0; i < hubs.length; i += 1) {
      for (let j = i + 1; j < hubs.length; j += 1) {
        const a = hubs[i];
        const b = hubs[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.hypot(dx, dy) || 0.1;
        const min = a.r + b.r + 52;
        if (dist >= min) continue;
        const push = (min - dist) / 2;
        const ux = dx / dist;
        const uy = dy / dist;
        a.x -= ux * push;
        a.y -= uy * push;
        b.x += ux * push;
        b.y += uy * push;
      }
    }
    for (let i = 0; i < hubs.length; i += 1) {
      const dx = hubs[i].x - origin[i].x;
      const dy = hubs[i].y - origin[i].y;
      const d = Math.hypot(dx, dy);
      const cap = 46;
      if (d > cap) {
        hubs[i].x = origin[i].x + (dx / d) * cap;
        hubs[i].y = origin[i].y + (dy / d) * cap;
      }
    }
  }
}

function placeHubLabel(hub, collisions) {
  const w = Math.max(92, hub.short.length * 11);
  const trials = [
    { x: hub.x - w / 2, y: hub.y + hub.r + 4, anchor: "middle", tx: hub.x, ty: hub.y + hub.r + 18 },
    { x: hub.x - w / 2, y: hub.y - hub.r - 38, anchor: "middle", tx: hub.x, ty: hub.y - hub.r - 8 },
    { x: hub.x + hub.r + 6, y: hub.y - 16, anchor: "start", tx: hub.x + hub.r + 8, ty: hub.y + 4 },
    { x: hub.x - hub.r - 6 - w, y: hub.y - 16, anchor: "end", tx: hub.x - hub.r - 8, ty: hub.y + 4 },
  ];
  for (const t of trials) {
    const box = { x: t.x, y: t.y, w, h: 36 };
    if (collisions.some((c) => boxesOverlap(c, box, 4))) continue;
    collisions.push(box);
    return { ...t, box };
  }
  return null;
}

function placeMap(data, outline) {
  const box = { x: 18, y: 128, w: 1164, h: 820 };
  const reserved = { x: 720, y: 780, w: 450, h: 310 };
  const rings = flattenRings(outline.geometry);
  const projPts = [];
  for (const ring of rings) {
    for (const [lon, lat] of ring) {
      if (lat > SHETLAND_LAT) continue;
      projPts.push(albers(lon, lat));
    }
  }
  const project = fitProjection(projPts, box);

  const outlinePaths = rings
    .filter((ring) => ring.some(([, lat]) => lat <= SHETLAND_LAT))
    .map((ring) => {
      const pts = ring.map(([lon, lat]) => project(lon, lat));
      return pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + "Z";
    });

  const placedHubs = data.hubs.map((hub) => {
    const [rawLon, rawLat] = centroidLonLat(hub.sites);
    const [lon, lat, nudged] = nudgeOntoLand(rawLon, rawLat, hub.sites, rings);
    const [x, y] = project(lon, lat);
    const r = 8 + 3.1 * Math.sqrt(hub.sites.length);
    const spokes = hub.sites.map((s) => {
      const [sx, sy] = project(s.lon, s.lat);
      return { ...s, x: sx, y: sy, label: labelKey(s.name) };
    });
    return {
      ...hub,
      lon,
      lat,
      rawLon,
      rawLat,
      nudged,
      x,
      y,
      r,
      spokes,
    };
  });
  separateHubs(placedHubs);

  const lesserPlaced = data.lesserGroups.map((g) => {
    const sites = g.sites.map((s) => {
      const [x, y] = project(s.lon, s.lat);
      return { ...s, x, y, label: labelKey(s.name) };
    });
    return { ...g, colour: data.lesserColour, sites };
  });

  const independents = data.independents.map((s) => {
    const [x, y] = project(s.lon, s.lat);
    return { ...s, x, y };
  });

  const collisions = [
    { x: reserved.x, y: reserved.y, w: reserved.w, h: reserved.h },
    { x: 24, y: 36, w: 560, h: 100 },
  ];
  const hubLabels = [];
  const unlabeled = [];
  for (const hub of placedHubs) {
    const lab = placeHubLabel(hub, collisions);
    if (lab) hubLabels.push({ hub, ...lab });
    else unlabeled.push(hub);
  }

  const siteLabels = [];
  const candidates = [];
  for (const hub of placedHubs) {
    for (const s of hub.spokes) {
      if (s.label) candidates.push({ ...s, colour: hub.colour });
    }
  }
  for (const g of lesserPlaced) {
    for (const s of g.sites) {
      if (s.label) candidates.push({ ...s, colour: g.colour });
    }
  }
  candidates.sort((a, b) => SITE_LABELS.indexOf(a.label) - SITE_LABELS.indexOf(b.label));
  for (const s of candidates) {
    const w = s.label.length * 7.2;
    const boxL = { x: s.x - w / 2, y: s.y - 22, w, h: 16 };
    if (collisions.some((c) => boxesOverlap(c, boxL))) {
      s.dropped = true;
      continue;
    }
    collisions.push(boxL);
    siteLabels.push({ ...s, labelX: s.x, labelY: s.y - 10 });
  }

  return { outlinePaths, placedHubs, lesserPlaced, independents, siteLabels, hubLabels, unlabeled, reserved };
}

function quadPath(x1, y1, x2, y2, bend) {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const cx = mx - (dy / len) * bend;
  const cy = my + (dx / len) * bend;
  return `M${x1.toFixed(1)},${y1.toFixed(1)} Q${cx.toFixed(1)},${cy.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)}`;
}

function svgMap(layout) {
  let out = "";
  for (const d of layout.outlinePaths) {
    out += `<path d="${d}" fill="${SB.ember}" fill-opacity="0.04" stroke="${SB.ember}" stroke-width="1.35" stroke-linejoin="round"/>`;
  }

  for (const n of layout.independents) {
    out += `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="2.7" fill="${SB.stone}" fill-opacity="0.6"/>`;
  }

  for (const g of layout.lesserPlaced) {
    if (g.sites.length >= 2) {
      for (let i = 0; i < g.sites.length - 1; i += 1) {
        const a = g.sites[i];
        const b = g.sites[i + 1];
        out += `<path d="${quadPath(a.x, a.y, b.x, b.y, 10)}" fill="none" stroke="${g.colour}" stroke-width="1.2" stroke-opacity="0.45"/>`;
      }
    }
    for (const s of g.sites) {
      out += `<circle cx="${s.x.toFixed(1)}" cy="${s.y.toFixed(1)}" r="4.2" fill="${g.colour}"/>`;
    }
  }

  for (const hub of layout.placedHubs) {
    hub.spokes.forEach((s, i) => {
      const bend = ((i % 5) - 2) * 11;
      out += `<path d="${quadPath(hub.x, hub.y, s.x, s.y, bend)}" fill="none" stroke="${hub.colour}" stroke-width="1.15" stroke-opacity="0.45"/>`;
    });
  }
  for (const hub of layout.placedHubs) {
    for (const s of hub.spokes) {
      out += `<circle cx="${s.x.toFixed(1)}" cy="${s.y.toFixed(1)}" r="4.4" fill="${hub.colour}"/>`;
    }
  }
  for (const hub of layout.placedHubs) {
    out += `<circle cx="${hub.x.toFixed(1)}" cy="${hub.y.toFixed(1)}" r="${hub.r.toFixed(1)}" fill="${hub.colour}"/>`;
    out += `<circle cx="${hub.x.toFixed(1)}" cy="${hub.y.toFixed(1)}" r="${(hub.r * 0.58).toFixed(1)}" fill="none" stroke="${SB.page}" stroke-width="1.3" stroke-opacity="0.4"/>`;
  }
  const halo = `stroke="${SB.page}" stroke-width="5.5" stroke-linejoin="round" paint-order="stroke"`;
  for (const lab of layout.hubLabels) {
    const hub = lab.hub;
    const nameSize = hub.sites.length >= 10 ? 24 : 20;
    const countSize = 16;
    out += `<text x="${lab.tx.toFixed(1)}" y="${lab.ty.toFixed(1)}" text-anchor="${lab.anchor}" font-family="Newsreader, Georgia, serif" font-size="${nameSize}" font-weight="500" fill="${SB.oak}" ${halo}>${esc(hub.short)}</text>`;
    const countX = lab.anchor === "start" ? lab.tx : lab.anchor === "end" ? lab.tx : lab.tx;
    out += `<text x="${countX.toFixed(1)}" y="${(lab.ty + 18).toFixed(1)}" text-anchor="${lab.anchor}" font-family="'JetBrains Mono', monospace" font-size="${countSize}" fill="${hub.colour}" ${halo}>${hub.sites.length}</text>`;
  }
  if (layout.unlabeled.length) {
    let ly = 980;
    out += `<text x="48" y="${ly}" text-anchor="start" font-family="'JetBrains Mono', monospace" font-size="13" fill="${SB.stone}">`;
    for (const hub of layout.unlabeled) {
      ly += 18;
      out += `<tspan x="48" y="${ly}">${esc(hub.short)}  ${hub.sites.length}</tspan>`;
    }
    out += `</text>`;
  }
  for (const s of layout.siteLabels) {
    const halo = `stroke="${SB.page}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"`;
    out += `<text x="${s.labelX.toFixed(1)}" y="${s.labelY.toFixed(1)}" text-anchor="middle" font-family="'Instrument Sans', system-ui, sans-serif" font-size="15" fill="${SB.oak}" ${halo}>${esc(s.label)}</text>`;
  }
  return out;
}

function cardChrome(data, svg, aria) {
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
</style>
</head>
<body>
  <script>if (location.search.includes("full")) document.body.classList.add("full");</script>
  <div class="card">
    <svg class="sb" viewBox="0 0 100 100"><text x="50.5" y="59" text-anchor="middle" dominant-baseline="central" font-family="Newsreader, Georgia, serif" font-size="84" font-weight="400" letter-spacing="-3" fill="${SB.copper}">S<tspan font-style="italic" font-weight="300" fill="${SB.gold}">b</tspan></text></svg>
    <div class="eyebrow"><span class="title">${esc(data.title)}</span><span class="ed">${esc(data.edition)}</span></div>
    <svg class="network" viewBox="0 0 1200 1200" width="1200" height="1200" role="img" aria-label="${esc(aria)}">${svg}</svg>
    <div class="stat">
      <div class="num">${esc(claim.headline)}</div>
      <div class="line">${esc(claim.body)}</div>
      <div class="line">${esc(claim.groups)}</div>
      <div class="line">${esc(claim.diageo)}</div>
      <div class="caveat">${esc(claim.caveat)}</div>
    </div>
    <div class="foot">
      <div class="source">Companies House PSC filings and Wikidata, matched to the Distillery Map</div>
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
  lines.push(`- ${claim.body} ${claim.groups} ${claim.diageo}`);
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
      "These are groups, not independents. On the map they share one tone, with a short line between their sites and no hub label."
    );
    lines.push("");
    for (const g of data.lesserGroups) {
      lines.push(`- **${g.display}** (${g.sites.length}): ${g.sites.map((s) => s.name).join("; ")}`);
    }
    lines.push("");
  }
  lines.push(`## Hub table (map centroids)`);
  lines.push("");
  lines.push(`Hubs sit at the geographic mean of each group's site coordinates, nudged onto land if the mean is in the sea. No registered offices.`);
  lines.push("");
  lines.push(`| Group | Sites | Centroid (nudged) | Raw mean | Nudged | Source |`);
  lines.push(`|---|---:|---|---|---|---|`);
  for (const h of mapLayout.placedHubs) {
    const src = h.sites[0]?.pscSource || "https://find-and-update.company-information.service.gov.uk/";
    lines.push(
      `| ${h.display} | ${h.sites.length} | ${h.lon.toFixed(4)}, ${h.lat.toFixed(4)} | ${h.rawLon.toFixed(4)}, ${h.rawLat.toFixed(4)} | ${h.nudged ? "yes" : "no"} | ${src} |`
    );
  }
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
    `- **Macdonald & Muir / Ardbeg / Glenmorangie.** Companies House PSC in this file rolls \`SC019038\` to Diageo plc in two hops (Macdonald & Muir → The Glenmorangie Company Limited → Diageo Plc). In the trade those two distilleries are LVMH. The card follows the PSC file, so they sit in Diageo's 34. Do not silently override; fix the walker or the filing and rebuild.`
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
  const { included, fillNames } = loadUniverse(table);
  const data = compute(included, table);
  const web = placeWeb(data);
  const map = placeMap(data, outline);

  writeFileSync(
    CARD_HTML,
    cardChrome(data, svgWeb(web), "Network of Scotch whisky operating groups.")
  );
  writeFileSync(
    MAP_HTML,
    cardChrome(data, svgMap(map), "Map of Scotland with Scotch whisky distilleries by controlling group.")
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
