"""
Export the Stillbound outreach universe from the Distillery Map dataset.

IMPORTANT — read before trusting the output.

The geojson has no spirit-category field. Its properties are name, source,
region, country, description, address, slug, website. Nothing records whether a
site makes whiskey, gin, rum or brandy. So this script CANNOT produce a
"whiskey distillery list", and any file that claims to be one is inferring.

What it produces instead is the addressable universe inside Stillbound's stated
jurisdiction sequence (IE -> NI -> UK -> US -> CA), tiered by that sequence, with
an honest confidence column:

  whiskey_signal = "explicit"  name/description/website literally says whisk(e)y,
                               bourbon, rye, single malt, scotch. High confidence.
                 = "unknown"   no signal either way. Most rows land here, because
                               the majority are simply named "<Placename> Distillery".
                               NOT a negative signal.

Enrichment (website scrape or a manual pass) is the missing step between this
file and a real target list. Tier 1 is 57 rows and can be checked by hand in an
afternoon; that is the near-term Irish-whiskey GTM anyway.

Usage:  python3 scripts/export_outreach_universe.py <output.csv>
"""
import csv
import json
import re
import sys
from pathlib import Path

GEOJSON = Path(__file__).resolve().parent.parent / "public/data/distilleries.geojson"
SITE = "https://distillerymap.org/distilleries"

SIGNAL = re.compile(r"whisk|bourbon|\brye\b|single malt|scotch|cooperage", re.I)

# Stillbound's jurisdiction sequence. Scotland is a region inside the UK in this
# data, so it is split out here the same way the map's country pages split it.
def tier(props):
    country = (props.get("country") or "").strip()
    if country == "Ireland":
        return "1 - Ireland"
    if country == "United Kingdom":
        return "2 - Scotland" if props.get("region") == "scotland" else "3 - Rest of UK"
    if country == "United States":
        return "4 - United States"
    if country == "Canada":
        return "5 - Canada"
    return None


def main(out_path):
    data = json.loads(GEOJSON.read_text())
    rows = []
    for feature in data["features"]:
        props = feature["properties"]
        t = tier(props)
        if not t:
            continue
        blob = " ".join(str(props.get(k) or "") for k in ("name", "description", "website"))
        coords = feature.get("geometry", {}).get("coordinates") or [None, None]
        rows.append(
            {
                "name": props.get("name") or "",
                "tier": t,
                "country": (props.get("country") or "").strip(),
                "region": props.get("region") or "",
                "address": props.get("address") or "",
                "website": props.get("website") or "",
                "whiskey_signal": "explicit" if SIGNAL.search(blob) else "unknown",
                "has_website": "yes" if props.get("website") else "no",
                "claimed_on_map": "yes" if props.get("claimed") else "no",
                "longitude": coords[0],
                "latitude": coords[1],
                "map_page": f"{SITE}/{_slug(props)}",
                "source": props.get("source") or "",
            }
        )

    rows.sort(key=lambda r: (r["tier"], r["name"].lower()))

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} rows -> {out_path}")
    for t in sorted({r["tier"] for r in rows}):
        sub = [r for r in rows if r["tier"] == t]
        exp = sum(1 for r in sub if r["whiskey_signal"] == "explicit")
        web = sum(1 for r in sub if r["has_website"] == "yes")
        print(f"  {t:20s} {len(sub):5d}  explicit whiskey signal: {exp:4d}  with website: {web:5d}")


def _slug(props):
    country = (props.get("country") or "").strip()
    if country == "United Kingdom" and props.get("region") == "scotland":
        return "scotland"
    return re.sub(r"[^a-z0-9]+", "-", country.lower()).strip("-")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "outreach-universe.csv")
