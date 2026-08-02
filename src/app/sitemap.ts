import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/constants";
import { getCountries } from "@/lib/data";
import { countryCopy } from "@/lib/country-copy";

/**
 * Countries whose intro copy has been written and reviewed carry a real
 * lastmod. The rest still serve the shared fallback sentence and genuinely
 * haven't changed, so they get an older date.
 *
 * This used to stamp new Date() on all 71 pages every build, which tells
 * Google the whole site changed every time anything deployed. Google ignores
 * lastmod it decides is unreliable, and re-crawl priority is the entire point
 * of the exercise — so it has to be honest to be worth sending.
 */
const COPY_SHIPPED = new Date("2026-08-02");
const FALLBACK_UNCHANGED = new Date("2026-07-28");

// Per-distillery pages join here when they ship (SEO phase 2b).
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const countries = await getCountries();
  const now = new Date();
  return [
    { url: SITE_URL, lastModified: now, changeFrequency: "weekly", priority: 1 },
    {
      url: `${SITE_URL}/distilleries`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    ...countries.map((c) => {
      const hasCopy = Boolean(countryCopy[c.slug]);
      return {
        url: `${SITE_URL}/distilleries/${c.slug}`,
        lastModified: hasCopy ? COPY_SHIPPED : FALLBACK_UNCHANGED,
        changeFrequency: "monthly" as const,
        priority: hasCopy ? 0.8 : 0.5,
      };
    }),
  ];
}
