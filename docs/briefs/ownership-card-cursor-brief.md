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
  "Eight groups run *m*. Diageo runs 28."
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
