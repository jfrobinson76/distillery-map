# Distillery Map — Research Brief, Iteration 2

**Date issued:** 22 August 2026
**Follows:** Your 21 August 2026 coverage audit (accepted, one correction below)
**Owner:** John Robinson

---

## Context

You audited the Distillery Map dataset on 21 August 2026 and delivered a coverage
audit, a US/TTB reconciliation, a China correction, and Eastern Europe source
research. All of it has been accepted and filed. This brief is the next
iteration: gap closure, using the queues your own audit produced.

## Standing conventions — apply to this and every future run

1. **Baseline figures.** 6,131 published locations across 141 countries. The
   strict United States count is **1,752**, taken from the `country` property.
   Always count by `country`.
2. **Correction to your audit: `region` is a map viewport, not geography.**
   The 143 Canadian records inside region "usa" are intentional — they sit in
   the US border viewport. Do not report region assignment as a defect and do
   not propose reassigning those rows. This supersedes recommendation 3 of
   your coverage audit.
3. **No bulk imports.** Never propose importing any registry, permit list, or
   POI feed directly into the public dataset. Every output is a reviewed
   candidate queue, one row per candidate.
4. **Provenance on every row.** Each candidate row must carry: source name,
   source URL, retrieval date, and the exact registry or licence reference.
   A claim without a checkable source is a lead, not a finding — label it as
   such.
5. **Physical production site is the bar.** Head offices, brand offices,
   distributors, operating centres, and shops do not qualify. Where only a
   registered (legal-entity) address is known, say so explicitly rather than
   presenting it as a production address.

---

## Task 1 — US enrichment pilot: California

From the 4,325-permit unmatched queue in your
`ttb_permits_not_matched_to_map.csv`, take the **501 California permits**.

- Deduplicate by premise address, owner name, DBA, and address.
- Classify every deduplicated candidate into exactly one of:
  `production_site` / `bottling_only` / `brand_or_office` /
  `duplicate_permit` / `closed_or_unverifiable` / `needs_review`.
- For anything classified `production_site`, verify against the operator's
  own website (or an equivalent independent source) that it is a current,
  physical distilling site.

**Deliverable:** one CSV — name, DBA, full premise address, classification,
evidence URL, retrieval date, TTB permit number.
**Also report:** the false-positive rate (how many raw permits collapsed into
how many real sites). That number decides whether we run Michigan, New York,
Texas, Pennsylvania, and Washington next.

## Task 2 — US verification queue

Adjudicate two lists from your reconciliation run:

- The **122 review-bucket matches** in `map_review.csv` (fuzzy score 70–84).
- The **54 strong name-only candidates** (score ≥95) from
  `map_unparsed_state_global_name_candidates.csv`.

For each row: confirm or reject the map-to-TTB match against the physical
address, and note current operating status. A name match in the wrong city is
a **rejection**, not a match — the bismarck-brewing case is the standing
example of why.

**Deliverable:** one CSV — map slug, TTB permit number, verdict
(confirm/reject/still-unclear), evidence URL, retrieval date, one-line reason.

## Task 3 — China pilot: one province

Per your own baijiu correction: **no Baidu Maps collection.** The target is
baijiu production sites, licence-led.

- Pick **one** major baijiu province: Sichuan or Guizhou. State which and why.
- Sources: provincial food-production licence records via the SAMR gateway,
  industry code GB/T 4754-2017 / 1512 (白酒制造), producer websites and
  plant-tour pages, OSM `craft=distillery`, and China Alcoholic Drinks
  Association or regional association membership as discovery leads.
- Dedupe against the existing 10 China records in the published dataset.

**Deliverable:** a candidate ledger CSV — name_native, transliteration,
province/city, licence number, licence issuer, registered address, production
address evidence, source URL, retrieval date, verification_level
(confirmed_production_site / entity_only / lead).
**Also report:** how many licence records were unusable and why. That tells us
whether this approach scales province by province.

## Task 4 — Eastern Europe: Hungary first

Your source research rated Hungary's **NAV excise-licensee dataset** as a
public bulk CSV/Excel download — the cheapest win in the region. Start there.

- Pull the NAV dataset and filter to spirit production: pálinkafőzde,
  szeszfőzde, and the tax-warehouse types covering spirits. Exclude tobacco
  and energy licensees.
- Dedupe against the existing 46 Hungary records in the published dataset.
- If time remains after Hungary, repeat the pattern for **Poland** (KOWR
  spirit-production register) and then **Czech Republic** (ARES, CZ-NACE
  11.01, cross-checked against Ministry of Agriculture distilling permits).

**Deliverable:** one CSV per country — name, address, licence or registry
reference, licence type, source URL, retrieval date, plus a dedupe column
flagging matches to existing map records.

---

## Not in scope this run

- Infographic or social-card design work.
- Lithuania, Latvia, Estonia, or Balkan countries beyond the desk research
  already delivered.
- Any whiskey-only taxonomy or classification work.
- Any change to the published dataset itself — candidates only.

## Delivery order

If you cannot complete everything, deliver in this order: Task 1, Task 4
(Hungary only), Task 2, Task 3. A finished task beats four partial ones.
