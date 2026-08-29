# Irish coverage gap audit - research brief

**Date issued:** 27 August 2026
**Owner:** John Robinson
**Triggered by:** A cross-reference of the dataset against a LinkedIn Recruiter talent pool
of Irish distillery employers, run for unrelated work. Eight known distilleries turned out
to be absent. The eight were found by spot-probing names, not by any systematic method, so
the true gap is unknown.

---

## Standing conventions - do not relitigate these

1. **`region` is a map viewport, not geography.** Records outside the geographic area may
   correctly sit in a region. `The Machrihanish Distillery` is in Campbeltown, Scotland and
   correctly carries `region: ireland` because Kintyre sits about 20 km from the Antrim
   coast and falls inside that viewport. This is the same principle as the 143 Canadian
   records in region `usa`. **Do not report region assignment as a defect.**
2. **Count by `country`.** Baseline is 6,131 published locations across 141 countries.
3. **`entity_role` marks what a pin is not.** Absence means spirits are distilled there.
   See `entity-roles.md`. Only add a new value if none fits, and document it in the same
   commit.

---

## Current Irish position

| Measure | Count |
|---|---|
| `country == "Ireland"` | 57 |
| Northern Ireland, identified by `BT` postcode in `address` | 11 |
| NI records with a **blank address**, so unclassifiable by postcode | 4 |
| **Island of Ireland total** | **72** |

The four blanks are Echlinville, Hinch, Copeland and Limavady. Several Republic entries
also carry empty `address` values, including Boann, Clonakilty, West Cork, Tipperary,
Glendalough, Hawk's Rock, Wayward and Rademon.

---

## Objective

Establish the true size of the Irish coverage gap and produce a reviewed queue of
additions. **Do not write to `distilleries.geojson` in this pass.** Output is a candidate
list for John to approve.

---

## Confirmed absent, verified by name search

Add these to the queue without further discovery work, but still source an address and
coordinates for each:

- **Teeling** (Newmarket, Dublin 8) - the priority. First new Dublin distillery in
  125 years and a major visitor site.
- **Dublin Liberties**
- **Lambay**
- **Listoke**
- **Micil** (Galway)
- **Killarney**
- **Nephin**
- **Ballyvolane**

---

## Method

**1. Build a reference list from at least three independent sources.** Named starting
points, all public:

- Irish Whiskey Association member list (Drinks Ireland / Ibec)
- Drinks Ireland member list
- Ireland Whiskey Trail and Irish whiskey tourism listings
- Revenue Commissioners published excise licence data, Republic
- HMRC approved distillers and warehouse keepers, Northern Ireland
- Wikipedia list of distilleries in Ireland, as a cross-check only, never as sole source

Gin, vodka and poitín producers count. The map is not whiskey-only.

**2. Normalise before diffing.** Name matching is the hard part and it produced false
positives on the first attempt. Strip `distillery`, `distillers`, `whiskey`, `the`, `ltd`,
`company`, `&`, punctuation and case before comparing, then eyeball every near-match.
Known traps already found:

- **Walsh Whiskey and Royal Oak separated in 2019.** Royal Oak is Illva Saronno-owned.
  Two entities, not one.
- **Lough Gill was renamed Hawk's Rock in April 2025.** Sazerac-owned. Both names appear
  in the wild.
- **Connacht Whiskey Company** and the dataset's `Ballina Whiskey` may be the same Mayo
  site. Confirm before adding either.
- **Jameson appears three times** plus `Irish Distillers Dungourney`. Bow St. has not
  distilled since 1971 and is a visitor centre. Candidate for an `entity_role`.

**3. Verify before queueing.** Every candidate needs a physical address and evidence of a
still on site. Brands that source spirit and do not distil are not additions under the
current convention. `Two Stacks Irish Whiskey`, `The Muff Liquor Company` and similar
non-distilling brands are a **definitional question for John**, not an automatic add.

**4. Run the reverse check too.** Entries in the dataset that should not be there or are
wrong: closed sites, duplicates, blank addresses, missing coordinates.

---

## Output

A markdown table in `docs/data-quality/`, one row per candidate:

`name | address | lat | lon | website | distils on site (Y/N/unknown) | source URL | confidence`

Plus a short covering note stating how many reference sources were reconciled, the raw
gap count, and which candidates were rejected and why.

---

## Guardrails

- **No uncapped API scrapes.** Estimate cost before running anything metered and clear it
  with John first.
- **Save every source.** Each row carries the URL it came from. Claims that cannot be
  traced back to a source do not go in the queue.
- **Do not edit `distilleries.geojson` in this pass.**
- Work on a branch. The repo is currently on `data/prune-non-distilleries`.
