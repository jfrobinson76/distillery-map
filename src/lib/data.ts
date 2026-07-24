import { promises as fs } from "fs";
import path from "path";
import { cache } from "react";

// Server-side reader for the same geojson the map fetches client-side.
// Used by page metadata, JSON-LD, sitemap, and (later) country pages.
export const getDistilleryData = cache(
  async (): Promise<GeoJSON.FeatureCollection<GeoJSON.Point>> => {
    const raw = await fs.readFile(
      path.join(process.cwd(), "public", "data", "distilleries.geojson"),
      "utf8"
    );
    return JSON.parse(raw);
  }
);

export async function getDistilleryCount(): Promise<number> {
  const data = await getDistilleryData();
  return data.features.length;
}
