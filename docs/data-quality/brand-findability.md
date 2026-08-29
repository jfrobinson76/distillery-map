# Brand-level findability

**Question:** someone searches the map for "Jawbox", "Shortcross", "Drumshanbo"
or "Bertha's Revenge" and gets nothing, because those are brands and the map
stores sites. How should the map handle that?

**Recommendation: add an optional `brands` list to the site feature.** One pin,
many search keys. Do not create brand pins.

---

## The size of it

The 27 August Irish sweep pulled roughly 34 gin brands off one directory page.
Almost none needed a new pin — Shortcross is Rademon Estate, An Dúlamán is
Ardara, Drumshanbo Gunpowder is The Shed, Method & Madness is Midleton, Xin is
Ahascragh, Minke is Clonakilty. Every one of those sites is already on the map,
and every one of those brand names returns nothing in the search box.

That is one country, one spirit category, one afternoon. The whiskey side is the
same shape — Fercullen, Dubliner, Silkie, Redbreast, Natterjack, Lír.

## The shape

```ts
/** Brands made at this site whose names differ from the site's own.
 *  Absent on most features. See docs/data-quality/brand-findability.md */
brands?: string[];
```

```json
{ "name": "Rademon Estate Distillery", "brands": ["Shortcross"] }
{ "name": "The Shed Distillery", "brands": ["Drumshanbo Gunpowder", "Drumshanbo"] }
```

Optional, like `entity_role` and `operator`. Present only where a brand name
differs from the pin name, so `Dingle Gin` at `Dingle Distillery` gets nothing
and the payload barely moves.

Search becomes one line wider (`src/components/DistilleryMapApp.tsx:566`):

```ts
const p = f.properties as DistilleryProps;
const hay = [p.name, ...(p.brands ?? [])].join(" ").toLowerCase();
return hay.includes(lower);
```

**The result row must say why it matched.** "Shortcross — made at Rademon Estate
Distillery", not a bare pin. A search that silently redirects you to a name you
didn't type reads as broken.

## Why not brand pins

Two pins on one door. Worse, the headline count is derived from the geojson at
build time and rendered live — `CLAUDE.md` is explicit that it is never
hardcoded. Brand pins would inflate the one number the product leads with, and it
would be inflated with duplicates. That is a credibility problem, not a display
problem.

## Why not a separate brand → site lookup file

More machinery for the same answer, and a second file to keep in step with the
first. The relationship belongs on the feature that owns it, the way `operator`
does.

---

## The actual payoff is SEO, not the search box

This is the part worth arguing.

Search Console flagged 68 of 71 country pages as effectively unindexed on
28 July 2026, for thin and duplicate content. The fix so far has been hand-written
country intros. Brand names are the other half of that fix, and they are already
sitting in the data waiting to be written down.

"Distilleries in Ireland" is a page Google has many of. "Where is Drumshanbo
Gunpowder made" is a question with exactly one right answer, and the map holds
it. A country page that renders **The Shed Distillery — home of Drumshanbo
Gunpowder** carries unique, high-intent, long-tail text that no template can
generate and no competitor's list has. Thirty-four of those on the Ireland page
alone.

So the sequence is: the field feeds the country pages, the country pages earn the
indexation, and the search box improves as a side effect.

## And it fills itself

The claim form already captures structured data from owners — website,
description, visitor info, booking link. Add a brands field to it and the dataset
fills from claims rather than from research. A brand owner whose brand is
currently unfindable has a concrete reason to claim their listing, which is
exactly the warm-inbound mechanic the claim model is built on.

Research seeds it. Claims maintain it.

---

## Suggested scope

Ireland first, then it is a config swap rather than a rebuild.

1. Add `brands` to `DistilleryProps` and widen the search filter. Small.
2. Render "home of X, Y" on country pages and in the map popup.
3. Populate the island of Ireland only, from sourced mappings.
4. Add brands to the claim form.
5. Review whether the Ireland page's indexation moves before doing country two.

Step 3 is the only one with real cost. Seven mappings are already sourced from
the 27 August sweep (Shortcross, An Dúlamán, Drumshanbo Gunpowder, Method &
Madness, Xin, Minke, Symphonia). The rest need a verification pass, at the same
evidence bar as every other row: the URL that proves it, or it does not go in.

## Ireland pilot shipped

*Implemented 29 August 2026.* The first release adds seven sourced brand names
to six island-of-Ireland sites:

| Site | Brands |
|---|---|
| Rademon Estate Distillery | Shortcross |
| Ardara Distillery | An Dúlamán |
| The Shed Distillery | Drumshanbo Gunpowder |
| Jameson Distillery Midleton | Method & Madness |
| Ahascragh Distillery | Xin, Symphonia |
| Clonakilty Distillery | Minke |

The field now feeds map search, explains brand matches in the result row,
renders “Home of …” in map popups and country-page HTML, and is collected by
the claim form. Research remains the seed; verified owner claims can maintain
the mappings from here.

This is deliberately an Ireland-only measurement release. Check the Ireland
country page's indexation and brand-query impressions before expanding the
research pass to country two.
