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

## Phase 1: United Kingdom (521 distilleries). State at 18 Sep 2026, 18:30

The Companies House name pass has **already been run** on all 521 (`--companies-house`,
commit 861f356). Do not rerun it. Result: 365 slugs have a row; 276 `high`/`verified`,
72 `medium`, 17 `low`, **156 unmatched**. The remaining work is judgment, not volume.

**1a. The 156 unmatched.** List them with
`python3 -c "..."` (see the commit message for the snippet) or by diffing the geojson UK
slugs against the crosswalk. Nearly all are sites with no company of their own: Diageo
(Dailuaine, Auchroisk, Glendullan, Glen Ord, Inchgower...), Bacardi (MacDuff, Royal Brackla,
Aultmore, Craigellachie, Aberfeldy), Inver House (Speyburn, Balmenach, Knockdhu, Pulteney,
Balblair), Chivas, Whyte & Mackay, Edrington, William Grant, Loch Lomond Group, Ian Macleod,
Gordon & MacPhail, Distell/Heineken (Bunnahabhain, Deanston, Tobermory), Beam Suntory
(Bowmore, Laphroaig, Ardmore, Glen Garioch, Auchentoshan). Find the **operating company** per
group on Companies House (SIC 11010, files full accounts, not dormant), confirm it on the
register page, then add one row per site to `company-crosswalk-manual.csv` with
`relation: operator` and the group named in `note`. Roughly 15 companies cover most of the 156.
Independent distilleries in the list (Arran, Abhainn Dearg) get their own search by hand.

**1b. The 72 `medium` and 17 `low`.** For each, open the register page. Read SIC codes and
`accounts.last_accounts.type`. Promote to `verified` in the manual CSV when SIC 11010 and
non-dormant accounts agree with the distillery; replace with the operator when the match is
a shell (BOWMORE LTD dissolved, ARDMORE LIMITED 2023, ABERFELDY LIMITED 2025, GLENBURGIE
DISTILLERY LIMITED 00074809 is a dormant Chivas name-holder); leave `low` with a reason
when neither is possible.

**1c. Target:** ≥ 450 of 521 UK slugs with a `high` or `verified` row, every one of the 156
either mapped to its operator or listed with a reason. Report the final distribution and the
residual list in the PR.

Rules from the matcher, keep them: an exact name on a dissolved or post-2023 registration is
`medium` at best; group-level numbers (Diageo plc 00023307) are `relation: group`, and the
operating subsidiary is a second row for the same slug when it exists.

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
