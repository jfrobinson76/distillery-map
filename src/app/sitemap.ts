import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/constants";

// Country and distillery pages will be appended here as they ship (SEO phases 2a/2b).
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1,
    },
  ];
}
