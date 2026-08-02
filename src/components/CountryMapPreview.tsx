"use client";

import { useState } from "react";
import { WOW } from "@/lib/constants";

/**
 * Click-to-load facade for the country-page map.
 *
 * The iframe used to render on every page load. It pulled Mapbox GL plus the
 * full 2.1MB geojson on a page whose job is to be indexed, and because it was
 * lazy it showed as an empty white block until it painted. Google credits
 * iframe content to the embed URL (which is noindex) rather than to this page,
 * so that cost bought no ranking value at all.
 *
 * Now nothing loads until the reader asks for it. The facade reserves the exact
 * same height, so there's no layout shift when it swaps.
 */
export function CountryMapPreview({
  src,
  countryName,
}: {
  src: string;
  countryName: string;
}) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div
      className="mt-8 overflow-hidden rounded-2xl"
      style={{ border: `1px solid ${WOW.parchmentDark}` }}
    >
      {loaded ? (
        <iframe
          src={src}
          title={`Map of distilleries in ${countryName}`}
          className="h-96 w-full"
        />
      ) : (
        <button
          type="button"
          onClick={() => setLoaded(true)}
          className="flex h-96 w-full flex-col items-center justify-center gap-3 transition-colors"
          style={{ background: WOW.parchment }}
        >
          <span
            className="rounded-full px-5 py-2.5 text-sm font-medium"
            style={{ background: WOW.amber, color: WOW.white }}
          >
            Show the interactive map
          </span>
          <span className="text-xs" style={{ color: WOW.muted }}>
            Every distillery in {countryName}, plotted. Loads on demand.
          </span>
        </button>
      )}
    </div>
  );
}
