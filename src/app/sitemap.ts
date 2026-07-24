import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/constants";
import { getCountries } from "@/lib/data";

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
    ...countries.map((c) => ({
      url: `${SITE_URL}/distilleries/${c.slug}`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
  ];
}
