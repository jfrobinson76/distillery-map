@AGENTS.md

# Distillery Map — distillerymap.ie

> A free, open distillery map — 6,497 distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.

## Project Overview

- **URL**: distillerymap.ie (also owns distillerymap.org, redirects to .ie)
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
└── distilleries.geojson  # 6,497 entries (OSM, Wikidata, Google Places, curated)
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
Every claim submission is a warm lead. The form captures structured data that becomes the premium listing schema.
No pricing page. No "For Business." The CRM conversation happens in email after they claim.

## Contact

- hello@distillerymap.ie (forwards to John's inbox)

## Parent Project

This is a SAMAC Consulting project. See `~/.claude/CLAUDE.md` for how all projects connect.
