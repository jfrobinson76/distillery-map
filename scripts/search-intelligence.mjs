#!/usr/bin/env node
/**
 * Distillery Map search intelligence.
 *
 *   npm run search:audit
 *   npm run search:ingest -- --dir <Search Console export folder>
 *   npm run search:report -- --period 28d
 *   npm run search:verify
 *   npm run search:pull -- --days 28       # only after read-only API setup
 *   npm run search:inspect                 # only after read-only API setup
 */
import crypto from "crypto";
import fs from "fs";
import path from "path";
import {
  DEFAULT_BASE_URL,
  auditCrawlGraph,
  buildIndexInspectionReport,
  buildSiteCorpus,
  canonicalPath,
  generateSearchReport,
  parseCsv,
  relativeSource,
} from "./search-intelligence-core.mjs";

const ROOT = process.cwd();
const DATA = path.join(ROOT, "data", "search-intelligence");
const RAW = path.join(DATA, "raw");
const NORMALISED = path.join(DATA, "normalised");
const REPORTS = path.join(DATA, "reports");
const IMPORTS = path.join(NORMALISED, "imports.jsonl");
const LAG_DAYS = 3;
const DIMENSIONS = ["date", "query", "page"];

function loadLocalEnv() {
  const file = path.join(ROOT, ".env.local");
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const equals = trimmed.indexOf("=");
    if (equals < 1) continue;
    const key = trimmed.slice(0, equals).trim();
    let value = trimmed.slice(equals + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = value;
  }
}

loadLocalEnv();

const BASE_URL = process.env.SITE_BASE_URL ?? DEFAULT_BASE_URL;
const GSC_SITE_URL = process.env.GSC_SITE_URL ?? "sc-domain:distillerymap.org";

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const hasFlag = (name) => process.argv.includes(`--${name}`);
const ensureDir = (directory) => fs.mkdirSync(directory, { recursive: true });
const ymd = (date) => date.toISOString().slice(0, 10);
const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");

function daysAgo(days) {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() - days);
  return ymd(date);
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function appendJsonl(file, records) {
  if (!records.length) return;
  ensureDir(path.dirname(file));
  fs.appendFileSync(file, `${records.map((record) => JSON.stringify(record)).join("\n")}\n`);
}

function writeJson(file, value) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function parseNumber(value) {
  const number = Number(String(value ?? "").replace(/[%,]/g, "").trim());
  return Number.isFinite(number) ? number : 0;
}

function parseOptionalNumber(value) {
  if (value === undefined || value === null || String(value).trim() === "") return null;
  return parseNumber(value);
}

function parseCtr(value) {
  if (value === undefined || value === null || String(value).trim() === "") return null;
  return String(value).includes("%") ? parseNumber(value) / 100 : parseNumber(value);
}

function normalizeDate(value) {
  const trimmed = String(value ?? "").trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed;
  const date = new Date(trimmed);
  return Number.isNaN(date.getTime()) ? null : ymd(date);
}

function importKeys() {
  return new Set(
    readJsonl(IMPORTS).map((record) =>
      `${record.source}|${record.report_type}|${record.report_scope}|${record.checksum}`
    )
  );
}

async function accessToken() {
  const clientId = process.env.GSC_CLIENT_ID;
  const clientSecret = process.env.GSC_CLIENT_SECRET;
  const refreshToken = process.env.GSC_REFRESH_TOKEN;
  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error(
      "Search Console API is not configured. Keep using search:audit/search:ingest until " +
      "GSC_CLIENT_ID, GSC_CLIENT_SECRET and GSC_REFRESH_TOKEN are deliberately added."
    );
  }

  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });
  if (!response.ok) throw new Error(`Google token refresh failed: ${response.status} ${await response.text()}`);
  const payload = await response.json();
  if (!payload.access_token) throw new Error("Google returned no access token.");
  return payload.access_token;
}

async function querySearchAnalytics(token, dimension, startDate, endDate) {
  const endpoint = `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(GSC_SITE_URL)}/searchAnalytics/query`;
  const rowLimit = 25_000;
  const rows = [];

  for (let startRow = 0; ; startRow += rowLimit) {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        startDate,
        endDate,
        dimensions: [dimension],
        rowLimit,
        startRow,
        dataState: "final",
      }),
    });
    if (!response.ok) {
      throw new Error(`Search Analytics ${dimension} query failed: ${response.status} ${await response.text()}`);
    }
    const payload = await response.json();
    const batch = payload.rows ?? [];
    rows.push(...batch);
    if (batch.length < rowLimit) break;
  }
  return rows;
}

async function pull() {
  const days = Number(arg("days", "28"));
  if (!Number.isFinite(days) || days < 1) throw new Error("--days must be a positive number");

  const endDate = arg("end", daysAgo(LAG_DAYS));
  const start = new Date(`${endDate}T00:00:00Z`);
  start.setUTCDate(start.getUTCDate() - (days - 1));
  const startDate = ymd(start);
  const token = await accessToken();
  const seen = importKeys();
  const importedAt = new Date().toISOString();
  const rawDir = path.join(RAW, ymd(new Date()), "google");
  let written = 0;

  console.log(`Pulling ${GSC_SITE_URL} · ${startDate} → ${endDate} (${days} days)`);
  for (const dimension of DIMENSIONS) {
    const rows = await querySearchAnalytics(token, dimension, startDate, endDate);
    const body = JSON.stringify({ rows });
    const checksum = sha256(body);
    const reportType = `search-${dimension}`;
    const rawFile = path.join(rawDir, `${reportType}-${startDate}-${endDate}-${checksum.slice(0, 12)}.json`);
    writeJson(rawFile, { rows });

    const dedupeKey = `google|${reportType}|all|${checksum}`;
    if (seen.has(dedupeKey)) {
      console.log(`  ${dimension}: ${rows.length} rows — already imported`);
      continue;
    }

    const records = rows.map((row) => {
      const value = row.keys?.[0] ?? "";
      return {
        source: "google",
        report_type: reportType,
        report_scope: "all",
        period_start: startDate,
        period_end: endDate,
        imported_at: importedAt,
        source_file: relativeSource(ROOT, rawFile),
        checksum,
        key: dimension === "page" ? canonicalPath(value) : value,
        raw_key: value,
        clicks: row.clicks ?? 0,
        impressions: row.impressions ?? 0,
        ctr: row.ctr ?? 0,
        position: row.position ?? 0,
      };
    });
    const target = { date: "search-daily.jsonl", query: "search-queries.jsonl", page: "search-pages.jsonl" }[dimension];
    appendJsonl(path.join(NORMALISED, target), records);
    appendJsonl(IMPORTS, [{
      source: "google",
      report_type: reportType,
      report_scope: "all",
      period_start: startDate,
      period_end: endDate,
      imported_at: importedAt,
      source_file: relativeSource(ROOT, rawFile),
      checksum,
      rows: records.length,
    }]);
    seen.add(dedupeKey);
    written += records.length;
    console.log(`  ${dimension}: ${records.length} rows → ${target}`);
  }
  console.log(`Done. ${written} new normalised rows.`);
}

async function inspect() {
  const crawlFile = path.join(REPORTS, "latest-crawl.json");
  if (!fs.existsSync(crawlFile)) {
    throw new Error("No crawl snapshot found. Run npm run search:audit first so the inspected set matches the live sitemap.");
  }

  const crawlReport = JSON.parse(fs.readFileSync(crawlFile, "utf8"));
  const limit = Number(arg("limit", String(crawlReport.pages.length)));
  if (!Number.isFinite(limit) || limit < 1) throw new Error("--limit must be a positive number");
  const urls = crawlReport.pages.slice(0, limit).map((page) => page.url);
  const token = await accessToken();
  const inspections = [];

  console.log(`Inspecting ${urls.length} sitemap URL${urls.length === 1 ? "" : "s"} in Google's index…`);
  for (let index = 0; index < urls.length; index += 1) {
    const url = urls[index];
    const response = await fetch("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ inspectionUrl: url, siteUrl: GSC_SITE_URL, languageCode: "en-US" }),
    });
    if (!response.ok) {
      const error = `HTTP ${response.status}: ${await response.text()}`;
      inspections.push({ url, error });
      console.log(`  ${index + 1}/${urls.length} error ${canonicalPath(url)} — HTTP ${response.status}`);
      continue;
    }
    const payload = await response.json();
    inspections.push({ url, inspectionResult: payload.inspectionResult ?? null });
    const verdict = payload.inspectionResult?.indexStatusResult?.verdict ?? "UNKNOWN";
    console.log(`  ${index + 1}/${urls.length} ${verdict.toLowerCase()} ${canonicalPath(url)}`);
  }

  const generatedAt = new Date().toISOString();
  const rawPayload = { generated_at: generatedAt, site: GSC_SITE_URL, inspections };
  const checksum = sha256(JSON.stringify(rawPayload));
  const rawFile = path.join(
    RAW,
    ymd(new Date()),
    "url-inspection",
    `inspection-${generatedAt.replace(/[:.]/g, "-")}-${checksum.slice(0, 12)}.json`
  );
  writeJson(rawFile, rawPayload);

  const result = buildIndexInspectionReport({ inspections, generatedAt, site: GSC_SITE_URL });
  writeJson(path.join(REPORTS, "latest-index.json"), result);
  console.log(`  ${result.counts.indexed}/${result.counts.inspected} indexed · ${result.counts.not_indexed} not indexed · ${result.counts.errors} errors`);
  console.log("Written to data/search-intelligence/reports/latest-index.json");
  if (result.counts.errors) process.exitCode = 1;
}

function ingest() {
  const directory = arg("dir");
  if (!directory) throw new Error("Pass --dir <folder> containing Chart.csv, Queries.csv and Pages.csv");
  const resolved = path.resolve(directory.replace(/^~/, process.env.HOME ?? "~"));
  if (!fs.existsSync(resolved)) throw new Error(`No such folder: ${resolved}`);

  const chartFile = path.join(resolved, "Chart.csv");
  if (!fs.existsSync(chartFile)) throw new Error("Chart.csv is required to establish the export period");
  const chart = parseCsv(fs.readFileSync(chartFile, "utf8"));
  const dates = chart.map((row) => normalizeDate(row.Date)).filter(Boolean).sort();
  if (!dates.length) throw new Error("Chart.csv contains no readable dates");

  const startDate = dates[0];
  const endDate = dates.at(-1);
  const importedAt = new Date().toISOString();
  const source = arg("source", "google");
  const seen = importKeys();
  const rawDir = path.join(RAW, ymd(new Date()), `${source}-export`);
  const dimensions = [
    { name: "date", file: "Chart.csv", key: "Date", target: "search-daily.jsonl" },
    { name: "query", file: "Queries.csv", key: "Top queries", target: "search-queries.jsonl" },
    { name: "page", file: "Pages.csv", key: "Top pages", target: "search-pages.jsonl" },
  ];
  let written = 0;

  console.log(`Ingesting ${source} export · ${startDate} → ${endDate} (${dates.length} days)`);
  for (const dimension of dimensions) {
    const sourceFile = path.join(resolved, dimension.file);
    if (!fs.existsSync(sourceFile)) {
      console.log(`  ${dimension.name}: ${dimension.file} missing — skipped`);
      continue;
    }
    const body = fs.readFileSync(sourceFile, "utf8");
    const rows = parseCsv(body);
    const checksum = sha256(body);
    const reportType = `search-${dimension.name}`;
    const rawFile = path.join(rawDir, `${reportType}-${startDate}-${endDate}-${checksum.slice(0, 12)}.csv`);
    ensureDir(rawDir);
    if (!fs.existsSync(rawFile)) fs.copyFileSync(sourceFile, rawFile);

    const dedupeKey = `${source}|${reportType}|all|${checksum}`;
    if (seen.has(dedupeKey)) {
      console.log(`  ${dimension.name}: ${rows.length} rows — already imported`);
      continue;
    }

    const records = rows.map((row) => {
      const rawKey = row[dimension.key] ?? "";
      return {
        source,
        report_type: reportType,
        report_scope: "all",
        period_start: startDate,
        period_end: endDate,
        imported_at: importedAt,
        source_file: relativeSource(ROOT, rawFile),
        checksum,
        key: dimension.name === "page" ? canonicalPath(rawKey) : dimension.name === "date" ? normalizeDate(rawKey) : rawKey,
        raw_key: rawKey,
        clicks: parseOptionalNumber(row.Clicks),
        impressions: parseOptionalNumber(row.Impressions),
        ctr: parseCtr(row.CTR),
        position: parseOptionalNumber(row.Position),
      };
    }).filter((record) => record.key);

    appendJsonl(path.join(NORMALISED, dimension.target), records);
    appendJsonl(IMPORTS, [{
      source,
      report_type: reportType,
      report_scope: "all",
      period_start: startDate,
      period_end: endDate,
      imported_at: importedAt,
      source_file: relativeSource(ROOT, rawFile),
      checksum,
      rows: records.length,
    }]);
    seen.add(dedupeKey);
    written += records.length;
    console.log(`  ${dimension.name}: ${records.length} rows → ${dimension.target}`);
  }
  console.log(`Done. ${written} new normalised rows.`);
  console.log(`Report with: npm run search:report -- --period ${dates.length}d`);
}

async function audit() {
  console.log(`Auditing ${BASE_URL} sitemap and rendered crawl graph…`);
  const result = await auditCrawlGraph({ baseUrl: BASE_URL });
  const checksum = sha256(JSON.stringify(result));
  const rawFile = path.join(RAW, ymd(new Date()), "crawl", `crawl-${result.generated_at.replace(/[:.]/g, "-")}-${checksum.slice(0, 12)}.json`);
  writeJson(rawFile, result);
  writeJson(path.join(REPORTS, "latest-crawl.json"), result);

  console.log(`  ${result.counts.fetched_200}/${result.counts.sitemap_urls} sitemap URLs returned 200`);
  console.log(`  ${result.counts.orphans} orphaned · ${result.counts.canonical_issues} canonical issues · ${result.counts.pages_with_query_links} pages with query links`);
  for (const issue of result.issues) console.log(`  [${issue.severity}] ${issue.type} — ${issue.url}: ${issue.detail}`);
  console.log("Written to data/search-intelligence/reports/latest-crawl.json");

  if (hasFlag("strict") && result.issues.some((issue) => issue.severity === "red")) process.exitCode = 1;
}

function siteCorpus() {
  const geojson = JSON.parse(fs.readFileSync(path.join(ROOT, "public", "data", "distilleries.geojson"), "utf8"));
  const agingFile = path.join(ROOT, "src", "lib", "aging-inventory.ts");
  const agingInventoryText = fs.existsSync(agingFile) ? fs.readFileSync(agingFile, "utf8") : "";
  return buildSiteCorpus({ geojson, agingInventoryText });
}

function report() {
  const periodDays = Number(String(arg("period", "28d")).replace(/d$/, ""));
  if (!Number.isFinite(periodDays) || periodDays < 1) throw new Error("--period must look like 28d");
  const crawlFile = path.join(REPORTS, "latest-crawl.json");
  const crawlReport = fs.existsSync(crawlFile) ? JSON.parse(fs.readFileSync(crawlFile, "utf8")) : null;
  const indexFile = path.join(REPORTS, "latest-index.json");
  const indexReport = fs.existsSync(indexFile) ? JSON.parse(fs.readFileSync(indexFile, "utf8")) : null;

  const result = generateSearchReport({
    queries: readJsonl(path.join(NORMALISED, "search-queries.jsonl")),
    pages: readJsonl(path.join(NORMALISED, "search-pages.jsonl")),
    daily: readJsonl(path.join(NORMALISED, "search-daily.jsonl")),
    corpus: siteCorpus(),
    crawlReport,
    indexReport,
    periodDays,
    source: arg("source", "google"),
    site: GSC_SITE_URL,
    baseUrl: BASE_URL,
  });
  writeJson(path.join(REPORTS, "latest.json"), result);

  console.log(`Search visibility · ${result.period ? `${result.period.start} → ${result.period.end}` : "no performance data yet"}`);
  if (result.totals.impressions !== null) {
    console.log(`  ${result.totals.clicks} clicks · ${result.totals.impressions} impressions · CTR ${(result.totals.ctr * 100).toFixed(2)}%`);
  }
  if (result.crawl) console.log(`  Crawl: ${result.crawl.counts.fetched_200}/${result.crawl.counts.sitemap_urls} sitemap URLs healthy`);
  if (result.index) console.log(`  Index: ${result.index.counts.indexed}/${result.index.counts.inspected} inspected URLs indexed`);
  console.log(`  ${result.alerts.length} alert${result.alerts.length === 1 ? "" : "s"}`);
  for (const alert of result.alerts.slice(0, 20)) console.log(`  [${alert.severity}] ${alert.type} — ${alert.subject}: ${alert.detail}`);
  if (result.notes) console.log(`  ${result.notes}`);
  console.log("Written to data/search-intelligence/reports/latest.json");
}

function verify() {
  const credentials = ["GSC_CLIENT_ID", "GSC_CLIENT_SECRET", "GSC_REFRESH_TOKEN"];
  const configured = credentials.filter((name) => Boolean(process.env[name]));
  const checks = [
    { ok: fs.existsSync(path.join(ROOT, "public", "data", "distilleries.geojson")), label: "site corpus source exists" },
    { ok: configured.length === 0 || configured.length === credentials.length, label: "API credentials are either complete or deliberately absent" },
    { ok: GSC_SITE_URL === "sc-domain:distillerymap.org" || Boolean(process.env.GSC_SITE_URL), label: `GSC_SITE_URL = ${GSC_SITE_URL}` },
  ];

  const imports = readJsonl(IMPORTS);
  const uniqueImports = new Set(imports.map((record) =>
    `${record.source}|${record.report_type}|${record.report_scope}|${record.checksum}`
  ));
  checks.push({ ok: imports.length === uniqueImports.size, label: `${imports.length} imports, ${uniqueImports.size} distinct` });

  if (hasFlag("require-api")) {
    checks.push({ ok: configured.length === credentials.length, label: "read-only API credentials configured" });
  }

  for (const check of checks) console.log(`  ${check.ok ? "ok  " : "FAIL"} ${check.label}`);
  if (configured.length === 0) console.log("  info API lane dormant by design; search:audit and search:ingest need no credentials");
  const failed = checks.filter((check) => !check.ok).length;
  console.log(`\n${checks.length - failed}/${checks.length} checks passed.`);
  if (failed) process.exitCode = 1;
}

const commands = { audit, pull, inspect, ingest, report, verify };
const command = process.argv[2];
if (!commands[command]) {
  console.error("Usage: node scripts/search-intelligence.mjs <audit|pull|inspect|ingest|report|verify> [options]");
  process.exit(1);
}

try {
  await commands[command]();
} catch (error) {
  console.error(`\n${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
}
