# `entity_role` — what a pin actually is

Added 16 August 2026, out of the non-distillery pruning pass
(`removed-non-distilleries-2026-08-16.md`).

## The problem it solves

The map is a tourism product. A visitor standing in Manchester Center, Vermont
wants to know there is a Village Garage Distillery tasting room inside the Orvis
store on Main Street. Nothing is distilled there, but the pin is genuinely useful
and it stays.

Downstream consumers of the same dataset ask a different question: *is there a
producer at this address I could talk to?* For them the tasting room is noise.

Both are right. So the data says what the place **is**, and each consumer decides
what to do with it. No consumer-specific flags live in the public file.

## The convention

A single optional string property on a feature:

```json
"entity_role": "tasting_room"
```

**Absence is the default and means "spirits are distilled here."** The
overwhelming majority of the 6,131 features carry no `entity_role` at all. Only
sites that are *not* distilling sites are marked, which keeps the public payload
flat and means adding the field churned 20 features rather than all of them.

The property is declared in `src/lib/data.ts` (`DistilleryProps`).

### Values

| Value | Means | Example |
|---|---|---|
| `tasting_room` | Off-site tasting room, bar or cafe pouring a producer's spirits. No still on the premises. | `village-garage-distillery-tasting-room-at-orvis` — a counter inside an Orvis store, 30 km from the distillery |
| `brand_shop` | Off-site retail shop selling a producer's own spirits. No still. | `wyoming-whiskey-distillery-shop` — the Whiskey Shop on Main Street, Kirby, a few hundred yards from the distillery building |
| `head_office` | Corporate or administrative office of a producer. No still. | `rock-and-storm-distilleries-pvt-ltd-head-office` — Chandigarh office; the distilling unit is at Chhajli, Sangrur |
| `bottling_plant` | Bottling, blending or packaging site. No still. | `rockland-distillery-bottling-plant` — Seethawakapura |

Add a value only when an existing one genuinely does not fit, and document it
here in the same commit.

### Non-distilling brands use these values, not a new one

Decided 27 August 2026: a brand that distils nothing goes on the map if it has a
real physical address, marked with whichever of the values above fits — usually
`head_office`. A `brand_home` value was considered and deliberately not added,
because the existing three cover every case seen so far. See
`inclusion-rules.md`.

### Open, awaiting a decision

Two rows currently assert distilling through the absence of `entity_role`, and
both would need a new value. Raised in `irish-gap-audit-2026-08-27.md`:

- `Irish Distillers Dungourney` — a maturation warehouse complex, no still.
  Proposed: `maturation_warehouse`, plus `operator: "Irish Distillers"`.
- `Jameson Distillery Bow St.` — a visitor centre that has not distilled since
  1971. Proposed: `visitor_centre`. `tasting_room` is the nearest existing value
  and is wrong.

**A shop or office in the name is not evidence of the role.** Of the 16 rows the
August 2026 pruning pass shortlisted as "offices and brand shops", nine turned
out to be the producer's actual distilling site with a shop or tasting counter
attached, and were renamed with no `entity_role` at all. The role is set from the
producer's own website, never from the pin's name.

## Related convention: `operator`

Added 16 August 2026, out of the Sliabh Liag Distillers case.

One business can run more than one mapped site. Sliabh Liag Distillers has two:
the distillery at Ardara and the bottling and administration centre at Carrick,
20 km away. A tourism map wants both pins. A consumer joining this data to
anything else needs to know they are one business.

A single optional string property carries that, and nothing more:

```json
"operator": "Sliabh Liag Distillers"
```

**Absence is the default and means the pin's own name is the business.** It is
set only where two or more pins belong to one operator, or where the pin's name
does not say who runs it. It is a plain trading name, not a foreign key — there
is no operator table and no id to resolve. Matching is exact string equality:

```js
const sites = data.features.filter((f) => f.properties.operator === "Sliabh Liag Distillers");
```

Deliberately not a parent/child link. Ardara is not "under" Carrick and neither
is the head site; they are two sites of one company, which is what a flat
operator string says and a parent pointer would not.

### What it is deliberately not

- **Not a category or quality field.** It says nothing about what spirit is made
  or how good it is. Spirit category lives in `data/categories/`.
- **Not a "remove me" flag.** Every row carrying an `entity_role` was reviewed and
  kept on purpose. The pruning pass deleted rows that were not connected to a
  producer at all; these are.
- **Not named for any one consumer.** There is no `gtm_exclude`, no
  `stillbound_*`. The map is a general product and the data stays neutral.

## How to filter on it

Everything on the map, unchanged:

```js
data.features
```

Distilling sites only:

```js
data.features.filter((f) => !f.properties.entity_role)
```

Prospecting a producer to talk to — drop the sites where nobody works, keep the
offices, because for several producers the office pin is the *only* pin they have
and the office is where you would make contact anyway:

```js
const NO_ONE_TO_TALK_TO = new Set(["tasting_room", "brand_shop"]);
data.features.filter((f) => !NO_ONE_TO_TALK_TO.has(f.properties.entity_role));
```

That last one is the rule already applied to pure-gin producers: they stay on the
map, they come out of prospecting. Same shape, different reason.

## Known gaps

The 20 marked rows are the ones the August 2026 pruning sweep surfaced by name.
The sweep only interrogated rows whose *name* carried a marker word, so a tasting
room with a clean-looking name is still unmarked. Five US rows named "tasting
room" were left unmarked because the address is a distilling site:

- `left-coast-brewing-co-tasting-room-smokehouse-distillery-irvine` and
  `-ontario` (CA). Shortlisted as tasting rooms, then checked: both location
  pages carry a menu section headed "Craft Spirits Produced on Site" listing
  Left Coast vodka, gin, rum, malt whiskey, bourbon and blanco agave, and the
  team page lists a Head Brewer/Distiller at Irvine. OC Weekly's account of the
  Irvine opening quotes the owner on the distillery build and says the brewer
  would be "brewing and distilling on the new system". The word "distillery" in
  those two names is real, so neither is marked.

And three where the tasting room sits on the production site:

- `j-henry-sons-bourbon-tasting-room-farm` (Dane, WI)
- `milam-and-greene-whiskey-distillery-and-tasting-room` (Blanco, TX)
- `pathfinder-farm-distillery-tasting-room-and-cocktail-bar` (Boonsboro, MD)

The Pathfinder row is a Main Street address and may yet be off-site. It was left
alone rather than guessed at.
