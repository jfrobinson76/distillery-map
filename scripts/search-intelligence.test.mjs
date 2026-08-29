import assert from "node:assert/strict";
import test from "node:test";
import {
  auditCrawlGraph,
  bestPageMatch,
  buildIndexInspectionReport,
  buildSiteCorpus,
  generateSearchReport,
  parseCsv,
  tokenise,
} from "./search-intelligence-core.mjs";

test("CSV parsing preserves quoted queries and percentage fields", () => {
  const rows = parseCsv('\uFEFFTop queries,Clicks,Impressions,CTR\n"gin, ireland",2,120,1.67%\n');
  assert.deepEqual(rows, [{ "Top queries": "gin, ireland", Clicks: "2", Impressions: "120", CTR: "1.67%" }]);
});

test("Unicode tokenisation keeps global spirit names comparable", () => {
  assert.deepEqual([...tokenise("Šmakovka, țuică & Pălincă")], ["smakovka", "tuica", "palinca"]);
});

test("crawl audit ignores query variants as canonical crawl paths and detects orphans", async () => {
  const pages = new Map([
    ["https://example.test/sitemap.xml", [200, "application/xml", `
      <urlset>
        <url><loc>https://example.test/</loc></url>
        <url><loc>https://example.test/a</loc></url>
        <url><loc>https://example.test/b</loc></url>
        <url><loc>https://example.test/orphan</loc></url>
      </urlset>`]],
    ["https://example.test/", [200, "text/html", '<link rel="canonical" href="https://example.test/"><a href="/a">A</a><a href="/b?filter=gin">Filtered</a>']],
    ["https://example.test/a", [200, "text/html", '<link rel="canonical" href="/a"><a href="/b#results">B</a>']],
    ["https://example.test/b", [200, "text/html", '<link rel="canonical" href="/b"><a href="/">Home</a>']],
    ["https://example.test/orphan", [200, "text/html", '<link rel="canonical" href="/orphan">']],
  ]);
  const fetchImpl = async (url) => {
    const row = pages.get(String(url));
    if (!row) return new Response("missing", { status: 404 });
    return new Response(row[2], { status: row[0], headers: { "content-type": row[1] } });
  };

  const report = await auditCrawlGraph({
    baseUrl: "https://example.test",
    fetchImpl,
    concurrency: 2,
    generatedAt: "2026-08-29T12:00:00.000Z",
  });

  assert.equal(report.counts.sitemap_urls, 4);
  assert.equal(report.counts.fetched_200, 4);
  assert.equal(report.counts.orphans, 1);
  assert.equal(report.counts.pages_with_query_links, 1);
  assert.equal(report.pages.find((page) => page.url.endsWith("/b")).inbound, 1);
  assert.equal(report.pages.find((page) => page.url.endsWith("/orphan")).inbound, 0);
});

test("site corpus maps distillery and brand queries to their country page", () => {
  const corpus = buildSiteCorpus({
    geojson: {
      features: Array.from({ length: 5 }, (_, index) => ({
        properties: {
          name: index === 0 ? "Latgolys Šmakovka" : `Latvia Producer ${index}`,
          country: "Latvia",
          brands: index === 0 ? ["Riga Rye"] : [],
        },
      })),
    },
  });

  assert.deepEqual(bestPageMatch("Riga Rye distillery", corpus), { score: 1, path: "/distilleries/latvia" });
  assert.deepEqual(bestPageMatch("Šmakovka Latvia", corpus), { score: 1, path: "/distilleries/latvia" });
});

test("URL Inspection keeps exclusions separate from technical index blocks", () => {
  const report = buildIndexInspectionReport({
    generatedAt: "2026-08-29T12:00:00.000Z",
    inspections: [
      {
        url: "https://distillerymap.org/distilleries/latvia",
        inspectionResult: { indexStatusResult: { verdict: "PASS", coverageState: "Submitted and indexed" } },
      },
      {
        url: "https://distillerymap.org/distilleries/finland",
        inspectionResult: {
          indexStatusResult: {
            verdict: "NEUTRAL",
            coverageState: "Crawled - currently not indexed",
            robotsTxtState: "ALLOWED",
            indexingState: "INDEXING_ALLOWED",
            pageFetchState: "SUCCESSFUL",
          },
        },
      },
      {
        url: "https://distillerymap.org/blocked",
        inspectionResult: {
          indexStatusResult: {
            verdict: "FAIL",
            coverageState: "Excluded by noindex",
            indexingState: "BLOCKED_BY_META_TAG",
          },
        },
      },
    ],
  });

  assert.deepEqual(report.counts, { inspected: 3, indexed: 1, not_indexed: 2, errors: 0 });
  assert.ok(report.issues.some((issue) => issue.type === "not-indexed" && issue.severity === "amber"));
  assert.ok(report.issues.some((issue) => issue.type === "index-technical-block" && issue.severity === "red"));
});

test("report keeps crawl, CTR, query-gap and visibility alerts separate", () => {
  const importedAt = "2026-08-29T12:00:00.000Z";
  const current = { period_start: "2026-07-30", period_end: "2026-08-26", imported_at: importedAt, source: "google" };
  const previous = { period_start: "2026-07-02", period_end: "2026-07-29", imported_at: importedAt, source: "google" };
  const report = generateSearchReport({
    periodDays: 28,
    queries: [
      { ...current, key: "ecuador rum", clicks: 0, impressions: 80, ctr: 0, position: 6 },
      { ...current, key: "cask market outlook", clicks: 1, impressions: 25, ctr: 0.04, position: 14 },
    ],
    pages: [
      { ...previous, key: "/distilleries/finland", clicks: 4, impressions: 100, ctr: 0.04, position: 9 },
      { ...current, key: "/distilleries/finland", clicks: 2, impressions: 60, ctr: 0.033, position: 11 },
    ],
    daily: [{ ...current, key: "2026-08-26", clicks: 8, impressions: 300, ctr: 0.026, position: 12 }],
    corpus: [
      { path: "/distilleries/ecuador", tokens: tokenise("Ecuador rum aguardiente") },
      { path: "/whiskey-aging-inventory", tokens: tokenise("whiskey aging inventory") },
    ],
    crawlReport: {
      generated_at: importedAt,
      counts: { sitemap_urls: 72, fetched_200: 72 },
      issues: [{ type: "crawl-orphan", severity: "amber", url: "https://distillerymap.org/research", detail: "No inbound link" }],
    },
    indexReport: {
      generated_at: importedAt,
      counts: { inspected: 2, indexed: 1, not_indexed: 1, errors: 0 },
      issues: [{ type: "not-indexed", severity: "amber", url: "https://distillerymap.org/distilleries/greece", detail: "Crawled - currently not indexed" }],
    },
  });

  assert.equal(report.totals.clicks, 8);
  assert.ok(report.alerts.some((alert) => alert.type === "crawl-orphan"));
  assert.ok(report.alerts.some((alert) => alert.type === "ctr-opportunity" && alert.subject === "ecuador rum"));
  assert.ok(report.alerts.some((alert) => alert.type === "query-gap" && alert.subject === "cask market outlook"));
  assert.ok(report.alerts.some((alert) => alert.type === "page-decline"));
  assert.ok(report.alerts.some((alert) => alert.type === "not-indexed" && alert.evidence === "gsc-url-inspection"));
  assert.ok(!report.alerts.some((alert) => alert.type === "index-issue"));
});
