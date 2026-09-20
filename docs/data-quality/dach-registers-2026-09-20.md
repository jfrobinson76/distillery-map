# Germany, Austria, Switzerland: company registers and licence lists for the crosswalk, 20 September 2026

Research for the DACH leg of `data/company-crosswalk/`. The map has 939 pins with
`country` in `Germany` (696), `Austria` (153), `Switzerland` (90). No address parsing was
needed for province/canton the way Canada needed it; city is pulled from the free-text
`address` field per pin.

Every "free / bulk / API / licence" claim below comes from a page or dataset this pass or
the previous pass actually fetched (cached in the scratchpad `dach/` folder); the URL is
cited next to each claim. Two pages fetched turned out to be client-side JS shells with no
readable terms in the saved HTML (`hr_*.xhtml` from handelsregister.de/Registerportal) —
that is flagged explicitly below rather than quoted from memory.

## Summary

No DACH country publishes a free bulk company register with a commercial-use licence.
The crosswalk instead uses three second-best free sources, one per country, each matched
locally with no live queries against the pin data itself (Germany and Switzerland) or a
small number of cached/rate-limited name searches (Austria):

- **Germany** — `offeneregister.de`, a 2017-2019 snapshot of the Handelsregister scraped
  and republished by OpenCorporates/Open Knowledge Foundation Deutschland under
  **CC-BY 4.0**. Not current, not authoritative, cannot be called "Handelsregister" data
  under §8.2 HGB, but free, bulk, and reusable.
- **Austria** — the JustizOnline **Firmenbuchabfrage** free name search (no bulk, no API,
  hard undocumented rate limit hit at ~100 requests), cross-checked against Statistik
  Austria's free CC-BY 4.0 **FN → ÖNACE** classification list to flag every company coded
  11.01 "Herstellung von Spirituosen".
- **Switzerland** — **Zefix** core data (legal name, UID, seat, purpose) pulled in bulk,
  free, from the federal government's own **LINDAS** linked-data endpoint under an
  opendata.swiss **"terms_by"** licence (free use, commercial included, attribution
  required) — a materially better route than the Zefix web app or its paid-account REST
  API.

A fourth, non-register source — BAZG's (Swiss customs) published PDF list of
**Lohnbrennereien** (contract distillers) — is used as a licence/industry layer to catch
Swiss small producers who have no Handelsregister entry of their own.

Germany and Austria have **no public bulk producer-licence list at all**: Germany's
federal Branntweinmonopol (which would have been the natural licence layer) was abolished
in 2018 (`bfb.html`, a secondary source, corroborates the date; the Zoll pages fetched,
`zoll_herst.html` etc., describe current excise procedure but publish no producer list),
and Austria's OENACE list only names FNs classified 11.01, not addresses or trading names
outside the Firmenbuch itself.

## Company registers

| Country | Register | Free lookup | Bulk / open data | API | Paid | Used |
|---|---|---|---|---|---|---|
| Germany | Handelsregister (official), handelsregister.de / Registerportal der Länder | Yes, name/place search, but capped and restrictive per the site's own Nutzungsordnung. The cached pages (`hr_welcome.xhtml`, `hr_normalesuche.xhtml`, `hr_nutzungsordnung.do`, `hr_information_nutzungsordnung.xhtml`) are all client-rendered PrimeFaces shells — the saved HTML has no readable terms text without executing JavaScript, so the specific "60 searches/hour, no systematic retrieval" figure quoted in `scripts/match_dach_registers.py` is the well-documented public description of this site's Nutzungsordnung, **not confirmed from the cached copy of the page itself**; treat it as reputable prior knowledge, not a page-read fact, until re-fetched with a JS-capable tool. | No bulk file (confirmed via the OffeneRegister README, see below: OpenCorporates explicitly could not get a licence to redistribute Handelsregister or Unternehmensregister data). | None public | Certificates, extracts (fees not itself checked; out of scope, register not queried) | **Not queried at all** — zero requests against handelsregister.de |
| Germany | Unternehmensregister, unternehmensregister.de (Bundesanzeiger Verlag) | Yes, name search (`ureg.html`, fetched: "Firmenname / EUID … Schnellsuche") | No — the OffeneRegister README (`or_daten.html`) states this register has "adverse terms of use that restrict OpenCorporates from publishing the data" | None found | Filing retrieval fees (site mentions a "Publikations-Plattform" for submitting filings; fee schedule not checked) | **Not used**, not queried beyond the one homepage fetch |
| Germany | offeneregister.de (OKFN Deutschland / OpenCorporates republication of Handelsregister data) | Yes, web search on the site (`offeneregister.html`) | **Yes.** `https://daten.offeneregister.de/de_companies_ocdata.jsonl.bz2` (260,455,433 bytes / 260 MB, also offered as a `.torrent`). **Licence: CC-BY 4.0**, attribution to OpenCorporates (`or_daten.html`, the dataset README, fetched in full: "we … make this available under the Creative Commons Attribution Licence 4.0"). Coverage: "collected by OpenCorporates mainly in the period from June 2017 to January 2019 … from the Handelsregisterbekanntmachungen and to a lesser extent the Handelsregister … for over 5,000,000 companies." Legal notice in the same README: per §8.2 HGB (German Commercial Code) this dataset **must not be circulated calling itself "Commercial Register" / "Handelsregister"**. Local filter kept 1,212,386 of 5,305,727 records sharing a token with a DACH pin name; 1,079,689 survived the keyword pre-filter before the final per-country match. | None (static dump only) | N/A | **Used** — this is the entire German match surface. Snapshot is 7+ years stale; status/address reflect 2017-2019, not today |
| Germany | OpenCorporates.com (hosts the same records, individual company pages) | Yes, web search; individual company URLs used as the `source` column for DE rows (`https://opencorporates.com/companies/de/{number}`) | Same bulk file as above; OpenCorporates' own terms (`oc_terms.html`, `oc2.html`, `oc3.html`, fetched but not deep-read this pass) additionally require attribution for reuse of their site/API beyond the CC-BY bulk file | Yes, opencorporates.com API exists but was not queried (out of scope; not needed once the bulk file is filtered locally) | API tiers exist (not itemised here) | Only used as a static citation link, not queried |
| Austria | Firmenbuch (official register) via JustizOnline Firmenbuchabfrage, https://justizonline.gv.at/jop/web/firmenbuchabfrage | **Yes**, free. `JOP_SEARCH` (`https://justizonline.gv.at/jop/service/fba/search?term=…`) returns name, FN, status, Sitz; `JOP_DETAIL` (`https://justizonline.gv.at/jop/service/fba/{id}`) adds legal form and address. Confirmed from the live FAQ content fetched at `jop_faq1.json`: "Über unseren digitalen Service **Firmenbuchabfrage** können Sie Teilauszüge (PDF) kostenlos herunterladen" (free partial extract). | None | The `search`/detail endpoints above are the closest thing to an API; **undocumented, no published rate limit**. Empirically: the server started answering HTTP 429 after roughly 100 requests in the previous pass's run (`run_jop.log`: 237 consecutive 429s logged after 100 successful, cached calls). No further live requests were made this pass to preserve the cap. | **Confirmed from `jop_faq1.json`**: "Aktueller Firmenbuchauszug EUR 4,89"; "Aktueller Firmenbuchauszug mit historischen (gelöschten) Daten EUR 8,20"; "Urkunden je EUR 1,52" (documents — annual accounts, specimen signature, articles of association). Payment via Visa/Mastercard/EPS. | Free search used, cached; paid extracts not purchased |
| Austria | Statistik Austria open data — "Firmenbuchnummer ÖNACE Zuordnung" (FN → industry classification) | N/A (bulk file, not a lookup) | **Yes.** `OGDEXT_HVD_FBNR_OENACE_1.csv`, catalogue page https://www.data.gv.at/katalog/datasets/456ce845-5d87-3877-bc0e-33c5371c7aa7, confirmed from the fetched dataset metadata page (`at_oenace_stat.html`): **Licence "Creative Commons Namensnennung 4.0 International"** (CC-BY 4.0), update frequency **monatlich** (monthly), first published 16.01.2026, last updated 02.09.2026, identifier `456ce845-…`. Population: "alle aktiv im Firmenbuch eingetragenen Unternehmen mit aktiv zugeordneter Wirtschaftstätigkeit" (every FN with an assigned ÖNACE code) — 326,871 rows in the cached copy, 151 coded 11.01 "Herstellung von Spirituosen". Two columns only: `FB_NUMMER`, `OENACE_ZUORD` — **no company name, no address**, so it is a filter layer on top of a name search, not a standalone identifier. | None | N/A | Used to flag which FN hits are spirits producers (`purpose_ok` in the matcher) |
| Austria | Unternehmensserviceportal (USP), usp.gv.at — general Firmenbuch background | Yes, informational only | N/A | N/A | N/A | Background reading only (`at_usp2.html`); no data extracted |
| Switzerland | Zefix (Zentraler Firmenindex), the federal EHRA's public company index | Yes, free web search at zefix.admin.ch (`zefix_home.html`) | **Yes**, via the **LINDAS** linked-data service — see below | **Zefix Public REST API** exists (`https://www.zefix.admin.ch/ZefixPublicREST/`, OpenAPI spec fetched at `zefix_openapi.json`) but **requires a registered account/subscription key**; not used. The web app's own backend was not scraped: not itself checked for a robots.txt block this pass, but the matcher's stated reason (site's own JS bundle, `zefix_main.js`, fetched but not parsed for a disallow rule) is carried over from the prior pass and should be re-verified before relying on it as a hard block. | Extracts via the register office (not itemised; register not queried directly) | Used via LINDAS bulk pull, see next row |
| Switzerland | Zefix core data via LINDAS (Swiss Linked Data platform, opendata.swiss) | N/A (SPARQL, not a per-company lookup) | **Yes.** Dataset "Zefix - Zentraral Firmenindex", published by the Eidgenössisches Amt für das Handelsregister (EHRA), catalogue page https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex (`ods_zefix_ds.html`, fetched: "Bestandsdaten … Firma/Name, Sitz und Domiziladresse", "tagesaktuelle Kerndaten" — daily-fresh). **Licence: opendata.swiss "terms_by"** badge, confirmed from the fetched terms page (`ods_terms.html`) and the dataset page markup (`ods_zefix_ds.html`, badge text "Quellenangabe ist Pflicht"): free use, commercial and non-commercial, attribution to source required. Metadata page shows "Zuletzt aktualisiert: 21. März 2022" for the catalogue *record*, but the SPARQL graph itself is served live from EHRA's system of record (core data fields only: legal name, UID, address, legal form code, Zweck/purpose text). | `https://lindas.admin.ch/query` — free public SPARQL endpoint, no auth, no published rate limit found on the fetched pages. Pulled in 32 pages of 25,000 rows (page size capped at `LINDAS_PAGE=25000` to avoid gateway timeouts; several 504s were hit and retried with backoff, see request log). | N/A | **Used** — 793,738 entities indexed, 7,242 with a distilling/spirits-purpose Zweck text |
| Switzerland | BFS (Bundesamt für Statistik) Unternehmensregister (BUR), the Swiss *statistical* business register | Search UI exists (`bur.html`, fetched: "Unternehmensregister — Bundesamt für Statistik", mentions LEI) | Not established this pass — this is a statistics register (BUR), a different system from Zefix; not pursued once Zefix/LINDAS proved sufficient | Not checked | Not checked | **Not used** |
| Switzerland | UID register, unternehmensregister.de-equivalent is not applicable here — `ureg.html` in the cache is actually the **German** Unternehmensregister (see the Germany table above), not a Swiss source. Corrected from the prior pass's file naming. | — | — | — | — | (mislabelled file, no Swiss content) |

## Licence / industry lists (second identifier layer)

| Country | List | Legal name? | Notes |
|---|---|---|---|
| Switzerland | BAZG (Bundesamt für Zoll und Grenzsicherheit) "Adressliste Lohnbrenner", https://www.bazg.admin.ch/dam/de/sd-web/7m2WSkYkaDRN/Adressliste%20Lohnbrenner_07_2026_DE.pdf | **Yes**, Nachname/Vorname or firm name, plus PLZ/Ort/Kanton | PDF, Stand 01.07.2026, converted once to text with `pdftotext -layout` (292 rows parsed). This is the **Kleinproduktion** contract-distiller list (BAZG's own page `ch_konzession.html`, fetched: producers under 200 L pure alcohol/year "profitieren von steuerlichen Vergünstigungen. Die Herstellung der Spirituosen erfolgt in einer Lohnbrennerei"). It is **not** a list of concession-holding commercial distillers (the larger "Gewerbeproduktion" tier, >200 L/year, which needs a Brennereikonzession under Art. 3 AlkG) — no open list of those concessions was found. Licence for the PDF itself is not stated on the fetched BAZG pages; treated as a public government publication, flagged here as a licence call for John if the crosswalk is ever used commercially at scale. |
| Switzerland | BAZG "Alkohol" / "Inlandproduktion" pages, https://www.bazg.admin.ch (`ch_alkohol.html`, `ch_konzession.html`) | N/A, background only | Confirms three production tiers (Gewerbe-, Klein-, landwirtschaftliche Produktion) and mentions a "Spirituosenregister" by name without linking it; that register was not located or fetched this pass — a gap, not a rejection. |
| Austria | Statistik Austria FN→ÖNACE list | No (FN only) | See company-register table above; used as the licence/industry layer for Austria since no separate producer-permit list is public |
| Germany | — | — | **No producer-licence list exists.** The federal Branntweinmonopol/Bundesmonopolverwaltung für Branntwein, which would have been the natural licence register, was wound down after ~100 years (secondary source `bfb.html`, a third-party news article, not a primary source — flagged as such). Current German Zoll (customs) pages on "Gewerbliche Herstellung von Alkohol" (`zoll_herst.html`, `zoll.html`, `zoll2.html`, `zoll3.html`, `zoll_abf.html`) describe excise procedure but publish no open producer list. |

## Method

`scripts/match_dach_registers.py` (stdlib only; network only behind `--fetch-lindas` /
`--fetch-justizonline`; `--build-de-subset` filters the already-downloaded bz2 locally,
no network):

1. **Germany** — pin name (plus a short hand-curated alias list for renamed/trading-name
   sites) token-matched against the OffeneRegister subset. Token Jaccard + city/postcode
   agreement against the registered office; drinks-word signal required for weak/partial
   matches; `high` needs an exact name or Jaccard ≥ 0.8 with location agreement or a
   distinctive name; snapshot status "currently registered" (2017-2019) required for
   `high`, otherwise capped at `medium`.
2. **Austria** — two passes: (a) local match against the 151 FNs coded ÖNACE 11.01 (no
   network), (b) JustizOnline free-text name search, full pin name first, distinctive
   tokens as a fallback only when nothing else is cached. Same Jaccard/city/purpose
   scoring as Germany, plus an OENACE-code purpose bonus.
3. **Switzerland** — pin name matched against the LINDAS Zefix core-data index the same
   way, plus a Zweck (purpose) text signal (`PURPOSE_RE`, matches "destill/brennerei/
   spirituos/whisk/…" etc. in the German-language purpose clause). Separately, the BAZG
   Lohnbrenner list is matched to catch pins whose named distiller is a contract producer,
   emitted to `dach-licences.csv`; where that name also resolves to a Zefix legal entity,
   a bridged `ch-zefix` candidate row is added too.
4. **Hand rows** — six group-run or renamed sites (Weinbrennerei Wilthen → Hardenberg-
   Wilthen AG; Schlichte Brennerei → Schwarze und Schlichte GmbH; Slyrs → SLYRS
   Destillerie GmbH & Co. KG; Säntis Malt → Brauerei Locher Aktiengesellschaft; Diwisa →
   DIWISA AG; Pfau Brand → Vereinigte Kärntner Brauereien AG). This pass re-verified every
   number against the cached source data (see "Hand-row fixes" below) rather than
   trusting the previous pass's entries.

## Hand-row fixes made this pass

The previous pass left three hand rows with a blank `company_number`, to be filled "when
present" by an auto-match that never fired (the auto-fill only triggers on an exact
company-name match among the machine-generated rows for the same slug, and none of these
three group companies share a name token with their distillery's pin name, so the
auto-fill loop never ran for them). Checked each directly against the cached bulk data
instead of inventing a number:

- **Säntis Malt → Brauerei Locher Aktiengesellschaft.** Found in the LINDAS Zefix dump:
  `CHE101250882`, Appenzell, Brauereiplatz 1, 9050 (`register.ld.admin.ch/zefix/company/
  457869`). Filled `CHE-101.250.882`; corrected the company name from the informal "AG"
  short form to the register's actual "Aktiengesellschaft".
- **Diwisa → DIWISA AG** (was recorded as "DIWISA Distillerie Willisau SA"). The current
  Zefix extract has no entity by that exact name; the current legal entity is **DIWISA
  AG**, `CHE101803195`, Willisau, Menznauerstrasse 23 (`register.ld.admin.ch/zefix/
  company/45938`), Zweck: "Fabrikation von und Handel mit Getränken aller Art,
  insbesondere Spirituosen und Likören". The old name survives only inside a linked
  pension foundation's name, "Personalfürsorgestiftung der Diwisa Distillerie Willisau
  SA" (`CHE109768645`) — evidence the company was renamed at some point, not evidence of
  the current legal name. Filled `CHE-101.803.195` and corrected `company_name`.
- **Pfau Brand → Vereinigte Kärntner Brauereien AG.** Not found in any cached source:
  absent from the Statistik Austria FN→ÖNACE list (breweries aren't coded 11.01) and no
  JustizOnline name search for it is cached. Rather than guess an FN, **left
  `company_number` blank** and rewrote the note to say so explicitly. A live JustizOnline
  search would resolve it in one request but was not spent this pass (see request budget,
  below).

`weinbrennerei-wilthen` (Göttingen früher Northeim HRB 130424 → Hardenberg-Wilthen
Aktiengesellschaft) and `schlichte-brennerei` (Münster HRB 12037 → Schwarze und Schlichte
GmbH) were checked the same way and were already correct verbatim against the cached
`de-offeneregister-subset.jsonl` — no change needed. `slyrs` (München HRA 82320) was
already correct and duplicates a machine-found row exactly, so only the hand row survives
the dedup.

## Result table

| Country | Pins | High | Medium | Low | Unmatched |
|---|---:|---:|---:|---:|---:|
| Germany | 696 | 56 | 12 | 14 | 614 |
| Austria | 153 | 8 | 1 | 3 | 141 |
| Switzerland | 90 | 37 | 3 | 10 | 40 |
| **Total** | **939** | **101** | **16** | **27** | **795** |

167 candidate rows in `dach-candidates.csv` (some pins carry more than one candidate;
`rank_and_emit` keeps up to 3 per pin, dropping `low` once a `high` exists). 34 licence
rows in `dach-licences.csv` (all `ch-bazg-lohnbrennerei`, contract distillers, not a
register number). Confidence split across all candidate rows: 106 high / 30 medium / 31
low. Registry split: 101 de-offeneregister, 52 ch-zefix, 14 at-firmenbuch.

## Request log

All fetching happened in the previous pass; this pass made **zero new network requests**
(everything below is a re-count of what's already in the cache/logs, done to stay honest
about the running total against the 400 cap per the resume instructions).

| Endpoint | Requests | Notes |
|---|---:|---|
| JustizOnline `search`/`detail` (`justizonline.gv.at/jop/service/fba/…`) | 337 | 100 succeeded (cached in `justizonline-cache.json`, all reused this pass, 0 new); 237 hit HTTP 429 and were never answered (`run_jop.log`, no data cached for those terms — a retry would cost a fresh request each) |
| LINDAS SPARQL (`lindas.admin.ch/query`, Zefix pages) | 32 | 4 attempts in an earlier run that crashed on a 504 gateway timeout after page 3 (`run_lindas.log`); 28 successful paged requests in the run that completed (`run_lindas2.log`, 793,738 rows across 32 pages) |
| One-off probe/terms/metadata pages (handelsregister.de, offeneregister.de, OpenCorporates, data.gv.at, Statistik Austria, JustizOnline FAQ, Zefix web app + OpenAPI spec, opendata.swiss, BFS, USP, German Zoll) | ~65 files cached | Each a single GET, not rate-limited (informational pages, not search endpoints) |
| OffeneRegister bulk file download (`daten.offeneregister.de/de_companies_ocdata.jsonl.bz2`) | 1 | 260 MB, one download, filtered locally afterwards with zero further network calls |
| BAZG Lohnbrenner PDF | 1 | One download, converted locally with `pdftotext` |

Running total against the 400-request cap: 337 (JustizOnline) + 32 (LINDAS) + ~65
(one-off probes) + 2 (bulk downloads) ≈ **436**. This **exceeds** the stated 400 cap. The
overrun happened in the previous pass, before this resume; it is disclosed here rather
than hidden, per the rule to count every prior request against the cap. Consequence for
this pass: **no further live requests were made** anywhere (Pfau Brand's FN was left
unresolved rather than spending one more JustizOnline call) and none should be made by a
future pass without John's sign-off to re-baseline the cap. The bulk-download and
one-off-probe categories are arguably a different kind of request than the "≤ 1
request/second on any search endpoint" rule was aimed at (the rule's own wording is
"search requests"), but the totals are reported without that carve-out so the number
can't be read as understating usage.

## Unmatched slugs, grouped by reason

795 unmatched pins in the candidates count (791 once the 4 Swiss pins that only landed in
`dach-licences.csv` are folded in). Listing all 795 individually would not be useful; the
matcher's own stderr output has the full slug list (`python3 scripts/match_dach_registers.py
--cache <dir>` prints it on the last line). Grouped by the most likely reason, from the pin
name alone:

| Country | No legal-form marker, no sole-trader word in the name (still almost certainly a small unregistered operator — the name just doesn't say so) | Explicit sole-trader/farm-distiller word (Obstbrennerei, Hofbrennerei, Hausbrennerei, Privatbrennerei, Abfindungsbrennerei, Lohnbrennerei, Kleinbrennerei, Landbrennerei, Streuobst…) | Hospitality/farm-shop word (Gasthof, Gasthaus, Hotel, Pension, Weingut, Mosterei, Kelterei, Hofladen, Imkerei…) — likely trades under a personal or trade name not in any register at all | Carries GmbH/AG/KG/UG/OHG/e.K./e.U./SA/Sagl in the pin name itself, still unmatched |
|---|---:|---:|---:|---:|
| Germany | 480 | 65 | 41 | 28 |
| Austria | 114 | 11 | 6 | 10 |
| Switzerland | 32 | 3 | 2 | 3 |

The first three columns (626 of 795, 79%) are the expected outcome stated in the
matcher's own docstring: German, Austrian and Swiss small-scale fruit/farm distillers
overwhelmingly operate as sole traders (Einzelunternehmen/Einzelfirma), which in all
three countries are only required to register once turnover crosses a threshold (Germany:
Kaufmannseigenschaft under HGB; Switzerland: CHF 100,000 revenue for the Handelsregister
since the 2023 reform; Austria: similar Unternehmensgesetzbuch thresholds for e.U.). No
free German, Austrian or Swiss register was found that lists unregistered sole traders —
correctly, since such a list would not exist by definition.

The 41 pins with an explicit legal-form marker but no match are the interesting residual
and were spot-checked rather than assumed: the German OffeneRegister snapshot stops in
January 2019, so a GmbH/UG formed after that date is invisible to it by construction; for
Austria, several of these correspond to JustizOnline searches that hit the 429 rate limit
before returning an answer (see request log) rather than a confirmed "not in the
Firmenbuch" result — those are open leads, not resolved non-matches, and a future pass
with fresh request budget should re-run `--fetch-justizonline` against just this subset.

## Gaps

- **Germany**: OffeneRegister is a 2017-2019 snapshot. Anything incorporated, renamed, or
  struck off since is invisible; every match's `note` already carries the retrieval date
  and "not current" caveat. No current free bulk alternative exists (Handelsregister
  itself blocks bulk/systematic use; Unternehmensregister's terms block redistribution).
- **Austria**: JustizOnline has no documented rate limit and started answering 429 after
  ~100 requests in the previous pass; roughly 237 name searches were never answered. No
  bulk Firmenbuch file exists at all — the FN→ÖNACE list is a classification filter, not
  a name/address source.
- **Switzerland**: the LINDAS Zefix core-data graph carries current legal entities well,
  but the BAZG Lohnbrenner PDF is the only public list of small/contract producers, and it
  is a licence list of contract distillers, not the underlying concession-holder register
  BAZG's own page references as a "Spirituosenregister" — that register was not located.
- **Licence calls for John**: the OffeneRegister CC-BY 4.0 bulk file carries a specific
  legal restriction (§8.2 HGB: must not be marketed as "Handelsregister" data) that is
  narrower than a normal CC-BY attribution requirement — worth a one-line disclaimer
  wherever DE crosswalk rows are shown publicly. The BAZG Lohnbrenner PDF's own licence
  terms were not stated on the fetched pages and should be treated as unconfirmed until
  checked directly with BAZG.
