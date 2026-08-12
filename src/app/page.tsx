import type { Metadata } from "next";
import Link from "next/link";
import DistilleryMapApp from "@/components/DistilleryMapApp";
import { getCountries, getDistilleryCount } from "@/lib/data";
import { SITE_URL, WOW } from "@/lib/constants";

/* How many country links ride in the footer row. Short on purpose: the point is
   to concentrate crawl signal on the biggest pages, which a long list undoes. */
const FOOTER_COUNTRY_LINKS = 12;

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

/* Welcome-overlay copy, server-rendered so it exists in crawlable HTML.
   The client overlay shell (backdrop + dismiss) lives in DistilleryMapApp. */
function WelcomeCopy({ count }: { count: number }) {
  return (
    <>
      <h2 className="text-2xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
        Distillery Map
      </h2>
      <p className="mt-3 text-sm leading-relaxed" style={{ color: WOW.muted }}>
        A free, open distillery map &mdash;{" "}
        <strong style={{ color: WOW.amber }}>{count.toLocaleString()}</strong>{" "}
        distilleries, tasting rooms, and spirit producers &mdash; and growing.
        Built by the community.
      </p>

      <div className="mt-6 space-y-3 text-sm" style={{ color: WOW.muted }}>
        <div className="flex items-start gap-3">
          <span
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            style={{ background: WOW.amber, color: WOW.white }}
          >1</span>
          <span><strong style={{ color: WOW.charcoal }}>Explore</strong> &mdash; zoom, pan, and click any pin for details</span>
        </div>
        <div className="flex items-start gap-3">
          <span
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            style={{ background: WOW.amber, color: WOW.white }}
          >2</span>
          <span><strong style={{ color: WOW.charcoal }}>Filter</strong> &mdash; use the region buttons to fly to Ireland, Scotland, USA, and more</span>
        </div>
        <div className="flex items-start gap-3">
          <span
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            style={{ background: WOW.amber, color: WOW.white }}
          >3</span>
          <span><strong style={{ color: WOW.charcoal }}>Contribute</strong> &mdash; know a distillery we&apos;re missing? Add it, report a closure, or suggest a fix</span>
        </div>
      </div>

      <p className="mt-5 text-xs" style={{ color: WOW.muted }}>
        Prefer a list?{" "}
        <Link href="/distilleries" className="underline" style={{ color: WOW.amber }}>
          Browse distilleries by country
        </Link>
        .
      </p>
    </>
  );
}

export default async function Page() {
  const [count, countries] = await Promise.all([getDistilleryCount(), getCountries()]);

  /* getCountries() is already sorted by size. Ireland is pinned on top of the
     cut because it anchors the whiskey audience this map is built for, and it
     sits just outside the largest dozen on raw distillery count. */
  const top = countries.slice(0, FOOTER_COUNTRY_LINKS);
  const ireland = countries.find((c) => c.slug === "ireland");
  const topCountries = [...top, ...(ireland && !top.includes(ireland) ? [ireland] : [])].map(
    ({ name, slug, count }) => ({ name, slug, count })
  );

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": `${SITE_URL}/#organization`,
        name: "Distillery Map",
        url: SITE_URL,
        email: "hello@distillerymap.org",
      },
      {
        "@type": "WebSite",
        "@id": `${SITE_URL}/#website`,
        name: "Distillery Map",
        url: SITE_URL,
        description: `A free, open distillery map with ${count.toLocaleString("en-US")} distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.`,
        publisher: { "@id": `${SITE_URL}/#organization` },
      },
      {
        "@type": "Dataset",
        "@id": `${SITE_URL}/#dataset`,
        name: "Distillery Map — worldwide distillery dataset",
        description: `Community-built dataset of ${count.toLocaleString("en-US")} distilleries, tasting rooms, and spirit producers worldwide, with names, locations, websites, and visitor information. Compiled from OpenStreetMap, Wikidata, and community submissions.`,
        url: SITE_URL,
        creator: { "@id": `${SITE_URL}/#organization` },
        spatialCoverage: "Worldwide",
        isAccessibleForFree: true,
        keywords: ["distillery", "whiskey", "whisky", "distilleries", "map", "spirits"],
        distribution: {
          "@type": "DataDownload",
          encodingFormat: "application/geo+json",
          contentUrl: `${SITE_URL}/data/distilleries.geojson`,
        },
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />
      <DistilleryMapApp
        count={count}
        welcome={<WelcomeCopy count={count} />}
        topCountries={topCountries}
      />
    </>
  );
}
