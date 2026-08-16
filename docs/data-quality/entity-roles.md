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
flat and means adding the field churned 30 features rather than all of them.

The property is declared in `src/lib/data.ts` (`DistilleryProps`).

### Values

| Value | Means | Example |
|---|---|---|
| `tasting_room` | Off-site tasting room, bar or cafe pouring a producer's spirits. No still on the premises. | `village-garage-distillery-tasting-room-at-orvis` — a counter inside an Orvis store, 30 km from the distillery |
| `brand_shop` | Off-site retail shop selling a producer's own spirits. No still. | `boutique-distillerie-louis-couderc` — town-centre boutique in Aurillac |
| `head_office` | Corporate or administrative office of a producer. No still. | `zuisen-distillery-co-ltd-head-office` — Zuisen's Naha office |
| `bottling_plant` | Bottling, blending or packaging site. No still. | `rockland-distillery-bottling-plant` — Seethawakapura |

Add a value only when an existing one genuinely does not fit, and document it
here in the same commit.

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

The 30 marked rows are the ones the August 2026 pruning sweep surfaced by name.
The sweep only interrogated rows whose *name* carried a marker word, so a tasting
room with a clean-looking name is still unmarked. Three US rows named "tasting
room" were left unmarked because the address is the production site and the
tasting room is on it:

- `j-henry-sons-bourbon-tasting-room-farm` (Dane, WI)
- `milam-and-greene-whiskey-distillery-and-tasting-room` (Blanco, TX)
- `pathfinder-farm-distillery-tasting-room-and-cocktail-bar` (Boonsboro, MD)

The Pathfinder row is a Main Street address and may yet be off-site. It was left
alone rather than guessed at.
