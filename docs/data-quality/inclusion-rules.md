# What goes on the map

The bar has been restated in its own words in three separate audit docs. This is
now the one place it lives. If another doc disagrees with this file, this file wins.

## The rule

**A pin needs a physical address and something real at it.**

There are exactly two ways to qualify:

1. **Spirits are distilled there.** The default. Carries no `entity_role`.
2. **It is a real place belonging to a producer or brand, where nothing is
   distilled.** Carries an `entity_role` saying what it actually is.

Spirit category is never grounds for exclusion. Gin, vodka, poitín, grappa,
schnapps and liqueur producers all count. The map is not whiskey-only.

## Sites in planning or under construction — off

*Decided by John, 27 August 2026.*

Planning permission is not a distillery. A site that does not exist yet does not
go on the map, however credible the plan, however good the press release.

This is not a close call and it should not be re-argued each audit. Irish Whiskey
Magazine's directory carries `in-planning` and `under-construction` as first-class
listing categories, and four of the eight candidates in the 27 August Irish sweep
came from them. Every future reconciliation against a trade directory will surface
the same class again. They are rejected on sight.

**Recheck rather than re-argue.** A planning-stage site becomes eligible the day
it distils, not the day it announces. The audit docs name the ones already
rejected, so the next pass checks their status rather than re-deciding the rule:
Curraghmore (Waterford), Harvest Lodge (Dublin), Stewarts Mill (Roscommon),
Gortinore (Waterford).

## Non-distilling brands — on, if the brand has a home

*Decided by John, 27 August 2026.*

A brand that sources its spirit and distils nothing still goes on the map,
**provided it has a real, verifiable physical address**. A brand with no address
is not a place, and a map of places has nothing to pin.

That address is marked with the `entity_role` that fits what the place actually
is — usually `head_office`, sometimes `brand_shop` or `tasting_room`. A new
`brand_home` value is deliberately **not** being added: the existing three cover
every case seen so far, and `entity-roles.md` says to add a value only when none
fits. If a brand home turns up that is genuinely none of the three, add it then.

Worked examples from the 27 August sweep:

- **Gortinore Distillers (Natterjack)** — the Mahon Bridge distillery is still
  being built, so it fails rule 1. Its own site gives 17 Dame Court, Dublin 2,
  which is a real address. Eligible as `head_office`. Note the distinction: the
  *brand* qualifies at Dame Court; the *distillery* does not qualify at Mahon
  Bridge until there is a still in it.
- **Two Stacks Irish Whiskey** — already on the map, Newry address, does not
  distil. Stays, and should carry a role rather than asserting distilling by the
  absence of one.
- **The Muff Liquor Company** — not currently on the map. Eligible on the same
  terms as Two Stacks, once an address is sourced.
- **Irish Whitetail** — still fails. Not because it is a brand, but because
  `irishwhitetail.ie` does not resolve and no address can be traced to any source.

The point of the rule is that a producer's real front door is useful to a visitor
and useful to anyone prospecting, and marking it honestly costs nothing. What is
not acceptable is an unmarked pin implying a still that isn't there.

## Evidence bar, unchanged

From `removed-non-distilleries-2026-08-16.md`, and it applies to additions as
much as to removals:

> Removing a real producer from a public map is worse than leaving a bad row.

Every row carries the URL it came from. A claim that cannot be traced to a source
does not go in, and does not come out.

## Related

- `entity-roles.md` — the `entity_role` and `operator` vocabularies
- `removed-non-distilleries-2026-08-16.md` — the pruning pass that set the bar
- `irish-gap-audit-2026-08-27.md` — the audit these two decisions came out of
