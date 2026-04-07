"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { WOW, regionViews, type Region } from "@/lib/constants";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

const countryToRegion: Record<string, Region> = {
  Ireland: "ireland",
  "United Kingdom": "scotland",
  "United States": "usa",
  Canada: "usa",
  Japan: "asia",
  India: "asia",
  Taiwan: "asia",
  Australia: "rest",
};

function EmbedMapInner() {
  const searchParams = useSearchParams();
  const regionParam = searchParams.get("region") as Region | null;
  const countryParam = searchParams.get("country");

  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [count, setCount] = useState(0);

  const initialView = regionParam && regionViews[regionParam]
    ? regionViews[regionParam]
    : { center: [0, 30] as [number, number], zoom: 2 };

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: initialView.center,
      zoom: initialView.zoom,
      attributionControl: false,
    });

    map.current.addControl(
      new mapboxgl.AttributionControl({ compact: true }),
      "bottom-right"
    );
    map.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.current.on("load", () => {
      fetch("/data/distilleries.geojson")
        .then((res) => res.json())
        .then((data) => {
          if (countryParam) {
            data.features = data.features.filter(
              (f: GeoJSON.Feature) =>
                (f.properties as Record<string, string>)?.country?.toLowerCase() ===
                countryParam.toLowerCase()
            );
          }

          setCount(data.features.length);

          map.current!.addSource("distilleries", {
            type: "geojson",
            data,
            cluster: true,
            clusterMaxZoom: 12,
            clusterRadius: 50,
          });

          map.current!.addLayer({
            id: "clusters",
            type: "circle",
            source: "distilleries",
            filter: ["has", "point_count"],
            paint: {
              "circle-color": [
                "step",
                ["get", "point_count"],
                WOW.amberGlow, 10, WOW.amber, 50, WOW.copper,
              ],
              "circle-radius": [
                "step",
                ["get", "point_count"],
                18, 10, 24, 50, 32,
              ],
              "circle-stroke-width": 2,
              "circle-stroke-color": WOW.parchment,
            },
          });

          map.current!.addLayer({
            id: "cluster-count",
            type: "symbol",
            source: "distilleries",
            filter: ["has", "point_count"],
            layout: {
              "text-field": "{point_count_abbreviated}",
              "text-font": ["DIN Pro Medium", "Arial Unicode MS Bold"],
              "text-size": 13,
            },
            paint: { "text-color": WOW.white },
          });

          map.current!.addLayer({
            id: "unclustered-point",
            type: "circle",
            source: "distilleries",
            filter: ["!", ["has", "point_count"]],
            paint: {
              "circle-color": [
                "match",
                ["get", "region"],
                "ireland", "#1a8a4a",
                "scotland", "#2563eb",
                "usa", "#b91c1c",
                "japan", "#dc2626",
                "europe", "#7c3aed",
                "australia", "#0891b2",
                "canada", "#dc2626",
                "india", "#ea580c",
                WOW.oakLight,
              ],
              "circle-radius": 7,
              "circle-stroke-width": 2,
              "circle-stroke-color": WOW.white,
            },
          });

          map.current!.on("click", "clusters", (e) => {
            const features = map.current!.queryRenderedFeatures(e.point, { layers: ["clusters"] });
            const clusterId = features[0]?.properties?.cluster_id;
            if (clusterId === undefined) return;
            (map.current!.getSource("distilleries") as mapboxgl.GeoJSONSource).getClusterExpansionZoom(
              clusterId,
              (err, zoom) => {
                if (err || !features[0]?.geometry) return;
                const geom = features[0].geometry as GeoJSON.Point;
                map.current!.easeTo({ center: geom.coordinates as [number, number], zoom: zoom ?? undefined });
              }
            );
          });

          map.current!.on("click", "unclustered-point", (e) => {
            if (!e.features?.[0]) return;
            const geom = e.features[0].geometry as GeoJSON.Point;
            const coords = geom.coordinates.slice() as [number, number];
            const props = e.features[0].properties!;

            const html = `
              <div style="font-family: system-ui, sans-serif; max-width: 260px;">
                <strong style="font-size: 14px; color: ${WOW.oak};">${props.name}</strong>
                ${props.region ? `<div style="font-size: 11px; color: ${WOW.muted}; margin-top: 2px; text-transform: capitalize;">${props.region}</div>` : ""}
                ${props.address ? `<div style="font-size: 11px; color: ${WOW.muted}; margin-top: 3px;">${props.address}</div>` : ""}
                ${props.description ? `<p style="font-size: 12px; color: #555; margin-top: 6px; line-height: 1.4;">${props.description}</p>` : ""}
                ${props.website ? `<a href="${props.website}" target="_blank" rel="noopener noreferrer" style="font-size: 12px; color: ${WOW.amber}; margin-top: 4px; display: inline-block; font-weight: 500;">Visit website &rarr;</a>` : ""}
              </div>
            `;

            new mapboxgl.Popup({ offset: 12, maxWidth: "280px" })
              .setLngLat(coords)
              .setHTML(html)
              .addTo(map.current!);
          });

          map.current!.on("mouseenter", "clusters", () => { map.current!.getCanvas().style.cursor = "pointer"; });
          map.current!.on("mouseleave", "clusters", () => { map.current!.getCanvas().style.cursor = ""; });
          map.current!.on("mouseenter", "unclustered-point", () => { map.current!.getCanvas().style.cursor = "pointer"; });
          map.current!.on("mouseleave", "unclustered-point", () => { map.current!.getCanvas().style.cursor = ""; });
        });
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="fixed inset-0 z-50 w-full h-screen" style={{ background: WOW.parchment }}>
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Powered by watermark */}
      <a
        href="https://distillerymap.ie"
        target="_blank"
        rel="noopener noreferrer"
        className="absolute bottom-2 left-2 z-10 flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-medium shadow-md transition-opacity hover:opacity-90"
        style={{ background: WOW.oak, color: WOW.parchment }}
      >
        <span style={{ color: WOW.amberGlow }}>Distillery Map</span>
        {count > 0 && (
          <span style={{ color: WOW.muted }}>&middot; {count.toLocaleString()}</span>
        )}
      </a>
    </div>
  );
}

export default function EmbedMap() {
  return (
    <Suspense fallback={<div style={{ width: "100%", height: "100vh", background: "#faf6ee" }} />}>
      <EmbedMapInner />
    </Suspense>
  );
}
