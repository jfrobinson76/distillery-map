# Brief: populate the distillery → registered company crosswalk

For Devin or a Cursor cloud agent. Branch from `data/company-crosswalk`. Open one PR per
phase. Do not merge; John merges.

## What exists

- `public/data/distilleries.geojson`: 6,139 distilleries, fields `slug name country region
  address website`. No company field.
- `data/company-crosswalk/company-crosswalk.csv`: 97 rows so far. Columns: `slug,
  distillery_name, country, registry, company_number, company_name, relation, match_method,
  confidence, verified, source, note`. 23 rows are `verified`; keep them untouched.
- `data/company-crosswalk/company-crosswalk-manual.csv`: hand-verified rows. Append here
  when you confirm a number by reading the register page; never edit the generated file
  by hand.
- `scripts/build_company_crosswalk.py`: builds the CSV from manual + Wikidata, and with
  `--companies-house` searches the Companies House API for UK names. Read its docstring.

## Secrets

`COMPANIES_HOUSE_API_KEY`: John supplies it. Free REST key from
https://developer.company-information.service.gov.uk/. Rate limit 600 requests per five
minutes; the script sleeps 0.6 s between calls. Never commit the key. Never raise the rate.

## Phase 1: United Kingdom (521 distilleries)

1. Run `python3 scripts/build_company_crosswalk.py --companies-house --limit 20`. Check the
   20 by hand against the register pages. Fix the matcher before scaling if more than 3 of 20
   are wrong.
2. Improve the matcher with the company profile endpoint
   (`GET /company/{number}`), which returns `sic_codes`. **SIC 11010 (distilling, rectifying
   and blending of spirits) is the strongest confidence signal available.** A name match with
   SIC 11010 is `high`; a name match with any other SIC is `medium` at best; 11050 (beer),
   47250 (retail of beverages) or 56xxx (hospitality) with a distillery-like name is a
   visitor-centre or bar company, not the producer: mark `low`, note it.
3. **Shells.** The first 20-name run (18 Sep) matched BOWMORE LTD (dissolved), ARDMORE LIMITED
   (registered 2023) and ABERFELDY LIMITED (registered 2025) on exact name. None operates the
   distillery; Beam Suntory, Beam Suntory and John Dewar & Sons do. The script now caps
   dissolved or post-2023 registrations at `medium`. Go further: read the profile's
   `accounts.last_accounts.type`; `dormant` or `micro-entity` on a famous name is a shell,
   mark `low` and find the operator via the SIC 11010 search or the group's Wikidata owner.
3b. Prefer the **operating company** over the holding company where both exist. Diageo plc
   (00023307) is the correct owner of Caol Ila and the wrong entity for accounts; note the
   group in `relation: group` and, if the operating company can be found, add it as a second
   row for the same slug with `relation: operator`. One slug may have two rows.
4. Run the full 521. Target: **≥ 400 UK slugs with a `high` or `verified` row.** Report the
   distribution of `confidence` and the slugs with no match at all as a list in the PR.
5. Do not touch the geojson.

## Phase 2: Ireland (check count with `country == "Ireland"`)

The Irish register is the CRO. Two routes; use the first if it works:
- CRO Open Services API (free, registration): https://services.cro.ie/ . Search by name,
  returns company number, status, type. Same matching rules as UK; Irish NACE code for
  distilling is 11.01.
- Fallback: https://core.cro.ie/ public search, one name at a time, no scraping beyond what a
  human would do. Record every number in the manual CSV with the CRO page as `source`.

Northern Ireland distilleries are on Companies House (numbers prefixed `NI`), not the CRO.

## Phase 3: the rest, only where a free public register exists

United States has no national company register; skip. Belgium, France, Norway, Denmark,
New Zealand, Japan carry OpenCorporates-style ids from Wikidata already; leave them.
Germany, Austria, Australia, Canada: stop and write down which register would work and
whether it is free, do not build.

## Rules

- **Claim only what was read.** `verified` means a human or the agent opened the register
  page for that number and the name and address agree with the distillery. Everything else
  is a lead with a confidence.
- Never fetch beyond the rate limit, never parallelise the API calls, never scrape a site
  whose terms forbid it. No uncapped runs.
- Every PR description states: rows added, confidence distribution, how many register pages
  were opened, and the slugs that could not be matched.
- Small, readable commits. Match the style of the script; no new dependencies.

## Done looks like

`company-crosswalk.csv` with ≥ 400 UK and the achievable Irish rows at `high`/`verified`, a
`low` list a human can work through later, and no change to anything outside
`data/company-crosswalk/` and `scripts/build_company_crosswalk.py`.

Context, if wanted: the vault note "Own the Index - Public Data Joins Plan" (Stillbound
Knowledge, `06 Stillbound engine`) explains why this file exists.
