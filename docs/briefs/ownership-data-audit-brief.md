# Adversarial audit: "Who Runs Scotland's Stills"

You are auditing a claim before it is published under John Robinson's name on LinkedIn. You
did not build it. Assume it is wrong until you have shown otherwise. Your output is a table of
disagreements and corrected figures, not reassurance.

## The claim under audit

> Half independent. 176 Scotch whisky distilleries. Fifteen groups run 89. Diageo runs 32,
> one in five. By number of distilleries, not by litres.

Repo `distillery-map`, branch `viz/ownership-map` (contains everything). Read
`data/ownership/README.md` for the builder's definitions, then set them aside and form your own.

## Files (do not trust any of them)

- `public/data/distilleries.geojson` — the map's 6,139 entries; Scotland = `region == "scotland"`.
- `data/categories/out_*.json`, `rules.json` — spirit-category verdicts per slug (a model made
  these; treat as hints).
- `data/company-crosswalk/company-crosswalk.csv` — slug → registered company, with
  `match_method` (manual / operator-map / wikidata-name / companies-house-search) and
  `confidence`. The `operator-map` rows were typed by a Claude session from industry
  knowledge; the `companies-house-search` rows are name matches and some are shells.
- `data/ownership/psc-parents.csv` — each company's ultimate controller from Companies House
  persons-with-significant-control chains, with the chain and the source URL per row.
- `data/ownership/groups.json` — display names only.
- `docs/social/ownership/ownership-summary.md` — the builder's own arithmetic and its list of
  28 unmatched Scotch sites that were *assumed* independent.

## What to check, in order of how likely it is to be wrong

1. **The denominator (176).** The SWA says ~150 operating malt and grain distilleries. Where do
   the other ~26 come from? For every entry in the Scotch set, decide: operating whisky
   distillery / mothballed or closed / not yet producing / gin-or-other with a whisky verdict /
   a bar, shop or warehouse / duplicate of another entry. Known suspects: Brora, Port Ellen,
   Rosebank (reopened, fine), `newbridge-bond-*` (a warehouse), `the-lost-distillery-company-*`
   (a bar), `rhidorroch-*` (a café), `black-friars-distillery` (Plymouth Gin, England: if it is
   in the Scotch set the region tag is wrong), `gordon-macphail` (a bottler's office, not a
   still), `diageo-global-supply-centre` (Leven: bottling and grain?). Produce your own count.

2. **The 28 "unmatched, assumed independent."** They are all in the summary. Each needs a
   sentence: who runs it, from its own website or Companies House. Any that is group-owned
   (e.g. a Distell, Ian Macleod or Pernod site with a shell company name) moves the split.

3. **Group membership, site by site.** Take the 89 "group-run" sites and check each against
   an outside source: the distillery's own site, the Wikipedia "List of whisky distilleries in
   Scotland" (owner column, CC BY-SA, facts are free), the owner's brand list. Flag every
   disagreement. Known suspects from the build: Warner's Distillery under La Martiniquaise
   (a Northamptonshire gin house; is that PSC chain real?), Benromach and The Cairn (both
   Gordon & MacPhail; does the file agree?), Glenglassaugh (Brown-Forman), Tormore (Elixir,
   not Pernod since 2022), GlenAllachie (independent since 2017, not Pernod), Bunnahabhain /
   Deanston / Tobermory (CVH = Distell = now Heineken?), Ardnahoe (Hunter Laing), Ben Nevis
   (Nikka), Glen Grant (Campari), Kininvie / Ailsa Bay / Girvan (Grant's), Dalmunach and Glen
   Keith (Pernod), North British (a 50/50 Edrington–Diageo JV: how should it count?).

4. **The independents.** Sample at least 25 of the 87. Are any actually group-owned through a
   structure the PSC chain missed: a family holding that owns two distilleries via separate
   companies (e.g. J & A Mitchell: Springbank and Glengyle; Angus Dundee: Glencadam and
   Tomintoul; Wemyss; Loch Lomond Group's third site), a foreign parent the chain could not
   follow, or an individual PSC who also controls another site?

5. **Diageo = 32, "one in five."** List the 32 by name. Compare with Diageo's own published
   list of Scotch malt distilleries (28 malt + Cameronbridge grain + Leven + Roseisle + the
   reopened Brora and Port Ellen). Which of the 32 are not on Diageo's own list, and which of
   Diageo's are missing?

6. **The PSC method itself.** Pick five chains from `psc-parents.csv` and re-walk them by hand
   on find-and-update.company-information.service.gov.uk. Does the crawler's "highest ownership
   band wins" rule ever pick the wrong parent? Does "individual PSC = top" hide a group?

7. **Recompute.** Write your own script from the geojson + crosswalk + psc file, with your own
   definitions from step 1, and produce: total, group-run, independent, number of groups,
   Diageo's count. Do not reuse `build-ownership-card.mjs` or the summary's numbers.

## Output

`docs/research/ownership-audit-2026-09.md` in this repo on a branch `audit/ownership-2026-09`,
plus a comment on PR #35 with the summary table. Structure:

1. **Verdict** in three lines: can the card's four numbers be published as they stand; if not,
   which change and to what.
2. **Disagreements table**: slug · what the build says · what you found · source URL · effect on
   the count.
3. **Your recomputed figures** with your definitions stated.
4. **What you could not verify** in the time, listed, not glossed.

Rules: quote sources with URLs; never "correct" a row from memory alone; a Wikipedia owner
cell needs a second source before it overrides a Companies House filing; do not change any
data file in the repo, only report. If the honest answer is "roughly half" with a range, say
the range.
