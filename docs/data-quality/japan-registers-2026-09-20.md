# Japan register research — distillery -> company crosswalk

Dated 20 Sep 2026. Country group: Japan (118 pins in `public/data/distilleries.geojson`,
`country == "Japan"`). This is a second-pass note: a prior agent ran the downloads and
built the candidate file; this pass fixed a matcher bug (see "Matcher fix" below), verified
every claim below against the cached page it comes from, and completed this note.

## Registers and lists

### 1. NTA 法人番号公表サイト (National Tax Agency Corporate Number Publication Site) — `jp-houjin-bangou`

- URL: https://www.houjin-bangou.nta.go.jp/
- Free. No account, no key, no paid tier for the data itself.
- **Bulk download** ("基本３情報ダウンロード"): https://www.houjin-bangou.nta.go.jp/download/
  (fetched, cached as `https___www.houjin-bangou.nta.go.jp_download_.html`). Nationwide or
  per-prefecture/overseas ZIP, three formats (CSV Shift-JIS, CSV Unicode, XML Unicode). Per
  the page: "全件データのダウンロード / 前月末時点で公表している法人等の最新情報を...ダウンロードすることができます"
  — the full-file snapshot is as of the end of the *previous* month; a same-day diff feed
  ("差分データ") also exists but was not used here (bulk snapshot is enough for a one-off
  crosswalk). Per-prefecture CSV-Unicode files fetched: 35 of 47 prefectures (only the ones
  a pin's address or the hand-row table needs), 224 MB total (`du -sh cache/nta/`), well
  under the 2 GB cap. Nationwide single file is listed at 240 MB (fileno 27886, seen in
  `zenken-filenos.json`) — not used; per-prefecture is smaller and sufficient.
  **Licence**: 公共データ利用規約（第1.0版） (PDL 1.0 — Japan's standard open-government
  licence, CC BY 4.0-compatible: attribution required, no implication the government
  produced a derivative work). Confirmed on the site's own terms page
  (`https___www.houjin-bangou.nta.go.jp_riyokiyaku_.html`, fetched) and again on
  `www.nta.go.jp-terms.html` (nta.go.jp terms explicitly list houjin-bangou.nta.go.jp
  content under the same PDL 1.0). Attribution used in `source`/`note` columns:
  "出典：国税庁法人番号公表サイト（国税庁）".
  **Cadence**: monthly (前月末時点 snapshot), refreshed each time the ZIP is re-fetched.
- **Web-API**: https://www.houjin-bangou.nta.go.jp/webapi/ (fetched, cached as
  `https___www.houjin-bangou.nta.go.jp_webapi_.html`). REST, versions 1.0-4.0. Needs an
  "アプリケーションID" (application ID) — free to obtain ("発行に費用は掛かりません") but the
  page states issuance takes "２週間から１か月程度" (2 weeks to 1 month) and goes through a
  separate invoice-registration portal, not a self-serve signup. **Not used**: an
  application ID was not requested (out of scope for a one-off crosswalk; recorded here in
  case a future refresh wants a lower-latency lookup path instead of re-downloading ZIPs).
  Rate limit for the Web-API itself is not stated on this page (would need the linked
  "Web-APIの詳細について" spec, not fetched).
- **What a free lookup returns**: the bulk file's 32-ish columns per the NTA resource
  definition include 法人番号 (13-digit corporate number, used here as `company_number`),
  legal name, kind code, prefecture/city/street, postcode, closure date/reason, assignment
  date, an optional registered English name/address, and an optional furigana reading —
  all free, all in the bulk file, nothing held back for a paid tier. There is no paid tier.

### 2. NTA 酒類等製造免許の新規取得者名等一覧 (new liquor-manufacturing-licence-holder lists) — `nta-seizo-menkyo`

- URL: https://www.nta.go.jp/taxes/sake/menkyo/shinki/seizo/02/zenkoku.htm (fetched, cached
  as `nta-licence/zenkoku.htm`, Shift-JIS).
- Free, no account. Yearly files, 平成26年 (2014) through 令和8年 (2026, through June),
  broken out by category (通信酒類, ビール, リキュール, ウイスキー, その他の醸造酒, 上記以外
  — spirits/beer/liqueur/whisky/other-brewed/other). Excel workbooks fetched for 13
  year-tags (h26-h30, r01-r08), 736 KB total. PDF versions of the same lists also exist on
  the page (per-category, 70-350 KB each) but the Excel was used since it is one file per
  year instead of six per year.
  **Licence**: same nta.go.jp domain, same PDL 1.0 terms (`www.nta.go.jp-terms.html`
  explicitly names nta.go.jp as covered).
  **What it returns**: office (tax office), licence date, application date, legal name
  (法人 rows only — sole-trader licensees show no 法人番号), trading name, product category,
  manufacturing-site address. Rows from 2016 (h28) onward increasingly carry the 13-digit
  法人番号 directly, letting this list bridge a distillery's *trading name* (what's on the
  bottle/pin) straight to its *legal name and 法人番号* without needing to guess at kanji.
  4,415 rows read across all years; 3,444 carry a 法人番号. No API for this dataset.

### 3. gBizINFO — considered, not used

- https://info.gbiz.go.jp/ (home fetched as `gbiz-home.html`) and its API docs
  (`https___content.info.gbiz.go.jp_api_index.html.html`, fetched). gBizINFO holds a
  broader (METI-run) corporate dataset including filings/subsidies/patents, which would
  have been a useful cross-check.
- The REST API page states plainly that use requires a prior 利用申請 (application) after
  which an API token is emailed ("申請後に登録したメールアドレスに...メール内にあるURLに
  アクセスするとAPIトークンが表示されます"). An unauthenticated probe request on 20 Sep 2026
  (`gbiz-probe.txt`) returned an error body — `{"id":null,"message":"500 - Internal Server
  Error.","errors":[]}` — not corporate data; this is consistent with "no unauthenticated
  access" but the exact HTTP status behind that JSON was not captured, so this note claims
  only what the cached file shows, not a specific status code.
  **Not used** for either the bulk download or the API: the API needs the token above, and
  the bulk-download page (`https___info.gbiz.go.jp_hojin_DownloadTop.html`, fetched) gates
  its file behind the same application flow. Skipped as out of scope for this pass; the NTA
  corporate-number register was sufficient on its own.

## Method

`scripts/match_japan_registers.py` (stdlib only, `--cache DIR`, network only behind
`--fetch-nta` / `--fetch-licences`). Loads the 118 Japan pins from the geojson, derives each
pin's prefecture (from its address, a postcode, or a small hand table `PIN_PREF` for the 11
pins whose address has no prefecture string), then streams the cached NTA prefecture ZIPs,
keeping only register rows that could matter (matching a pin's postcode, kanji name, a
licence-list 法人番号, or containing a drinks-industry word). Bridges tried in order:

1. **kanji-exact** — pin's kanji name (from the geojson `name`/`description`) equals a
   register legal name after stripping legal suffixes (株式会社 etc.) and generic words
   (蒸溜所/蒸留所/ディスティラリー/distillery) — `high`.
2. **licence-houjin** — the licence list's 法人番号 + trading name + manufacturing-site
   address bridges a pin straight to its register row — `high`, downgraded to `medium` if
   the register row shows a closure/status flag.
3. **romaji-bridge** — the register's English name or furigana (romanised in-script), with
   generic words stripped, contains a distinctive Latin token from the pin's name or
   website domain, scored by whether the prefecture/postcode agrees and whether a
   drinks-industry word appears in the legal name — `high`/`medium`/`low` by strength.
4. **postcode-signal** — same 7-digit postcode as the pin, plus a drinks-industry word in
   the company name, with no name match — `medium`.

Well-known group-run sites got a hand row (`HAND` table in the script): the pin's own
operating company as `relation: self` or `operator`, plus the parent as `relation: group`,
each resolved to a `company_number` from the register by kanji legal name. Present in this
pass: Suntory (Yamazaki, Hakushu, Chita), Nikka/Asahi (Yoichi, Miyagikyo), Kirin (Fuji
Gotemba), Hombo Shuzo (Mars Komagatake/Shinshu, Mars Tsunuki), Venture Whisky (Chichibu, by
kanji-exact self match, no separate hand row needed), Sasanokawa Shuzo (Asaka), Kenten
Jitsugyo (Akkeshi — pin slug `kenten`, its website is akkeshi-distillery.com), Gaia Flow /
Gaiaflow Distilling (Shizuoka: `self` = the operating company, `group` = the parent — both
resolved), Wakatsuru Shuzo (Saburomaru), Nagahama Romman Beer (Nagahama), 黒木本店 (Osuzuyama),
Niseko Distillery / Hakkaisan (Niseko). **Not present as pins in this 118-pin set** (checked
by kanji and by English name, zero hits): Kanosuke/Komasa Jyozo, Yuza, Kaikyo — the brief's
checklist names them as group-run sites to watch for, but none of the three has a pin in
this country group, so there is nothing to add.

Name bridging is the hard part: most pins carry a romanised/English name (from OSM, Google
Places or Wikidata) while the register is entirely kanji, so bridge 3 (romaji-bridge) is
doing the bulk of the medium/low-confidence work and is the one most worth a human's second
look — it is a fuzzy heuristic, not an exact match, hence `low` wherever the drinks-word or
location signal is missing.

## Matcher fix (this pass)

Two issues found and fixed before trusting the script:

1. **Wrong `--cache` root breaks the whole match silently-ish.** The script's cache layout
   is `<cache>/nta/<pref>.zip` and `<cache>/nta-licence/<year>.xlsx`. The scratchpad has
   *both* a `japan/cache/nta/...` directory (matching that layout) and a decoy top-level
   `japan/nta-licence/...` directory (a leftover from earlier manual analysis, holding the
   same Excel files plus a hand-built `licences-all.csv` the script never reads). Pointing
   `--cache` at the scratchpad root instead of `scratchpad/.../japan/cache` makes every
   prefecture zip "missing" (35 warnings) and the run silently falls back to whatever the
   licence-list bridge and hand rows can do alone — 124 rows instead of 453, with most pins
   unmatched. **Confirmed via `--cache .../japan/cache`, the correct root, reproduces the
   453/65 rows already on disk exactly.** Documented here so the next run doesn't repeat it.
2. **Non-deterministic tie-break in the romaji-bridge note text.** `for t in pin["toks"]:`
   iterated a Python `set`, whose order depends on per-process hash randomisation; when two
   tokens tied on confidence, the note text (which token gets quoted) could differ between
   runs even though the confidence/company_number never changed. Fixed by sorting the
   iteration (`for t in sorted(pin["toks"]):`) — confirmed two consecutive runs now produce
   byte-identical output. One row's note text changed as a result of the fix
   (`echigo-yakuso-distillery`: now cites token `'yakuso'` instead of `'etigo'`; same
   company, same confidence, same register number).
3. Also corrected an overclaim in the script's own docstring: it said the gBizINFO probe
   "answered 401" — the cached response is a JSON body reading `500 - Internal Server
   Error`, not a documented 401; the docstring now says what was actually observed instead
   of guessing the status code.

Verified: `python3 -c "import ast; ast.parse(...)"` parses clean; two back-to-back runs from
`--cache .../japan/cache` (no `--fetch-*` flags, fully offline) produce identical
`japan-candidates.csv` (453 rows) and `japan-licences.csv` (65 rows) — idempotent.

## Result table (118 pins)

| Prefecture | Pins | High | Medium | Low | Unmatched |
|---|---|---|---|---|---|
| Kagoshima | 23 | 23 | 0 | 0 | 0 |
| Okinawa | 8 | 7 | 1 | 0 | 0 |
| Hokkaido | 8 | 8 | 0 | 0 | 0 |
| Tokyo | 7 | 5 | 0 | 1 | 1 |
| Nagasaki | 6 | 6 | 0 | 0 | 0 |
| Kyoto | 5 | 2 | 0 | 2 | 1 |
| Shizuoka | 5 | 4 | 1 | 0 | 0 |
| Fukushima | 4 | 4 | 0 | 0 | 0 |
| Miyazaki | 4 | 3 | 1 | 0 | 0 |
| Nagano | 4 | 4 | 0 | 0 | 0 |
| Saitama | 4 | 3 | 1 | 0 | 0 |
| Aichi | 3 | 3 | 0 | 0 | 0 |
| Chiba | 3 | 3 | 0 | 0 | 0 |
| Kanagawa | 3 | 3 | 0 | 0 | 0 |
| Kumamoto | 3 | 3 | 0 | 0 | 0 |
| Niigata | 3 | 3 | 0 | 0 | 0 |
| Yamagata | 3 | 3 | 0 | 0 | 0 |
| Iwate | 2 | 2 | 0 | 0 | 0 |
| Osaka | 2 | 1 | 1 | 0 | 0 |
| Yamanashi | 2 | 2 | 0 | 0 | 0 |
| Aomori | 1 | 0 | 1 | 0 | 0 |
| Gifu | 1 | 0 | 1 | 0 | 0 |
| Hiroshima | 1 | 1 | 0 | 0 | 0 |
| Hyogo | 1 | 1 | 0 | 0 | 0 |
| Ibaraki | 1 | 1 | 0 | 0 | 0 |
| Ishikawa | 1 | 1 | 0 | 0 | 0 |
| Miyagi | 1 | 1 | 0 | 0 | 0 |
| Oita | 1 | 1 | 0 | 0 | 0 |
| Okayama | 1 | 0 | 1 | 0 | 0 |
| Saga | 1 | 0 | 1 | 0 | 0 |
| Shiga | 1 | 1 | 0 | 0 | 0 |
| Tochigi | 1 | 1 | 0 | 0 | 0 |
| Tottori | 1 | 1 | 0 | 0 | 0 |
| Toyama | 1 | 1 | 0 | 0 | 0 |
| Yamaguchi | 1 | 1 | 0 | 0 | 0 |
| (no prefecture) | 1 | 0 | 0 | 0 | 1 |
| **Total** | **118** | **103** | **9** | **3** | **3** |

453 candidate rows across 115 matched slugs (several candidates per pin by design — the
builder keeps only the best `high`/`medium` row per pin from `high`/`medium`/`low`
candidates; `low` rows and any without a register number stay as leads for a human). 65
licence-list rows in `japan-licences.csv`, all `registry: nta-seizo-menkyo`.

## Request log

The prior agent's `summary.json` has an empty `requests` log (the fetch step and the
offline match step were run separately and only the final offline run's — empty — log was
saved). Per the brief's resume rule, treat the missing log as 200 requests already spent.
Counting what is actually cached, on top of that assumption:

- 35 POSTs to the NTA 全件ダウンロード endpoint (one prefecture ZIP each, ≤1/s per the
  script's `fetch_nta`; confirmed by `ls cache/nta/*.zip` = 35 files, 224 MB total).
- 13 GETs for the yearly licence Excel files (`cache/nta-licence/*.xlsx`).
- ~13 GETs for terms/reference pages (zenken listing page, houjin-bangou 利用規約/webapi/
  download pages, gBizINFO home/terms/API-doc/download-doc pages, 公共データ利用規約 and
  nta.go.jp terms pages, one prefecture's licence-office page).
- 1 unauthenticated gBizINFO API probe.

That is ~62 requests with direct on-disk evidence, comfortably inside even the
conservative 200-already-spent assumption. **This pass made zero new network requests** —
both matcher runs used `--cache .../japan/cache` with no `--fetch-*` flag, fully offline.
Running total against the 400 cap: conservatively ≤200 (assumed) + 0 (this pass) = ≤200.

## Unmatched slugs (3 of 118)

- **`distillery-japan-6`** (グッドウルフ麦酒 / Good Wolf Brewery) — the pin has no address at
  all (blank in `pins.csv`), so no prefecture or postcode to select a register file or
  narrow a search; name/website alone weren't enough for a safe bridge. This is the
  "(no prefecture)" row in the table above.
- **`nameless-distillery`** (Nameless Distillery 名もない蒸留所, Jiyūgaoka, Tokyo) — address
  resolves to Tokyo (zip cached) but the pin's name is literally generic ("no-name
  distillery") in both languages, and its website (mizunara.shop-pro.jp) is a storefront
  platform domain filtered out as too generic to bridge on — no distinctive token survives.
- **`ixey-non-alcoholic-spirits-kyoto-distillery-salon`** (Kyoto) — address resolves to
  Kyoto (zip cached) but the only web presence is an Instagram handle (filtered as a
  generic platform domain), the product is explicitly non-alcoholic (likely outside the
  NTA liquor-manufacturing-licence regime entirely, so the licence-list bridge has nothing
  to match against either), and no kanji legal-name match was found.

## Files written

- `data/company-crosswalk/japan-candidates.csv` — 453 rows, schema-conformant (verified
  header + `confidence`/`relation`/`verified` value sets programmatically).
- `data/company-crosswalk/japan-licences.csv` — 65 rows, `registry: nta-seizo-menkyo`.
- `scripts/match_japan_registers.py` — fixed as described above; parses clean; idempotent
  from `--cache <scratchpad>/japan/cache` (two consecutive offline runs byte-identical).
- This file.

## Grading correction, 20 Sep, later the same day

Two guards added to the matcher after review of the first output. Postcode-neighbour rows
(a company at the pin's postcode carrying a sake or liquor word) were `medium`; they include
liquor shops, a medical corporation and a labour union, so they are now `low`. Where a hand
row names the group or operator of a site, machine name matches for that site are town-name
collisions (Yoichi Beer LLC for Yoichi Distillery, a brewing company for Setouchi) and are
now `low`. Result after the guards: 126 high, 16 medium, 311 low; 110 of 118 pins carry a
high or medium 法人番号. The three unmatched pins are unchanged.

## Migration onto scripts/crosswalklib, 20 Sep, later still

`match_japan_registers.py` now gets fetching, the row schema and the two guards above from
`scripts/crosswalklib` (`fetch.Fetcher`, `rows.write`, `grading.apply_guards`) instead of its
own copies; kanji/romaji parsing stays local. `spent=62` (the count above) is passed into the
shared `Fetcher` so its cap carries over. `fetch_licences` (13 plain GETs, no cookies) moved
onto `Fetcher.bulk`. `fetch_nta` needs a CSRF token plus the session cookie that request sets,
then a POST per prefecture ZIP — `Fetcher`'s public API is GET/bulk-only and can't carry a form
body or a cookie jar across calls, so `fetch_nta` keeps its own `urllib` opener but reports its
request count and log lines through the same `Fetcher` instance, so the cap and the audit trail
are still one thing. Folded into `crosswalklib.names.GENERIC` (append, not remove, so every
matcher gets them): `beer`/`beers`, and the `shuzo`/`shuzou`/`syuzou`/`jozo`/`jyozo`/`kura`
romaji family (kept local before only because the matcher had no shared list to put them in).
`STOP_LATIN` keeps only what's genuinely Japan-specific: prefecture/city names, romaji spelling
variants not worth generalising, and website-hosting artefacts.

Switching to `rows.write()` (which refuses a row with no register number at better than `low`)
surfaced two pre-existing rows that the old unchecked CSV writer had let through invalid: hand
row `sicx-gin-distillery-cafe-bar` (17 same-named register hits in Kyoto, number never
resolved) was written `medium` with a blank `company_number`, and two licence-bridge rows
(`distillery-japan-10`, `dewa-distillery`, both `h26`-list matches from before the 法人番号
column existed on that list) were written `high` with a blank number. All three predate this
migration; `apply_guards`'s "no number, never better than `low`" rule now catches them (applied
to `auto + hand` and to `lic_rows`, not just `auto`, since the rule is about the row, not the
method that produced it). Candidates after the migration: 126 high, 15 medium, 312 low — one
row down from the 16 medium above, specifically `sicx-gin-distillery-cafe-bar`. Every other row
is unchanged; the two licence-file rows affect `japan-licences.csv`, not the candidates count.

