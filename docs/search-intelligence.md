# Search intelligence

Distillery Map keeps crawl evidence separate from search-performance evidence.
That distinction matters: a page can be indexed with no impressions, and a page
can disappear from a performance export without being deindexed.

## Commands

| Command | Purpose | Credentials |
|---|---|---|
| `npm run search:audit` | Fetch the live sitemap and every listed page; check status, redirects, canonical, `noindex`, rendered inbound links and query-string crawl variants | None |
| `npm run search:ingest -- --dir <folder>` | Ingest a manual Search Console export containing `Chart.csv`, `Queries.csv` and `Pages.csv` | None |
| `npm run search:report -- --period 28d` | Combine the latest crawl audit and comparable performance periods into action-led alerts | None |
| `npm run search:verify` | Check the local consumer, dedupe store and optional credential state | None |
| `npm run search:pull -- --days 28` | Pull finalised Search Analytics data by date, query and page | Read-only GSC OAuth |
| `npm run search:inspect` | Inspect every URL from the latest crawl snapshot against Google's indexed version | Read-only GSC OAuth |
| `npm run search:auth` | One-time helper to mint the read-only refresh token | OAuth client configured first |
| `npm run search:test` | Run parser, crawl-graph, corpus and alert tests | None |

Generated evidence is local and git-ignored:

```text
data/search-intelligence/
  raw/YYYY-MM-DD/...
  normalised/imports.jsonl
  normalised/search-daily.jsonl
  normalised/search-queries.jsonl
  normalised/search-pages.jsonl
  reports/latest-crawl.json
  reports/latest-index.json
  reports/latest.json
```

Raw imports are named with a checksum and are never silently replaced with a
different payload. The normalised store deduplicates by source, report type,
scope and checksum.

## Crawl audit rules

Every URL in the live sitemap should:

- return HTTP 200 without redirecting;
- allow indexing;
- declare itself as canonical; and
- have at least one rendered inbound link from another sitemap page.

Same-origin links containing a query string are reported but do not count as a
canonical crawl path. Fragments are stripped before matching because they do not
create a separate HTTP URL.

Run the audit after navigation, sitemap or routing changes:

```bash
npm run search:audit
npm run search:report
```

Add `-- --strict` to make red crawl issues return a non-zero exit code.

## Performance alerts

The initial thresholds reflect Distillery Map's current search volume:

- **CTR opportunity:** at least 50 impressions, average position 1–10 and CTR below 1%.
- **Page decline:** at least 50 previous impressions and a decline of 30% or more between comparable periods.
- **Search visibility loss:** present in the previous performance period and absent in the current one. This is explicitly not treated as proof of deindexing.
- **Query gap:** at least 20 impressions and less than 45% coverage by the closest page corpus.

The query-gap corpus is built from country pages, distillery names, brand aliases,
descriptions, addresses and the whisk(e)y inventory research. Tokenisation is
Unicode-aware so names such as `Šmakovka`, `țuică` and `pălincă` remain comparable.

## Manual lane first

Until API credentials are configured, export Search Console performance with the
same date range and no filters, unzip it, then run:

```bash
npm run search:ingest -- --dir /path/to/export
npm run search:report -- --period 28d
```

Two non-overlapping 28-day exports are required before decline comparisons can run.

## Optional read-only API setup

Only configure this after the local audit/report consumer is useful.

1. Enable the Google Search Console API in the chosen Google Cloud project.
2. Add `http://localhost:5312` as an authorised redirect URI on the OAuth client.
3. Put `GSC_CLIENT_ID` and `GSC_CLIENT_SECRET` in `.env.local`.
4. Run `npm run search:auth` and store the returned `GSC_REFRESH_TOKEN` in `.env.local`.
5. Run `npm run search:verify -- --require-api`.
6. Run `npm run search:pull -- --days 28` and `npm run search:inspect`, followed by `npm run search:report -- --period 28d`.

Defaults:

```text
GSC_SITE_URL=sc-domain:distillerymap.org
SITE_BASE_URL=https://distillerymap.org
```

The OAuth scope is `webmasters.readonly`. Do not use Google's Indexing API for
these pages; it is not the general-purpose indexing route for directory content.
The read-only URL Inspection endpoint reports the version in Google's index; it
does not run the live-page test and it never requests indexing. Run
`search:audit` first so its sitemap snapshot defines the exact inspection set.

API contracts: [Search Analytics query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query),
[URL Inspection](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect),
and [Search Console API quotas](https://developers.google.com/webmaster-tools/limits).

## Operator interpretation

- Search Analytics measures visibility, not index coverage.
- The crawl report measures what the site exposes now, not what Google last saw.
- Confirm suspected indexing changes in URL Inspection before labelling them as such.
- Repeatedly requesting indexing does not substitute for useful content and internal links.
