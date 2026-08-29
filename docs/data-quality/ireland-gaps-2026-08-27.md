# Island of Ireland — gaps and crossed records, 27 August 2026

Triggered by a cross-reference from a parallel session: **Teeling was not findable
by name** in `public/data/distilleries.geojson`. Eight island-of-Ireland names were
probed by hand and eight came back missing. That probe was not a sweep, so this pass
reconciled the whole island against a published list before changing anything.

**Baseline.** 72 features on the island of Ireland — 57 with `country: "Ireland"`,
15 with `country: "United Kingdom"` inside a Northern Ireland bounding box.

**Reconciled against** the Wikipedia list of whiskey distilleries in Ireland
(47 operating, sourced from the Irish Whiskey Association's count of 50 operational
distilleries as of March 2025), then each candidate checked against its own website
or an independent source. Same bar as `removed-non-distilleries-2026-08-16.md`:
evidence per row, and the only question asked is *does anything get distilled here*.

**Result.** 6,131 features → **6,138**. Seven added, four repaired, three rejected
with reasons recorded.

---

## The finding behind the finding: Teeling was already on the map, under the wrong name

Teeling was not missing. It was mis-named, and the surrounding Dublin 8 records were
crossed with each other — the signature of a bad OSM/Wikidata merge, not of absent data.

| Record | What it held | What is true |
|---|---|---|
| `jameson` | `13-17 Newmarket, The Liberties, Dublin 8, D08 KD91` + `jamesonwhiskey.com` | **D08 KD91 is Teeling's address.** Jameson has two other pins on the map (Bow St. `D07 V57C`, Midleton) and no third site at Newmarket |
| `pearse-lyons-distillery` | `website: https://teelingwhiskey.com/` | Pearse Lyons' site is `pearselyonsdistillery.com`. Teeling's URL had been stapled to the wrong feature |
| `pearse-lyons-distillery` | `St. James's Gate ... D08 VF8H`, coords `53.3379, -6.2838` | `121-122 James's Street, D08 ET27`, coords `53.3437311, -6.2894326` — the old pin sat ~650 m south, off James's Street entirely |
| `roe-co-distillery` | `James's St ... D08 ET27` | `D08 ET27` is Pearse Lyons'. Roe & Co is `92 James's Street, D08 YYW9` |

A name search for "Teeling" returned nothing, which read as a coverage gap. It was a
data-integrity defect: three adjacent Dublin 8 features sharing each other's fields.

### Repairs applied

- `jameson` → renamed **Teeling Distillery**, slug `teeling-distillery`,
  website `teelingdistillery.com`, address `13-17 Newmarket, The Liberties, Dublin 8,
  D08 KD91`, coords `53.337626, -6.277099` (Nominatim, "Teeling Whiskey Company").
- `pearse-lyons-distillery` → website, address and coordinates corrected as above.
- `roe-co-distillery` → address corrected to `92 James's Street, Dublin 8, D08 YYW9`.
  Coordinates were already right and were left alone.
- `belfast-distillery` → description now names **McConnell's**, the trading name the
  Wikipedia list uses. The site itself was already on the map; only the alias was missing.

Feature `slug` is a React key on country pages, not a route
(`src/app/distilleries/[country]/page.tsx:155`), so the rename breaks no URL.

---

## Added — 7 rows

| Name | Where | Distils on site? | Source consulted |
|---|---|---|---|
| The Dublin Liberties Distillery | 33 Mill Street, Dublin 8, D08 V221 | Yes, working distillery since 2019 | thedld.com |
| Micil Distillery | 226 Upper Salthill Road, Galway, H91 N9WK | Yes, distillery + visitor centre over the Oslo Bar | micildistillery.com |
| Lambay Whiskey | Lambay Island, Co. Dublin | Yes — off-grid island micro-distillery opened May 2025 | lambaywhiskey.com; Drinks Ireland, 27 May 2025; RTÉ, 16 May 2025 |
| Listoke Distillery & Gin School | Tinure Business Park, Ballymakenny Road, Drogheda, A92 HDR7 | Yes, 50-litre still since 2016 | listokedistillery.ie |
| Ballyvolane House Spirits | Ballyvolane House, Castlelyons, Co. Cork, P61 FP70 | Yes — Bertha's Revenge milk gin distilled on site | ballyvolanespirits.ie |
| Baoilleach Distillery | Gortnabrade, Carrigart, Co. Donegal, F92 N8H3 | Yes | baoilleachdistillery.ie |
| Glendree Distillery | Glendree, Feakle, Co. Clare | Yes | Irish Whiskey Magazine distillery listing |

Coordinates from OpenStreetMap Nominatim, verified county-by-county against the
address before use. Glendree and Baoilleach are townland-level rather than
door-level; both sites are rural and neither has a mapped building.

**Lambay is included on the strength of the 2025 micro-distillery, not the brand.**
Before May 2025 Lambay was distilled elsewhere and only matured on the island, which
under the pruning rule would not have qualified.

---

## Rejected — 3, with reasons

- **Killarney Brewing & Distilling** (Fossa, Co. Kerry) — *not added.* Examinership
  failed in July 2025, a liquidator was appointed and operations ceased. Adding it
  would have put a closed site on a public map. Named in the original probe list.
- **Nephin** (Lahardane, Co. Mayo) — *not added.* The distillery building was
  completed in 2018 but there is no evidence production ever began; it is absent
  from the Irish Whiskey Association's operating list. Nominatim carries a POI for
  it, which is not evidence of distilling. Revisit if production is confirmed.
- **The Machrihanish Distillery** `region: "ireland"` — *not a defect.* This was
  filed and **retracted on 17 August 2026** (`data/audit/UK-NI-WALES-AUDIT.md`).
  `region` is a map viewport assigned from a hand-drawn bounding box, not a geography
  claim. Campbeltown at 55.44°N sits inside the box drawn around Ireland, as does the
  rest of Kintyre, which is why that box holds 16 UK rows. Its `country` is
  `United Kingdom` and is correct. Nothing to fix.

  The reason this keeps resurfacing is that the field name invites the mistake.
  The standing suggestion from that retraction — derive `region` from `country` and
  move the viewport to a separate `map_bucket` field — would stop it recurring.
  Not done here: it touches every one of the 6,138 rows and is John's call.

---

## Already correct, checked and left alone

- **Hawk's Rock Distillery** already carries `Formerly Lough Gill Distillery —
  acquired by Sazerac (2022), renamed 2025` in its description. No change needed.
- **Ballina Whiskey** already carries `Formerly Connacht Whiskey Company`. This is
  the Wikipedia list's "Connacht"; not a gap.

---

## Still open

- **`country` is inconsistent across the island.** Five features carry
  `country: "Ireland"` with a Northern Ireland postcode: Belfast Distillery,
  Rademon Estate, Scotts Irish, The Quiet Man, Titanic Distillers. First filed
  16 August in `UK-NI-WALES-AUDIT.md` (defect 1), still standing, untouched here
  because it is a jurisdiction decision rather than a data repair.
- **The probe was Irish-only.** Nothing here says the other 6,066 features are clean.
  The same crossed-fields pattern would be invisible to a name search anywhere else
  on the map, and the Dublin 8 cluster was only caught because someone knew Teeling
  should be there.
