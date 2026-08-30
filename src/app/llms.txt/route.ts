import { getCountries, getDistilleryCount, countryDisplayName } from "@/lib/data";
import { countryCopy } from "@/lib/country-copy";
import { TOTAL } from "@/lib/aging-inventory";
import { SITE_URL } from "@/lib/constants";

// llms.txt is generated, not hand-written: the count, the country list and the
// research figures all change, and a stale file is worse than none.
export const dynamic = "force-static";

export async function GET() {
  const count = await getDistilleryCount();
  const countries = await getCountries();
  const withCopy = countries.filter((c) => countryCopy[c.slug]);
  const rest = countries.filter((c) => !countryCopy[c.slug]);
  const n = count.toLocaleString("en-US");

  const lines = [
    "# Distillery Map by Stillbound",
    "",
    `> A free, open map of ${n} distilleries, tasting rooms and spirit producers worldwide, community-built and verified against the inclusion standard "listed and trading". ${SITE_URL}`,
    "",
    "## What this site is",
    "",
    `Distillery Map is the largest free, open map of the world's distilleries: ${n} sites across ${countries.length} countries, covering whiskey, whisky, bourbon, rum, gin, brandy and other spirits. It is a product of Stillbound (https://stillbound.ai), the AI platform for the whiskey industry. Data comes from OpenStreetMap, Wikidata, national registers and community submissions, and every addition since August 2026 carries a proving source. Anyone can submit a distillery, report a closure or suggest a correction. Distillery owners can claim their listing free of charge; a claimed listing shows a verified badge.`,
    "",
    "## Key facts",
    "",
    `- ${n} distilleries, tasting rooms and spirit producers mapped, in ${countries.length} countries`,
    "- A pin means a real address where spirits are distilled today, or a real place belonging to a producer or brand (marked as head office, brand shop, tasting room or bottling plant)",
    "- Closed, demolished and planned sites are not listed",
    "- Free to use, no account, no paywall",
    `- Dataset available as GeoJSON: ${SITE_URL}/data/distilleries.geojson`,
    `- Embeddable map for partner sites: ${SITE_URL}/embed`,
    "",
    "## Research",
    "",
    `- How much whiskey is aging in the world: ${SITE_URL}/whiskey-aging-inventory. Best estimate ${TOTAL.central} million casks maturing worldwide, source-bounded range ${TOTAL.low} to ${TOTAL.high} million, with each country tiered by source quality.`,
    "",
    "## Country pages with editorial",
    "",
    ...withCopy.map(
      (c) => `- Distilleries in ${countryDisplayName(c.name)} (${c.count}): ${SITE_URL}/distilleries/${c.slug}`
    ),
    "",
    "## Other country pages",
    "",
    ...rest.map((c) => `- ${c.name} (${c.count}): ${SITE_URL}/distilleries/${c.slug}`),
    "",
    "## Other pages",
    "",
    `- All countries: ${SITE_URL}/distilleries`,
    `- Privacy: ${SITE_URL}/privacy`,
    "",
    "## For distillery owners",
    "",
    "Claim your listing from its map popup to correct details, add brands made at the site, and add visitor information. Claiming is free. Contact details from a claim are used only to manage the listing.",
    "",
    "## Contact",
    "",
    "hello@stillbound.ai",
    "",
  ];

  return new Response(lines.join("\n"), {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}
