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

/* ── Country aggregation for /distilleries pages ── */

// Countries below this count don't get their own page (thin-content guard)
const MIN_COUNTRY_PAGE = 5;

export type CountryEntry = {
  name: string; // display name as stored in the data, e.g. "United States"
  slug: string;
  count: number;
  /** "region" for the Scotland special page, otherwise "country" */
  kind: "country" | "region";
};

export function slugifyName(name: string): string {
  return name
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

// Countries whose names read naturally with "the" ("distilleries in the United States")
const THE_COUNTRIES = new Set([
  "United States",
  "United Kingdom",
  "Netherlands",
  "Czech Republic",
  "Philippines",
  "Bahamas",
  "Isle of Man",
]);

export function countryDisplayName(name: string): string {
  return THE_COUNTRIES.has(name) ? `the ${name}` : name;
}

type DistilleryProps = {
  name?: string;
  country?: string;
  region?: string;
  website?: string;
  description?: string;
  address?: string;
  slug?: string;
  claimed?: boolean;
};

export const getCountries = cache(async (): Promise<CountryEntry[]> => {
  const data = await getDistilleryData();
  const counts = new Map<string, number>();
  let scotland = 0;
  for (const f of data.features) {
    const props = f.properties as DistilleryProps;
    const c = props.country?.trim();
    if (c) counts.set(c, (counts.get(c) ?? 0) + 1);
    if (props.region === "scotland") scotland++;
  }
  const entries: CountryEntry[] = [...counts.entries()]
    .filter(([, n]) => n >= MIN_COUNTRY_PAGE)
    .map(([name, count]) => ({
      name,
      slug: slugifyName(name),
      count,
      kind: "country" as const,
    }));
  // Scotland is a region in the data (part of the UK) but the single most
  // searched distillery geography — it gets its own page.
  if (scotland >= MIN_COUNTRY_PAGE) {
    entries.push({ name: "Scotland", slug: "scotland", count: scotland, kind: "region" });
  }
  return entries.sort((a, b) => b.count - a.count);
});

export async function getCountryBySlug(
  slug: string
): Promise<{ entry: CountryEntry; features: GeoJSON.Feature<GeoJSON.Point, DistilleryProps>[] } | null> {
  const [countries, data] = await Promise.all([getCountries(), getDistilleryData()]);
  const entry = countries.find((c) => c.slug === slug);
  if (!entry) return null;
  const features = (data.features as GeoJSON.Feature<GeoJSON.Point, DistilleryProps>[])
    .filter((f) =>
      entry.kind === "region"
        ? f.properties.region === "scotland"
        : f.properties.country?.trim() === entry.name
    )
    .sort((a, b) => (a.properties.name || "").localeCompare(b.properties.name || ""));
  return { entry, features };
}
