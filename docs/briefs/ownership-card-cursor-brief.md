# Brief: "Who Runs the UK's Stills" — the ownership web

For a Cursor agent. Repo `distillery-map`. Read this whole file before touching anything.

## Setup, and the one rule that avoids a collision

Another agent (Devin) is working on branch `data/company-crosswalk`, editing
`data/company-crosswalk/*.csv`. **You read those files; you never write to them.**

1. `git fetch origin && git checkout -b viz/ownership-card origin/data/company-crosswalk`
2. Everything you create lives in `data/ownership/`, `docs/social/ownership/` and
   `scripts/build-ownership-card.mjs`. Nothing else changes.
3. Commit small. Open a PR against `data/company-crosswalk` (not main). John merges.

## What we are making

One square social image, 2400×2400 (retina 2×, LinkedIn downsamples), in the same
Stillbound creative as the August aging-inventory card and the September Kentucky county
card: a **network diagram** of who operates the UK's distilleries. Not a map. Eight group
hubs, each with spokes out to the distilleries it runs; every independent distillery as its
own small node in the surrounding field, unconnected, because that is the point. The claim it
carries:

> Of the UK distilleries tied to a company at high confidence, most have a company of their
> own. Eight groups run the rest. Diageo alone runs 28.

Recompute those numbers from the data at build time; they change as the crosswalk fills. Never
hard-code a figure in the HTML.

## Inputs

- `public/data/distilleries.geojson` — 6,139 distilleries; UK ones have `country ==
  "United Kingdom"`, coordinates in `geometry`.
- `data/company-crosswalk/company-crosswalk.csv` — slug → company. Columns: `slug,
  distillery_name, country, registry, company_number, company_name, relation, match_method,
  confidence, verified, source, note`. Use rows with `confidence` in `high` or `verified`
  only. Ignore `medium` and `low`.
- `data/boundaries/ne_10m_admin_0_countries.geojson` — country outlines.
- `docs/social/aging-inventory-map-card.html` and `scripts/build-map-card.mjs` — the
  existing card and its build/export. **Match its type, palette, masthead and export path
  exactly.** Palette from that file: parchment `#F7EEDA`, ink `#2A1F17`, deep brown `#6E2F14`,
  coppers `#9C4E20` `#A05A22`, amber `#C8852E`, gold `#D39A3D`, muted `#7F7262`. Fonts:
  Newsreader (display), Instrument Sans (UI), JetBrains Mono (figures).
- `docs/editorial-voice.md` — voice rules for any words on the card.

## Step 1: the group table (`data/ownership/groups.json`)

The crosswalk names companies, not groups. Diageo appears as `Diageo`, `DIAGEO SCOTLAND
LIMITED` and `Diageo plc`. Write a small, hand-checked mapping from `company_name` (and
`company_number`) to a display group, e.g.

```
Diageo                 <- Diageo, DIAGEO SCOTLAND LIMITED, Diageo plc, 00023307, SC000750
Pernod Ricard          <- CHIVAS BROTHERS LIMITED
Bacardi                <- JOHN DEWAR AND SONS LIMITED
Suntory Global Spirits <- BEAM SUNTORY UK LIMITED
Whyte & Mackay         <- WHYTE AND MACKAY GROUP LIMITED
William Grant          <- WILLIAM GRANT & SONS LIMITED, William Grant & Sons
Edrington              <- THE EDRINGTON GROUP LIMITED
Ian Macleod            <- IAN MACLEOD DISTILLERS LIMITED
Inver House            <- INVER HOUSE DISTILLERS LIMITED
LVMH                   <- MACDONALD & MUIR LIMITED
Nikka                  <- Nikka Whisky Distilling
Brown-Forman           <- THE BENRIACH DISTILLERY COMPANY LIMITED
```

Every company not in the table is `Independent`. A company that appears for exactly one
distillery is by definition independent. Put a `note` on each mapping saying why (e.g.
"operating subsidiary of Diageo plc"). Do not guess ownership you cannot state; leave it
`Independent` and list it in the PR for a human.

## Step 2: the card (`docs/social/ownership/ownership-card.html`)

Render the web with D3 force layout (or a deterministic radial layout if force is unstable
across builds; the PNG must be reproducible). Square frame, parchment ground.

- **Masthead** top-left, report-edition style as the August card: **"Who Runs the UK's
  Stills · September 2026"**, Stillbound mark as the August card carries it. "UK", never
  "Britain": Northern Ireland's distilleries are in the data.
- **Hubs**: the top eight operating groups by site count, drawn as larger nodes labelled in
  Newsreader with the group name and, in JetBrains Mono, the count. One colour per hub from
  the palette's coppers, amber, gold and deep brown, plus at most three restrained tones you
  add to stay inside the creative; no primary blue or green. Hub size scales with site count
  (Diageo, 28, is visibly the largest).
- **Spokes**: a thin line (`#6E2F14`, 35% alpha) from each hub to each of its distilleries,
  drawn as a small filled node in the hub's colour, labelled only where there is room (Islay
  and Speyside names are recognisable and worth showing; do not label all 28 Diageo sites if
  they collide).
- **Independents**: every high-confidence distillery whose company runs only that site, as a
  small muted node (`#7F7262`, 60% alpha), unlabelled, no spokes, scattered as a field around
  and between the hubs so the eye reads "many small, few large".
- **The number**, bottom-right, large, Newsreader: the share of high-confidence UK
  distilleries that are independent, e.g. **"79% independent"**, with two lines under it:
  "*n* distilleries tied to a registered company at high confidence." and
  "*g* groups run *m*. Diageo runs *d*." (all computed; do not write 8 or 28)
- **Legend**: none needed if hubs are labelled. If a hub label will not fit, a compact legend
  bottom-left in JetBrains Mono, sorted by count.
- **Footer**, small, Instrument Sans: "Source: Companies House and Wikidata, matched to the
  Stillbound Distillery Map. Method and full table: stillbound.ai/research/ownership" (page
  does not exist yet; keep the slug a variable at the top of the build).
- No hashtags, no logo wall, no gradient, no glow. One idea, very little text. John rejected
  an earlier card for being "visually exhausting" at feed size (review notes in
  `docs/linkedin-aging-inventory-post.md`); the Kentucky county card is the recent example of
  the density that worked.
- **Optional variant B**, only after A ships: the same data as a map of the UK with the same
  colours, for a carousel second slide. Do not start B before A is reviewed.

## Step 3: the build (`scripts/build-ownership-card.mjs`)

- Reads the three inputs, computes the numbers, renders the HTML with them injected, exports
  `docs/social/ownership/ownership-card-2400.png` the same way `build-map-card.mjs` exports.
- Also writes `docs/social/ownership/ownership-summary.md`: the computed numbers, the
  group table with counts, and the list of companies left as Independent with more than one
  site (those are the ones a human should look at). This file is the audit trail for the
  claim on the card.
- Add an npm script `ownership-card` alongside `share-card` in `package.json`.

## Checks before the PR

- Rebuild after `git pull` on the crosswalk branch; numbers must move with the data.
- View the PNG at 393 px wide (a phone). If the legend or footer is unreadable, drop
  elements; do not shrink type.
- Every figure on the card appears in `ownership-summary.md`.
- No file under `data/company-crosswalk/` changed:
  `git diff --stat origin/data/company-crosswalk -- data/company-crosswalk` must be empty.

## Done looks like

A PR with the web PNG, the HTML, the build script, `groups.json`, the summary, and a PR
description that quotes the three numbers and lists the multi-site companies you left as
Independent.

---

## Variant B is now the primary (John, 18 Sep 2026, after seeing A)

A is approved and kept as the second carousel slide. **B is the lead image**: the same claim,
drawn on a map of the UK with every distillery at its real coordinates.

### Delivery route

`cursor[bot]` has read-only access to this repo. Do exactly what worked for A: build on a
local branch `viz/ownership-map` off `origin/viz/ownership-card` (PR #33 carries A), then park
the commit as an apply-ready patch plus the PNG on `jfrobinson76/stillbound-knowledge` in
`_meta/Product Sync/Ownership Map/` and open a PR there. Claude applies it to this repo.
Do not edit A's files; add alongside them.

### The picture

- **Base**: UK outline from `data/boundaries/ne_10m_admin_0_countries.geojson` (GBR; include
  Northern Ireland, exclude the Republic or render it at 30% so the border reads). Deep brown
  line on parchment, no fill or a 4% brown fill. Project so **Scotland is large**: a conic or
  transverse Mercator centred around 4°W, 56.5°N, with England running off the bottom edge
  is acceptable; Shetland may be dropped or inset. Islay, Skye, Orkney and Speyside must be
  distinguishable at feed size.
- **Every high-confidence UK distillery at its real coordinates** from the geojson.
  Independents (the 79%) as the same small muted dots as A (`#7F7262`, 60% alpha). They stay
  dots. No lines.
- **Group sites** as filled dots in the group's colour from A (keep A's palette assignment
  per group so the two slides agree).
- **Groups come from control, not from a hand table.** `data/ownership/psc-parents.csv`
  (now on `data/company-crosswalk`) gives each company's ultimate controller from Companies
  House persons-with-significant-control filings. Group sites by `ultimate_number` (or
  `ultimate_name` where the chain stops at a foreign parent such as Pernod Ricard SA). A
  distillery is **independent when its controller runs exactly one site.** Keep
  `groups.json` only for display names (Kintail Trustees → Edrington; Emperador Holdings →
  Whyte & Mackay; International Beverage → Inver House; LLG Topco → Loch Lomond Group;
  Speymalt → Gordon & MacPhail; Glen Turner Co → La Martiniquaise) and colours. At 18 Sep
  this gives 71% independent (223/312), 15 controllers with more than one site, Diageo 30.
  Recompute at build; the figures change after the crosswalk review.
- **Hubs sit at the geographic centre of each group's distilleries.** No offices, no
  addresses; a pundit reads geography, not registrations. Compute the centroid of the
  group's site coordinates, nudge it if it lands in the sea, and draw A's larger node there
  with the group's display name and count. Show the **top eight groups by site count** as
  hubs with lines; the remaining multi-site groups are drawn as their sites in a shared
  seventh/eighth tone with a short line between the sites and no hub label, so the 71% is
  visually honest without eight more labels.
- **Lines from each hub to each of its sites**, thin, the group's colour at 45% alpha, drawn
  under the dots. Diageo's 28 lines from Edinburgh will fan across the Highlands and out to
  Islay and Skye; that fan is the picture. Slight curvature (quadratic, small offset) so
  overlapping lines to Speyside separate; no arrows.
- **Label discipline**: hub labels only, plus at most six site labels where they carry the
  story (Lagavulin, Caol Ila, Talisker, Cardhu, Glenfiddich, Laphroaig). No label collisions;
  drop a label rather than shrink it.
- **Masthead, the number, footer**: identical to A. Fix A's masthead wrap (the "·" should not
  end line one). Use one name per group across both slides; "Suntory Global Spirits" in the
  summary and "Suntory" on the card is fine if the post uses the short form.
- Output `docs/social/ownership/ownership-map-2400.png` and `ownership-map.html`; extend
  `scripts/build-ownership-card.mjs` with a `--variant map` flag or add
  `build-ownership-map.mjs`; add `npm run ownership-map`. Append the hub table (group,
  registered office, coordinates, source URL) to `ownership-summary.md`.

### Export note

Headless Chrome hangs on John's Mac with the current flags. If you touch the exporter, use
`--headless=new` and `--virtual-time-budget=8000`, and keep a 60 s timeout. Commit the PNG
from your own export either way.

### Checks

Same as A, plus: A must be rebuilt on the same controller-based grouping so both slides carry
the same figures (the 79% card is superseded; do not post it); view at 393 px, Islay and Speyside still distinguishable.

---

## Correction, 18 Sep 2026 21:40: the card is Scotch whisky only

Read `data/ownership/README.md` on `data/company-crosswalk` first. The UK-wide number was two
industries in one denominator (England's gin belt is ~100% independent by nature). The card
that survives a hostile question is **Scotch whisky only**:

- Universe: map region `scotland` AND (description says malt/grain/whisky OR the category
  verdict in `data/categories/out_*.json` includes whisky). 178 at 18 Sep.
- Grouping: controller from `data/ownership/psc-parents.csv`; independent = controller runs
  one site.
- Expected figures (recompute): ~150 matched, 14 groups running ~90, Diageo 34, independents
  ~60 matched plus ~28 unmatched small sites. Treat unmatched Scotch sites as independent
  dots on the map (they are all small post-2005 distilleries; list them in the summary).
- **Title: "Who Runs Scotland's Stills · September 2026"** (Scotland, whisky; not UK).
- **The number**: not a single percentage. Two lines, Newsreader:
  **"Half independent."** then, smaller: "*n* Scotch whisky distilleries. Fourteen groups run
  *m*. Diageo runs *d*, one in five." And the caveat line in Instrument Sans: "By number of
  distilleries, not by litres." That caveat is not optional.
- Map: Scotland only, large; Islay, Campbeltown, Speyside, Skye, Orkney legible. No England.
- Slide two (A rebuilt): same universe and grouping, web layout.
- The 79% PNG in PR #33 is superseded; leave it in git history, replace the file.
