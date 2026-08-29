import path from "path";

export const DEFAULT_BASE_URL = "https://distillerymap.org";

const STOP_WORDS = new Set([
  "the", "a", "an", "and", "or", "for", "to", "in", "of", "on", "is", "it",
  "my", "your", "how", "what", "when", "do", "does", "can", "i", "you", "with",
  "distillery", "distilleries", "map", "stillbound", "spirits", "spirit",
]);

export function canonicalPath(value) {
  try {
    const url = new URL(value, DEFAULT_BASE_URL);
    return url.pathname.replace(/\/+$/, "") || "/";
  } catch {
    return value;
  }
}

export function slugifyName(value) {
  return value
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function tokenise(value) {
  return new Set(
    String(value ?? "")
      .normalize("NFKD")
      .replace(/\p{M}/gu, "")
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s-]/gu, " ")
      .split(/[\s-]+/)
      .filter((word) => word.length > 2 && !STOP_WORDS.has(word))
  );
}

export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quoted) {
      if (character === '"') {
        if (text[index + 1] === '"') {
          field += '"';
          index += 1;
        } else {
          quoted = false;
        }
      } else {
        field += character;
      }
    } else if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (character !== "\r") {
      field += character;
    }
  }

  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  if (!rows.length) return [];

  const headers = rows[0].map((header) => header.replace(/^\uFEFF/, "").trim());
  return rows
    .slice(1)
    .filter((values) => values.length === headers.length && values.some(Boolean))
    .map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index]])));
}

export function parseSitemap(xml) {
  return [...String(xml).matchAll(/<loc>([^<]+)<\/loc>/gi)].map((match) =>
    match[1]
      .replaceAll("&amp;", "&")
      .replaceAll("&lt;", "<")
      .replaceAll("&gt;", ">")
      .trim()
  );
}

export function buildIndexInspectionReport({
  inspections = [],
  generatedAt = new Date().toISOString(),
  site = "sc-domain:distillerymap.org",
} = {}) {
  const pages = inspections.map(({ url, inspectionResult = null, error = null }) => {
    const status = inspectionResult?.indexStatusResult ?? {};
    return {
      url,
      path: canonicalPath(url),
      indexed: status.verdict === "PASS",
      verdict: status.verdict ?? null,
      coverage_state: status.coverageState ?? null,
      robots_txt_state: status.robotsTxtState ?? null,
      indexing_state: status.indexingState ?? null,
      page_fetch_state: status.pageFetchState ?? null,
      last_crawl_time: status.lastCrawlTime ?? null,
      google_canonical: status.googleCanonical ?? null,
      user_canonical: status.userCanonical ?? null,
      referring_urls: status.referringUrls ?? [],
      sitemaps: status.sitemap ?? [],
      inspection_result_link: inspectionResult?.inspectionResultLink ?? null,
      error,
    };
  });

  const issues = [];
  for (const page of pages) {
    if (page.error) {
      issues.push({
        type: "inspection-error",
        severity: "red",
        url: page.url,
        detail: page.error,
      });
      continue;
    }
    if (page.indexed) continue;

    const technicalBlock =
      page.robots_txt_state === "DISALLOWED" ||
      (page.indexing_state && !["INDEXING_ALLOWED", "INDEXING_STATE_UNSPECIFIED"].includes(page.indexing_state)) ||
      (page.page_fetch_state && !["SUCCESSFUL", "PAGE_FETCH_STATE_UNSPECIFIED"].includes(page.page_fetch_state));
    const detail = [page.coverage_state, page.page_fetch_state, page.indexing_state]
      .filter(Boolean)
      .join(" · ") || "Google returned no index-status detail";
    issues.push({
      type: technicalBlock ? "index-technical-block" : "not-indexed",
      severity: technicalBlock ? "red" : "amber",
      url: page.url,
      detail,
    });
  }

  return {
    generated_at: generatedAt,
    site,
    counts: {
      inspected: pages.length,
      indexed: pages.filter((page) => page.indexed).length,
      not_indexed: pages.filter((page) => !page.indexed && !page.error).length,
      errors: pages.filter((page) => page.error).length,
    },
    issues,
    pages,
  };
}

function attribute(tag, name) {
  const match = tag.match(new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, "i"));
  return match?.[2] ?? null;
}

function normalizedUrl(value) {
  const url = new URL(value);
  return `${url.origin}${url.pathname === "/" ? "/" : url.pathname.replace(/\/+$/, "")}`;
}

export function extractHtmlSignals(html, pageUrl) {
  const linkTags = [...String(html).matchAll(/<link\b[^>]*>/gi)].map((match) => match[0]);
  const canonicalTag = linkTags.find((tag) =>
    (attribute(tag, "rel") ?? "").toLowerCase().split(/\s+/).includes("canonical")
  );
  const canonicalHref = canonicalTag ? attribute(canonicalTag, "href") : null;

  const robotsTags = [...String(html).matchAll(/<meta\b[^>]*>/gi)]
    .map((match) => match[0])
    .filter((tag) => ["robots", "googlebot"].includes((attribute(tag, "name") ?? "").toLowerCase()));
  const robotsContent = robotsTags.map((tag) => attribute(tag, "content") ?? "").join(",").toLowerCase();

  const hrefs = [...String(html).matchAll(/<a\b[^>]*>/gi)]
    .map((match) => attribute(match[0], "href"))
    .filter(Boolean)
    .map((href) => href.replaceAll("&amp;", "&"));

  return {
    canonical: canonicalHref ? new URL(canonicalHref, pageUrl).href : null,
    noindex: /(?:^|[,\s])noindex(?:$|[,\s])/i.test(robotsContent),
    hrefs,
  };
}

async function mapWithConcurrency(values, concurrency, mapper) {
  const results = new Array(values.length);
  let nextIndex = 0;

  async function worker() {
    while (nextIndex < values.length) {
      const index = nextIndex;
      nextIndex += 1;
      results[index] = await mapper(values[index], index);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, values.length) }, worker));
  return results;
}

export async function auditCrawlGraph({
  baseUrl = DEFAULT_BASE_URL,
  fetchImpl = fetch,
  concurrency = 8,
  generatedAt = new Date().toISOString(),
} = {}) {
  const origin = new URL(baseUrl).origin;
  const sitemapUrl = new URL("/sitemap.xml", origin).href;
  const sitemapResponse = await fetchImpl(sitemapUrl, { redirect: "follow" });
  if (!sitemapResponse.ok) {
    throw new Error(`Sitemap fetch failed: ${sitemapResponse.status} ${sitemapUrl}`);
  }

  const urls = parseSitemap(await sitemapResponse.text()).map(normalizedUrl);
  const targets = new Set(urls);
  const inbound = new Map(urls.map((url) => [url, new Set()]));

  const pages = await mapWithConcurrency(urls, concurrency, async (url) => {
    try {
      const response = await fetchImpl(url, { redirect: "follow" });
      const contentType = response.headers?.get?.("content-type") ?? "";
      const html = contentType.includes("text/html") ? await response.text() : "";
      const signals = extractHtmlSignals(html, url);
      const outbound = new Set();
      const queryLinks = new Set();

      for (const href of signals.hrefs) {
        let resolved;
        try {
          resolved = new URL(href, url);
        } catch {
          continue;
        }
        if (resolved.origin !== origin) continue;
        if (resolved.search) {
          queryLinks.add(resolved.href);
          continue;
        }
        const target = normalizedUrl(resolved.href);
        if (targets.has(target) && target !== url) outbound.add(target);
      }

      return {
        url,
        status: response.status,
        final_url: normalizedUrl(response.url || url),
        content_type: contentType,
        canonical: signals.canonical ? normalizedUrl(signals.canonical) : null,
        noindex: signals.noindex,
        outbound: [...outbound].sort(),
        query_links: [...queryLinks].sort(),
        error: null,
      };
    } catch (error) {
      return {
        url,
        status: null,
        final_url: null,
        content_type: null,
        canonical: null,
        noindex: null,
        outbound: [],
        query_links: [],
        error: error instanceof Error ? error.message : String(error),
      };
    }
  });

  for (const page of pages) {
    for (const target of page.outbound) inbound.get(target)?.add(page.url);
  }

  for (const page of pages) {
    page.referring_pages = [...(inbound.get(page.url) ?? [])].sort();
    page.inbound = page.referring_pages.length;
  }

  const issues = [];
  for (const page of pages) {
    if (page.error || page.status !== 200) {
      issues.push({ type: "http-error", severity: "red", url: page.url, detail: page.error ?? `HTTP ${page.status}` });
    }
    if (page.final_url && page.final_url !== page.url) {
      issues.push({ type: "sitemap-redirect", severity: "red", url: page.url, detail: `Redirects to ${page.final_url}` });
    }
    if (page.noindex) {
      issues.push({ type: "sitemap-noindex", severity: "red", url: page.url, detail: "Sitemap URL declares noindex" });
    }
    if (page.status === 200 && !page.canonical) {
      issues.push({ type: "missing-canonical", severity: "amber", url: page.url, detail: "No canonical link in rendered HTML" });
    } else if (page.canonical && page.canonical !== page.url) {
      issues.push({ type: "canonical-mismatch", severity: "red", url: page.url, detail: `Canonical points to ${page.canonical}` });
    }
    if (page.inbound === 0) {
      issues.push({ type: "crawl-orphan", severity: "amber", url: page.url, detail: "No rendered inbound link from another sitemap page" });
    }
    if (page.query_links.length) {
      issues.push({
        type: "query-link-variants",
        severity: "amber",
        url: page.url,
        detail: `${page.query_links.length} rendered same-origin query-string link${page.query_links.length === 1 ? "" : "s"}`,
      });
    }
  }

  const count = (type) => issues.filter((issue) => issue.type === type).length;
  return {
    generated_at: generatedAt,
    site: origin,
    sitemap: sitemapUrl,
    counts: {
      sitemap_urls: urls.length,
      fetched_200: pages.filter((page) => page.status === 200).length,
      fetch_failures: pages.filter((page) => page.status !== 200).length,
      orphans: count("crawl-orphan"),
      noindex: count("sitemap-noindex"),
      canonical_issues: count("missing-canonical") + count("canonical-mismatch"),
      redirects: count("sitemap-redirect"),
      pages_with_query_links: count("query-link-variants"),
    },
    issues,
    pages,
  };
}

export function buildSiteCorpus({ geojson, agingInventoryText = "" }) {
  const features = Array.isArray(geojson?.features) ? geojson.features : [];
  const byCountry = new Map();
  let scotlandCount = 0;

  for (const feature of features) {
    const properties = feature?.properties ?? {};
    const country = String(properties.country ?? "").trim();
    if (country) {
      if (!byCountry.has(country)) byCountry.set(country, []);
      byCountry.get(country).push(properties);
    }
    if (properties.region === "scotland") scotlandCount += 1;
  }

  const corpus = [
    { path: "/", text: "worldwide open community distillery map whiskey whisky gin rum brandy vodka" },
    { path: "/distilleries", text: `distilleries by country ${[...byCountry.keys()].join(" ")}` },
    { path: "/whiskey-aging-inventory", text: `global whisk(e)y aging inventory casks barrels stock maturation ${agingInventoryText}` },
  ];

  for (const [country, propertiesList] of byCountry) {
    if (propertiesList.length < 5) continue;
    const text = propertiesList
      .flatMap((properties) => [
        properties.name,
        properties.country,
        properties.address,
        properties.description,
        ...(Array.isArray(properties.brands) ? properties.brands : []),
        ...(Array.isArray(properties.spirits) ? properties.spirits : []),
      ])
      .filter(Boolean)
      .join(" ");
    corpus.push({ path: `/distilleries/${slugifyName(country)}`, text: `${country} ${text}` });
  }

  if (scotlandCount >= 5) {
    const scotlandText = features
      .filter((feature) => feature?.properties?.region === "scotland")
      .flatMap((feature) => [feature.properties.name, feature.properties.address, feature.properties.description])
      .filter(Boolean)
      .join(" ");
    corpus.push({ path: "/distilleries/scotland", text: `Scotland Scotch whisky ${scotlandText}` });
  }

  return corpus.map((page) => ({ path: page.path, tokens: tokenise(page.text) }));
}

export function bestPageMatch(query, corpus) {
  const queryTokens = tokenise(query);
  if (!queryTokens.size) return { score: 1, path: null };

  let best = { score: 0, path: null };
  for (const page of corpus) {
    let hits = 0;
    for (const token of queryTokens) if (page.tokens.has(token)) hits += 1;
    const score = hits / queryTokens.size;
    if (score > best.score) best = { score, path: page.path };
  }
  return best;
}

export function periodPair(records, periodDays) {
  const periods = new Map();
  for (const record of records) {
    const key = `${record.period_start}|${record.period_end}`;
    if (!periods.has(key)) periods.set(key, []);
    periods.get(key).push(record);
  }

  const ordered = [...periods.entries()]
    .map(([key, rows]) => {
      const [period_start, period_end] = key.split("|");
      const length = Math.round((Date.parse(period_end) - Date.parse(period_start)) / 86400000) + 1;
      return { period_start, period_end, length, rows };
    })
    .filter((period) => !periodDays || period.length === periodDays)
    .sort((a, b) => b.period_end.localeCompare(a.period_end));

  const current = ordered[0] ?? null;
  const previous = current
    ? ordered.find((period) => period.period_end < current.period_start && period.length === current.length) ?? null
    : null;
  return { current, previous };
}

export function latestByKey(rows) {
  const latest = new Map();
  for (const row of rows) {
    const current = latest.get(row.key);
    if (!current || row.imported_at > current.imported_at) latest.set(row.key, row);
  }
  return latest;
}

function sumMetric(map, metric) {
  let total = 0;
  let measured = false;
  for (const row of map.values()) {
    if (row[metric] === null || row[metric] === undefined) continue;
    total += row[metric];
    measured = true;
  }
  return measured ? total : null;
}

export function generateSearchReport({
  queries = [],
  pages = [],
  daily = [],
  corpus = [],
  crawlReport = null,
  indexReport = null,
  periodDays = 28,
  source = "google",
  site = "sc-domain:distillerymap.org",
  baseUrl = DEFAULT_BASE_URL,
  generatedAt = new Date().toISOString(),
} = {}) {
  const filterSource = (records) => records.filter((record) => (record.source ?? "google") === source);
  const queryPeriods = periodPair(filterSource(queries), periodDays);
  const pagePeriods = periodPair(filterSource(pages), periodDays);
  const dailyPeriods = periodPair(filterSource(daily), periodDays);

  const currentQueries = queryPeriods.current ? latestByKey(queryPeriods.current.rows) : new Map();
  const currentPages = pagePeriods.current ? latestByKey(pagePeriods.current.rows) : new Map();
  const previousPages = pagePeriods.previous ? latestByKey(pagePeriods.previous.rows) : new Map();
  const currentDaily = dailyPeriods.current ? latestByKey(dailyPeriods.current.rows) : new Map();
  const previousDaily = dailyPeriods.previous ? latestByKey(dailyPeriods.previous.rows) : new Map();
  const period = queryPeriods.current ?? pagePeriods.current ?? dailyPeriods.current;
  const comparisonPeriod = pagePeriods.previous ?? dailyPeriods.previous;
  const alerts = [];

  for (const issue of crawlReport?.issues ?? []) {
    alerts.push({
      type: issue.type,
      severity: issue.severity,
      subject: canonicalPath(issue.url),
      url: issue.url,
      detail: issue.detail,
      evidence: "live-crawl",
    });
  }

  for (const issue of indexReport?.issues ?? []) {
    alerts.push({
      type: issue.type,
      severity: issue.severity,
      subject: canonicalPath(issue.url),
      url: issue.url,
      detail: issue.detail,
      evidence: "gsc-url-inspection",
    });
  }

  for (const row of currentQueries.values()) {
    const hasQueryMetrics = [row.clicks, row.impressions, row.ctr, row.position]
      .every((value) => value !== null && value !== undefined);
    if (hasQueryMetrics && row.impressions >= 50 && row.position >= 1 && row.position <= 10 && row.ctr < 0.01) {
      alerts.push({
        type: "ctr-opportunity",
        severity: "amber",
        subject: row.key,
        detail: `${row.impressions} impressions at position ${row.position.toFixed(1)}, CTR ${(row.ctr * 100).toFixed(2)}%. Check title and description alignment.`,
        clicks: row.clicks,
        impressions: row.impressions,
        ctr: row.ctr,
        position: row.position,
        evidence: "search-performance",
      });
    }

    if (hasQueryMetrics && row.impressions >= 20) {
      const match = bestPageMatch(row.key, corpus);
      if (match.score < 0.45) {
        alerts.push({
          type: "query-gap",
          severity: "green",
          subject: row.key,
          detail: `${row.impressions} impressions, ${row.clicks} clicks, position ${row.position.toFixed(1)}. Nearest page covers ${Math.round(match.score * 100)}% of meaningful query terms.`,
          impressions: row.impressions,
          clicks: row.clicks,
          position: row.position,
          nearest_page: match.path,
          evidence: "search-performance",
        });
      }
    }
  }

  for (const [key, previous] of previousPages) {
    if (previous.impressions === null || previous.impressions < 50) continue;
    const current = currentPages.get(key);
    if (current && (current.impressions === null || current.impressions === undefined)) continue;
    const currentImpressions = current?.impressions ?? 0;
    const change = (currentImpressions - previous.impressions) / previous.impressions;
    if (change <= -0.3) {
      alerts.push({
        type: current ? "page-decline" : "search-visibility-loss",
        severity: "amber",
        subject: key,
        url: new URL(key, baseUrl).href,
        detail: current
          ? `Impressions down ${Math.round(Math.abs(change) * 100)}%, ${previous.impressions} → ${currentImpressions}.`
          : `Absent from the current performance report after ${previous.impressions} impressions. This is not proof of deindexing; check URL Inspection separately.`,
        impressions: currentImpressions,
        prior_impressions: previous.impressions,
        change,
        evidence: "search-performance",
      });
    }
  }

  const severityOrder = { red: 0, amber: 1, green: 2 };
  alerts.sort((a, b) =>
    severityOrder[a.severity] - severityOrder[b.severity] ||
    (b.impressions ?? 0) - (a.impressions ?? 0) ||
    a.subject.localeCompare(b.subject)
  );

  const totalsSource = currentDaily.size ? currentDaily : currentPages;
  const previousTotalsSource = previousDaily.size ? previousDaily : previousPages;
  const clicks = sumMetric(totalsSource, "clicks");
  const impressions = sumMetric(totalsSource, "impressions");
  const previousClicks = sumMetric(previousTotalsSource, "clicks");
  const previousImpressions = sumMetric(previousTotalsSource, "impressions");

  const topRows = (map, label) => [...map.values()]
    .filter((row) => row.clicks !== null && row.impressions !== null)
    .sort((a, b) => b.clicks - a.clicks || b.impressions - a.impressions)
    .slice(0, 10)
    .map((row) => ({
      [label]: row.key,
      clicks: row.clicks,
      impressions: row.impressions,
      position: row.position === null || row.position === undefined
        ? null
        : Number(row.position.toFixed(1)),
    }));

  return {
    generated_at: generatedAt,
    source,
    site,
    period: period ? { start: period.period_start, end: period.period_end, days: period.length } : null,
    comparison: comparisonPeriod
      ? { period_start: comparisonPeriod.period_start, period_end: comparisonPeriod.period_end }
      : null,
    totals: {
      clicks,
      impressions,
      ctr: clicks !== null && impressions ? clicks / impressions : null,
      clicks_previous: previousClicks,
      impressions_previous: previousImpressions,
    },
    crawl: crawlReport
      ? { generated_at: crawlReport.generated_at, counts: crawlReport.counts }
      : null,
    index: indexReport
      ? { generated_at: indexReport.generated_at, counts: indexReport.counts }
      : null,
    top_pages: topRows(currentPages, "page"),
    top_queries: topRows(currentQueries, "query"),
    alerts,
    notes: period
      ? comparisonPeriod
        ? null
        : "Only one comparable period is available; decline alerts will begin after the next import."
      : "No Search Console performance data yet. Crawl and URL Inspection alerts remain independent; ingest an export or configure the read-only API lane later.",
  };
}

export function relativeSource(root, file) {
  return path.relative(root, file).split(path.sep).join("/");
}
