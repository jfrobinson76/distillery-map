#!/usr/bin/env python3
"""Remove records that carry the word "distillery" but are not distilleries.

Google Places matched on the name, so the dataset picked up a hiking trailhead,
an office park, an art gallery, a startup incubator, a running shop and a
holiday let. They inflate the count the homepage renders, which is the one
number the site's credibility rests on.

Removal is by EXPLICIT SLUG, never by pattern. A pattern pass over names looked
tempting and would have deleted Wilderness Trail Distillery, Wiggly Bridge
Distillery, Junction 56, Burnt Church, Trailhead Spirits and Spirit Lab
Distilling — all real producers whose names happen to contain "trail",
"bridge", "junction" or "lab". Names are not evidence. This list is hand-checked,
one entry at a time, with the reason recorded.

Museums and visitor centres attached to working distilleries are NOT removed
(Van Kleef, Cardrona, Old Hokonui, Yilan). A distillery can have a museum; it
cannot be a conservation area.

Spirit category is never grounds for removal. A distillery that makes only gin,
vodka, schnapps, grappa or liqueur stays. The question this script asks is
"does anything get distilled here", not "is it whiskey".

Tasting rooms are NOT removed. The product defines itself as "distilleries,
tasting rooms, and spirit producers" (CLAUDE.md), so an off-site tasting room
is a product-scope question for John, not a data-quality defect. The 2026-08-16
pass lists them for review instead — see
docs/data-quality/removed-non-distilleries-2026-08-16.md.

Every removal is written to data/audit/pruned_non_distilleries.json so the
decision is reversible and defensible later.

Run: .venv/bin/python scripts/prune_non_distilleries.py          # dry run
     .venv/bin/python scripts/prune_non_distilleries.py --apply
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILLERIES = ROOT / "public" / "data" / "distilleries.geojson"
AUDIT = ROOT / "data" / "audit" / "pruned_non_distilleries.json"

# slug -> why it is not a distillery
REMOVE = {
    "distillery-apartments": "residential apartments, Germany",
    "distillery-bend-trailhead": "hiking trailhead",
    "distillery-commons": "office park, Louisville",
    "distillery-gallery": "art gallery",
    "distillery-labs": "startup incubator",
    "distillery-road-conservation-area": "conservation area",
    "mercidistillery-magasin-de-running-trail-outdoor-provisions-a-grenoble":
        "running and outdoor shop, Grenoble",
    "the-distillery-lavender-farm-studio-apartment-family-room-with-garden-view":
        "holiday rental",
    "the-distillers-library": "whisky bar, not a producer",
    "the-distillers-library-bangkok": "whisky bar, not a producer",
    "the-whisky-distillery-marina-bay-sands": "whisky retail and bar, not a producer",
    "madan-singh-anand-sons-storage-tanks-liquor-bottling-plant-distillation-plant-rectified-spirit-plant-pot-still-plant":
        "equipment supplier and bottling plant, not a producer",
}

# --- 2026-08-16 pass -------------------------------------------------------
# Second sweep. Same rule: explicit slug, evidence per row, never a pattern.
# Each entry was checked against its own website or an independent source
# before it went on this list; the full evidence table with the URL consulted
# is docs/data-quality/removed-non-distilleries-2026-08-16.md.
#
# Spirit category was never a reason. Every removal below is a place where
# nothing is distilled, or a second pin on a producer that is already mapped.

REMOVE.update({
    # Breweries that make beer only. A name containing "Brewery" is not
    # evidence either way — eight brewery-named rows were checked and KEPT
    # because they also distil (Braunstein, Wilderen, Bourgogne des Flandres,
    # Elch-Bräu, Neunspringe, Tagohinke, TTL Puli, Colts Neck Stillhouse).
    "71-brewery": "brewery, beer only — 71 Brewing, Dundee; core range is five beers, tour covers brewing only",
    "madrugada-brewing-company-brewpub": "brewpub, beer only — all-beer range, no still referenced anywhere",
    "wuri-brewery": "brewery, beer only — one of TTL's three beer plants; TTL's distilling sits in its separate distilleries",
    "talisman-brewing-company": "brewery, beer only — beer-only taproom; Visit Ogden lists Ogden's Own as the city's distillery",
    "bent-river-brewing-company": "brewery, beer only — craft brewery and brewpub; only spirits link is buying used barrels",
    "ivory-bill-brewing": "brewery, beer only — craft brewery and taproom, no still; now permanently closed",
    "eureka-springs-brewery": "brewery, beer only — small-batch brewery, all beer brewed on site",
    "coachella-valley-brewing-company": "brewery, beer only — brewery and taproom, no distilling on site",
    "roughhouse-brewing": "brewery, beer only — ranch brewery making ales, lagers and foeder-aged beers",

    # Holiday lets, guesthouses and hostels. Most were picked up from Google
    # Places listings whose website is a booking-site URL.
    "plockton-distillery-flat": "holiday rental — listing on isleofskyerentals.com",
    "seaside-cottage-at-steinhart-distillery-with-ocean-views-cottage-1": "holiday rental — despegar.com hotel listing; Steinhart's distillery is mapped separately",
    "seaside-cottage-at-steinhart-distillery-with-ocean-views-pet-friendly": "holiday rental — bluepillow.com listing; second pin on the same cottage",
    "grand-canyon-brewery-and-distillery-cabin-historic-tack-house": "holiday rental — despegar.com listing; the brewery-distillery itself is mapped separately",
    "mama-bear-s-retreat-near-water-park-distillery-great-for-families": "holiday rental — bluepillow.com listing",
    "the-distillery-at-hocking-hills-retreats": "holiday rental — bluepillow.com listing; Hocking Hills Moonshine is mapped separately",
    "rustic-luxury-w-horses-historic-whiskey-distillery": "holiday rental — despegar.com listing",
    "the-little-distillery-three-bedroom-house": "holiday rental — bluepillow.com listing",
    "distillery-4-federow-distillery": "holiday rental — vrbo.com listing",
    "art-douro-historic-distillery": "holiday rental — airbnb.com listing",
    "palmse-distillery-guesthouse-double-room": "guesthouse room — bluepillow.com listing",
    "palmse-distillery-guesthouse-viinavabriku-kulalistemaja": "guesthouse in the former distillery at Palmse manor, run by the museum; seasonal rooms, no distilling",
    "nynas-hostel-distillery": "STF hostel in an 1801 farm-distillery building; distilling ceased mid-19th century",
    "the-distillery-studio-room": "named guest room at Mountain Road Estate; the farm distils lavender oil, not spirits",

    # Hotel in a converted distillery. Hôtel de la Distillerie in Corsica was
    # checked and KEPT — that one really does distil.
    "garrigae-distillerie-de-pezenas-hotellerie-et-spa": "hotel and spa in a rehabilitated former distillery; no production",

    # Restaurants and venues that do not distil.
    "the-distillery-restaurant-mt-hope": "sports bar and grill chain in Rochester NY, no spirits production",
    "the-distillery-restaurant-henrietta": "sports bar and grill chain in Rochester NY, no spirits production",
    "the-distillery-restaurant-victor": "sports bar and grill chain in Rochester NY, no spirits production",
    "la-distillerie-restaurant-brasserie": "brasserie inside the Domaine de la Chartreuse hotel, Gosnay; no production",
    "rj-cinema-distillery-taproom": "cinema and taproom; its own copy puts production at a separate distillery in Norwood",

    # Equipment, supplies and plant vendors. They sell to distilleries.
    "mile-hi-distilling": "home-distilling equipment retailer, Wheat Ridge CO — sells stills and kits, not spirits",
    "affordable-distillery-equipment-llc": "distillery equipment retailer",
    "5-star-brewing-distilling-supplies-qld": "brewing and distilling supply shop, Capalaba QLD",
    "moonshine-distillery-supplies": "equipment importer and retailer, South Africa",
    "millside-craft-distilling-supplies-online-store": "online distilling-supplies store, Benoni; premises by appointment only",
    "micet-distillery-equipment-manufacturer": "brewing and distilling equipment manufacturer, turnkey systems for other producers",
    "procient-engineering-pvt-ltd-distillery-plant-manufacturers-corporate-office": "distillery plant engineering firm; supplies distillation modules to plant owners",
    "larco-india-pvt-ltd-etp-stp-wtp-plant-manufacturer-and-supplier-in-maharashtra-cpu-for-sugar-and-distillery": "effluent and water treatment plant manufacturer; distilleries are its clients",
    "distiller-warehouse-ltd": "water-distiller and water-purification retailer, Western Canada — nothing to do with spirits",

    # Other businesses that are not distilleries.
    "the-distillery-studio-s-modyrts-music": "recording studio, Port Elizabeth",

    # Historic ruin, not an operating producer.
    "chevalier-de-villarcon-distillery-ruins": "colonial distillery ruins at Sainte-Anne, Martinique; a ruin among the sugar and rum estate remains",

    # Second pins on a producer that is already mapped: administrative offices,
    # sales agencies and off-site brand shops at a different address from the
    # working site. The parent slug is named so each one is reversible.
    # Offices with NO parent on the map were deliberately LEFT IN — deleting
    # them would take the producer off the map entirely.
    "o-donnell-moonshine-hq-kein-verkauf": "brand head office in Berlin-Mitte, the row itself says 'kein Verkauf'; parent o-donnell-moonshine",
    "office-range-and-proof-house-royal-lochnagar-distillery": "wikidata listed-building record for a building inside the distillery; parent royal-lochnagar-distillery",
    "adinco-distillery-office": "office pin 1.8 km from the plant; parent adinco-distilleries",
    "grainfuel-distilleries-private-limited-head-office": "corporate office in Ahmedabad, plant is in Matar; parent grainfuel-distilleries-private-limited",
    "rockland-distilleries-head-office": "head office in Colombo, production site is at Seethawakapura; parent rockland-distillery-bottling-plant",
    "monument-distillers-nigeria-factory-office": "office pin 21 km from the mapped company site, and its website points at an unrelated UK distiller; parent monument-distillers-nigeria-ltd",
    "forgood-distillery-franchise-store": "franchise retail outlet; parent forgood-distillery",
    "forgood-distillery-general-agency": "sales agency in Guangzhou; parent forgood-distillery",
    "forgood-distillery-liyang-general-agency": "sales agency in Liyang; parent forgood-distillery",
    "aura-distillery-shop-zagreb": "brand shop in Zagreb, 200 km from the producer; parents aura / destilerija-aura / aura-family-distillery",
    "aura-distillery-shop-krk": "brand shop on Krk; parents aura / destilerija-aura / aura-family-distillery",
    "distillery-aura-shop": "brand shop in Rovinj; parents aura / destilerija-aura / aura-family-distillery",
    "distilleries-et-domaines-de-provence-store-museum": "town-centre store and museum, production is at Z.A. Les Chalus; parent distilleries-et-domaines-de-provence",
    "la-boutique-by-d4f-distillerie-des-4-freres": "brand boutique on a different street; parent distillerie-des-4-freres",
    "distillerie-bonollo-shop-anagni-fr": "brand shop in Anagni; parent distillerie-bonollo-s-p-a",
})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = json.loads(DISTILLERIES.read_text())
    before = len(data["features"])

    removed, kept = [], []
    for f in data["features"]:
        slug = f["properties"].get("slug")
        if slug in REMOVE:
            removed.append({
                "slug": slug,
                "name": f["properties"].get("name"),
                "country": f["properties"].get("country"),
                "source": f["properties"].get("source"),
                "reason": REMOVE[slug],
            })
        else:
            kept.append(f)

    found = {r["slug"] for r in removed}
    missing = sorted(set(REMOVE) - found)

    print(f"before: {before}")
    print(f"removing: {len(removed)}")
    for r in removed:
        print(f"  {r['name'][:52]:54}{r['reason']}")
    if missing:
        print(f"\nlisted but not found ({len(missing)}) — already gone or slug changed:")
        for m in missing:
            print(f"  {m}")
    print(f"\nafter: {before - len(removed)}")

    if args.apply:
        data["features"] = kept
        DISTILLERIES.write_text(json.dumps(data, ensure_ascii=False))

        # Append, never overwrite. Earlier passes already ran and their rows are
        # no longer in the geojson, so a plain write would erase the only record
        # that they were ever removed.
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        ledger = json.loads(AUDIT.read_text()) if AUDIT.exists() else []
        known = {r["slug"] for r in ledger}
        ledger.extend(r for r in removed if r["slug"] not in known)
        AUDIT.write_text(json.dumps(ledger, indent=2, ensure_ascii=False))
        print(f"\nwrote {DISTILLERIES.relative_to(ROOT)}")
        print(f"ledger {AUDIT.relative_to(ROOT)}: {len(ledger)} rows "
              f"(+{len(ledger) - len(known)} this run)")
    else:
        print("\ndry run — nothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
