@AGENTS.md

# Distillery Map by Stillbound — distillerymap.org

## Canon: this is a Stillbound ecosystem product

Decided 2 Aug 2026. Distillery Map is not a standalone test build — it is a
product in the Stillbound ecosystem, named the same way as Distill by Stillbound.
Stillbound is the AI-for-whiskey platform; the map is its public, free layer.

**Light touch, deliberately.** "by Stillbound" is a byline, not a rename:
page titles, site name, header wordmark, footer. The domain does NOT move —
distillerymap.org is the SEO asset and stays put.

**Timing rule.** Search Console flagged 68 of 71 country pages as effectively
unindexed on 28 Jul 2026. Any deeper rebrand (OG imagery, domain, visual system)
waits until indexation recovers. Ship country copy first, rebrand from strength.

**Who the dataset actually reaches.** Of the full dataset, roughly 2,600 sit in
Stillbound's stated jurisdiction sequence (IE→NI→UK→US→CA), about 2,500 of those
with a website on file. The rest are German fruit distillers, French cognac
houses, Italian grappa makers. Whiskey is the niche where Stillbound wins, but
the underlying system is category-agnostic — a gin producer has the same
inventory, maturation and compliance problems. Do not oversell this as "6,000
customers"; the defensible number is the jurisdiction-sequence figure.

Every claimed listing is a warm inbound from a distillery that came to us. That
is the bridge from map to Stillbound, independent of branding.

---

> A free, open distillery map — a community-built dataset of distilleries, tasting rooms, and spirit producers worldwide.

**Never hardcode the total.** The count is derived from the geojson at build time and rendered live (`src/app/page.tsx`). It changes every time entries are added or removed.

## Project Overview

- **URL**: distillerymap.org (primary), distillerymap.ie (redirects to .org)
- **Stack**: Next.js 16, React 19, TypeScript, Tailwind CSS 4, Mapbox GL
- **Hosting**: Vercel (Hobby plan — never add Co-Authored-By to commits)
- **Forms**: Formspree (ID: mjgpywkp — shared for submissions + claims)
- **No database** — all client-side, data from static geojson

## Commands

```bash
npm run dev          # Dev server
npm run build        # Production build
npm run lint         # ESLint
```

No test suite. Validate with `npm run build`.

## Site Structure

```
src/app/
├── page.tsx              # Main map — search, regions, submit, claim flow
├── embed/
│   ├── layout.tsx        # noindex, strips parent layout
│   └── page.tsx          # Embeddable map (?region=, ?country=)
├── layout.tsx            # Root layout — fonts, metadata, body only
└── globals.css           # WOW palette as Tailwind theme

src/lib/
└── constants.ts          # WOW palette, regions, Formspree ID

public/data/
└── distilleries.geojson  # source of truth for the count (OSM, Wikidata, Google Places, curated)
```

## Form Types (all via Formspree mjgpywkp)

Forms are distinguished by the `form_type` hidden field:
- `add` — new distillery submission
- `closure` — report a closure
- `correction` — suggest a fix
- `claim` — distillery owner claiming their listing

Claim submissions include: contact_name, contact_email, contact_role, plus optional listing updates (website, description, visitor_info, booking_link).

## Environment Variables

- `NEXT_PUBLIC_MAPBOX_TOKEN` — required for map rendering

## Design

Uses the WOW (World of Whiskey) palette — amber/oak/parchment. Self-contained, no dependency on SAMAC branding. Fonts: Geist (sans) + Fraunces (display).

## Monetisation (subtle, not overt)

Claimed listing model: free base layer → claim & correct → enhanced listing (paid, future).
First 50 claims get the enhanced listing free (logo + URL); after that, €25/year (decided 24 Jul 2026, not yet public).
Every claim submission is a warm lead. The form captures structured data that becomes the premium listing schema.
No pricing page. No "For Business." The CRM conversation happens in email after they claim.

### Claim workflow (rule, applies to every validated claim)

When a claim is validated (real person from the distillery confirms via the form/email):
1. Apply their listing updates to the geojson.
2. Set `"claimed": true` on the feature — this swaps the popup's "Claim it" link
   for a "✓ Verified by the distillery" badge and adds a ✓ Verified tick on country pages.
3. Contact details (name, email, role) stay in John's Gmail ONLY — NEVER in the
   geojson (it is publicly served) and never committed anywhere in this repo.
   GDPR basis: they submitted the claim to manage their listing; use contacts for
   that purpose only — no marketing without separate consent, honour deletion requests.

Claimed so far: Lough Ree Distillery (Michael Clancy, CTO — 24 Jul 2026).

## Country Page Editorial (voice + review gate)

Country page intro copy is not templated boilerplate — Search Console flagged 68 of
71 pages as effectively unindexed (28 Jul 2026) because the identical intro sentence
across every country reads as thin/duplicate content to Google.

- `docs/editorial-voice.md` — the voice bible. Read before writing or revising any
  country intro. Defines who's "talking" (a drinks trade veteran, not a travel
  blogger or AI), banned phrases, AI-tell patterns to avoid, and the 3-point content
  checklist (scale in context / what's actually distinct / what the list below offers).
- `/review-country-copy` — 5-persona review (Marguerite/accuracy, Fintan/voice+
  uniqueness, Priya/reader, Callum/commercial neutrality, Yuki/SEO). **Gate: no
  country-page copy is committed without passing this review** — applies to copy
  written in-session or by a delegated subagent. A subagent must run the review
  itself and report the table alongside the copy.
- Ireland, Scotland, USA, Japan were the first batch (drafted 28 Jul 2026) — check
  those files/commits for the calibrated example of what "PASS" looks like before
  writing the next batch.

## Research

`/whiskey-aging-inventory` — the global aging-inventory map and estimate (~58m casks).
Figures live in `src/lib/aging-inventory.ts` (source of truth). The reasoning, arithmetic,
sources and dated correction log live in `docs/research/whiskey-aging-inventory-evidence.md`.

**Rule: change a number in the module, add the reasoning to the evidence doc in the same
session.** Two figures in the first pass were wrong in ways invisible from the conclusion
alone (Kentucky quoted as the US national total; an out-of-date claim about Indian whisky
being molasses-based). A derivation that exists only in a chat transcript cannot be defended
when a distiller pushes back.

Share image: `npm run share-card` with a dev server up, writes `public/share/`.

## Planned

- **Angel's Share infographic** — visual explainer of barrel evaporation during maturation (~2% per year). Standalone content piece, not a full education section. Reference data exists in GWC project (`docs/whiskey-glossary-research.md`).

## Contact

- hello@distillerymap.ie (forwards to John's inbox)
- hello@distillerymap.org (forwards to John's inbox)

## Parent Project

This is a SAMAC Consulting project. See `~/.claude/CLAUDE.md` for how all projects connect.
