# Crosswalk grading rules, one table for every register

Set 20 September 2026 after the world pass showed each matcher inventing its own grading
(three different tables, one TLS bypass, one request-cap overrun). Code:
`scripts/crosswalklib/` (`names.py`, `grading.py`, `fetch.py`, `rows.py`), 21 tests in
`test_lib.py`. Every `scripts/match_*_registers.py` imports it and may not define its own
normaliser, grade or socket. The per-country notes dated 2026-09-19 and 2026-09-20 describe
the registers and remain the source record; their result tables predate this table and the
numbers below supersede them.

## What a grade claims

- `high`: the crosswalk treats this company as the entity behind the pin.
- `medium`: probably, one signal missing. Folded into the spine, flagged.
- `low`: a lead for a human. Stays in the candidates file, never enters the spine.
- `verified`: a human opened the register page. Matchers never set it.

## Evidence, per candidate

name (exact, or token Jaccard on distinctive words) · location (`strong` = same postcode,
street or city; `weak` = same state, province, département or prefecture; `conflict` = a
known different city; `none`) · active on the register · the pin name is distinctive (more
than a trade label) · the company name carries a trade word (`signal`).

## The table

| Name | Location | Other | Grade |
|---|---|---|---|
| exact or ≥ 0.8 | strong | active | high |
| exact or ≥ 0.8 | weak | active, signal | high |
| exact or ≥ 0.8 | none | exact, distinctive, signal | high |
| exact or ≥ 0.8 | any | inactive, or none of the above | medium |
| 0.6–0.8 | strong | | medium |
| 0.6–0.8 | weak | signal | low |
| 0.4–0.6 | strong | signal | low |
| any | none | no signal | nothing |
| any | conflict | | never above medium |
| any | any | pin not distinctive | strong → ≤ medium, weak → ≤ low, none → nothing |

A number read from the distillery's own website (Italy, Spain, India, South Africa, where
the law puts the owner's tax number on the site) counts as `strong` location with signal.

## Guards, applied to every finished candidate list

1. A premises or postcode match claimed as `self` with no name overlap is a lead. The same
   match as `operator` keeps its grade (a holding company at the distillery's address).
2. Where a hand row names the operator or group of a site, machine `self` rows for that site
   are town-name collisions and become leads (Yoichi Beer for Yoichi Distillery).
3. No register number, never above `low`.
4. Two or more different companies tied at `high` for one pin in one register: all `medium`
   (five companies named Niagara in Niagara Falls).

The builder then keeps the best row per (pin, register, relation).

## Fetching

One `Fetcher` per matcher: verified TLS with no way to turn it off, every request logged
before it is sent, the cap counts every attempt including errors, one request per second,
a 429 stops that host for the run, nothing fetched without an explicit `--fetch-*` flag.
`post()` exists for registers that hand out a session before a download (NTA Japan).

## Effect on the spine, 20 Sep 2026

Pins with a high or medium register number, before the shared table and after:

| Country | Pins | Before | After | High before | High after |
|---|---|---|---|---|---|
| United States | 1,730 | 1,495 | 1,461 | 1,093 | 1,099 |
| Australia | 367 | 336 | 323 | 286 | 233 |
| United Kingdom | 521 | 443 | 443 | 376 | 376 |
| France | 481 | 326 | 310 | 271 | 237 |
| Canada | 270 | 118 | 126 | 108 | 103 |
| Italy | 251 | 130 | 125 | 94 | 72 |
| Japan | 118 | 110 | 110 | 102 | 101 |
| India | 104 | 58 | 40 | 38 | 28 |
| Germany | 696 | 68 | 89 | 56 | 50 |
| Switzerland | 90 | 40 | 50 | 37 | 33 |
| Ireland | 64 | 42 | 42 | 37 | 37 |
| Belgium | 108 | 31 | 30 | 29 | 30 |
| Spain | 66 | 20 | 17 | 14 | 12 |
| Austria | 153 | 9 | 11 | 8 | 6 |
| New Zealand | 57 | 4 | 3 | 3 | 3 |
| South Africa | 85 | 3 | 1 | 1 | 0 |
| **Total** | | **3,238** | **3,186** | **2,556** | **2,424** |

The 132 joins that left `high` were the ones the review had already questioned: ceased
companies graded high, sole-trader ABNs, single-word names matched inside a state with no
trade word, ties. Germany and Switzerland gained because the shared stop lists are wider.
