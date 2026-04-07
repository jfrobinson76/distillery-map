"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { WOW, FORMSPREE_SUBMIT_ID, regionViews, regionLabels, type Region } from "@/lib/constants";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

/* ─── Welcome Overlay ─── */
function WelcomeOverlay({ onClose, count }: { onClose: () => void; count: number }) {
  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center p-4" style={{ background: "rgba(43, 30, 18, 0.6)" }}>
      <div className="w-full max-w-md rounded-2xl shadow-2xl p-8" style={{ background: WOW.parchment }}>
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

        <button
          onClick={onClose}
          className="mt-8 w-full rounded-full px-6 py-3 text-sm font-medium transition-colors"
          style={{ background: WOW.amber, color: WOW.white }}
          onMouseEnter={(e) => (e.currentTarget.style.background = WOW.amberLight)}
          onMouseLeave={(e) => (e.currentTarget.style.background = WOW.amber)}
        >
          Explore the Map
        </button>
      </div>
    </div>
  );
}

/* ─── Submit / Report Panel ─── */
type SubmitType = "add" | "closure" | "correction";

function SubmitPanel({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [submitType, setSubmitType] = useState<SubmitType>("add");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("sending");
    const form = e.currentTarget;

    try {
      const res = await fetch(`https://formspree.io/f/${FORMSPREE_SUBMIT_ID}`, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });

      if (res.ok) {
        setStatus("sent");
        form.reset();
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }

  const inputClass =
    "mt-1 w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors";

  const headings: Record<SubmitType, string> = {
    add: "Add a Distillery",
    closure: "Report a Closure",
    correction: "Suggest a Correction",
  };

  const successMessages: Record<SubmitType, string> = {
    add: "We'll review and add it to the map.",
    closure: "We'll verify and update the map.",
    correction: "We'll review and make the fix.",
  };

  return (
    <div
      className="absolute top-0 right-0 z-20 h-full w-full max-w-sm shadow-2xl overflow-y-auto"
      style={{ background: WOW.parchment, borderLeft: `1px solid ${WOW.parchmentDark}` }}
    >
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold" style={{ color: WOW.oak }}>{headings[submitType]}</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full transition-colors text-lg"
            style={{ color: WOW.muted }}
            onMouseEnter={(e) => (e.currentTarget.style.background = WOW.parchmentDark)}
            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        {/* Type selector */}
        <div className="mt-4 flex gap-1 rounded-lg p-1" style={{ background: WOW.parchmentDark }}>
          {(["add", "closure", "correction"] as SubmitType[]).map((type) => (
            <button
              key={type}
              onClick={() => setSubmitType(type)}
              className="flex-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors capitalize"
              style={{
                background: submitType === type ? WOW.amber : "transparent",
                color: submitType === type ? WOW.white : WOW.muted,
              }}
            >
              {type === "add" ? "Add New" : type === "closure" ? "Closure" : "Correction"}
            </button>
          ))}
        </div>

        {status === "sent" ? (
          <div
            className="mt-8 rounded-xl p-6 text-center"
            style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
          >
            <p className="text-base font-semibold" style={{ color: WOW.oak }}>Thanks!</p>
            <p className="mt-2 text-sm" style={{ color: WOW.muted }}>
              {successMessages[submitType]}
            </p>
            <button
              onClick={onClose}
              className="mt-4 rounded-full px-4 py-2 text-sm font-medium transition-colors"
              style={{ background: WOW.amber, color: WOW.white }}
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <input type="hidden" name="form_type" value={submitType} />

            <div>
              <label htmlFor="distillery_name" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Distillery Name *
              </label>
              <input
                type="text"
                id="distillery_name"
                name="distillery_name"
                required
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            {submitType === "add" && (
              <>
                <div>
                  <label htmlFor="location" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Location (city, region, country) *
                  </label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    required
                    placeholder="e.g. Midleton, Co. Cork, Ireland"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="website" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Website
                  </label>
                  <input
                    type="url"
                    id="website"
                    name="website"
                    placeholder="https://"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="spirit_type" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    What do they distil?
                  </label>
                  <input
                    type="text"
                    id="spirit_type"
                    name="spirit_type"
                    placeholder="e.g. Single malt whiskey, bourbon, gin"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>
              </>
            )}

            {submitType === "closure" && (
              <div>
                <label htmlFor="details" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                  Any details? (year closed, source)
                </label>
                <textarea
                  id="details"
                  name="details"
                  rows={3}
                  placeholder="e.g. Closed in 2023, building demolished"
                  className={`${inputClass} resize-none`}
                  style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                />
              </div>
            )}

            {submitType === "correction" && (
              <>
                <div>
                  <label htmlFor="correction_website" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Website
                  </label>
                  <input
                    type="url"
                    id="correction_website"
                    name="website"
                    placeholder="https://"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Description / tagline
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={2}
                    placeholder="e.g. Independent craft distillery specialising in single malt"
                    className={`${inputClass} resize-none`}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="visitor_info" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Visitor info <span style={{ color: WOW.muted, fontWeight: "normal" }}>(tours, tastings, shop)</span>
                  </label>
                  <input
                    type="text"
                    id="visitor_info"
                    name="visitor_info"
                    placeholder="e.g. Tours daily, booking required"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="booking_link" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Booking / visit link
                  </label>
                  <input
                    type="url"
                    id="booking_link"
                    name="booking_link"
                    placeholder="https://"
                    className={inputClass}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>

                <div>
                  <label htmlFor="correction_details" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                    Anything else to fix?
                  </label>
                  <textarea
                    id="correction_details"
                    name="details"
                    rows={2}
                    placeholder="e.g. Wrong location, name is misspelled"
                    className={`${inputClass} resize-none`}
                    style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
                  />
                </div>
              </>
            )}

            <div>
              <label htmlFor="submitter_email" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Your email <span style={{ color: WOW.muted, fontWeight: "normal" }}>(optional)</span>
              </label>
              <input
                type="email"
                id="submitter_email"
                name="submitter_email"
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <p className="text-xs" style={{ color: WOW.muted }}>
              By submitting, you confirm this information is accurate and agree it may be
              published on the Distillery Map. Your email is only used to follow up
              on your submission.
            </p>

            {status === "error" && (
              <p className="text-xs" style={{ color: "#dc2626" }}>
                Something went wrong. Email{" "}
                <a href="mailto:hello@distillerymap.ie" className="underline">hello@distillerymap.ie</a> instead.
              </p>
            )}

            <button
              type="submit"
              disabled={status === "sending"}
              className="w-full rounded-full px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-50"
              style={{ background: WOW.amber, color: WOW.white }}
              onMouseEnter={(e) => { if (status !== "sending") e.currentTarget.style.background = WOW.amberLight; }}
              onMouseLeave={(e) => (e.currentTarget.style.background = WOW.amber)}
            >
              {status === "sending"
                ? "Submitting..."
                : submitType === "add"
                ? "Submit Distillery"
                : submitType === "closure"
                ? "Report Closure"
                : "Submit Correction"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

/* ─── Claim Panel ─── */
function ClaimPanel({ distilleryName, onClose }: { distilleryName: string; onClose: () => void }) {
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("sending");
    const form = e.currentTarget;

    try {
      const res = await fetch(`https://formspree.io/f/${FORMSPREE_SUBMIT_ID}`, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });

      if (res.ok) {
        setStatus("sent");
        form.reset();
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }

  const inputClass =
    "mt-1 w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors";

  return (
    <div
      className="absolute top-0 right-0 z-20 h-full w-full max-w-sm shadow-2xl overflow-y-auto"
      style={{ background: WOW.parchment, borderLeft: `1px solid ${WOW.parchmentDark}` }}
    >
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold" style={{ color: WOW.oak }}>Claim This Listing</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full transition-colors text-lg"
            style={{ color: WOW.muted }}
            onMouseEnter={(e) => (e.currentTarget.style.background = WOW.parchmentDark)}
            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        <p className="mt-3 text-sm" style={{ color: WOW.muted }}>
          Work at <strong style={{ color: WOW.charcoal }}>{distilleryName}</strong>?
          Claim your listing to make sure your details are accurate and up to date.
        </p>

        {status === "sent" ? (
          <div
            className="mt-8 rounded-xl p-6 text-center"
            style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
          >
            <p className="text-base font-semibold" style={{ color: WOW.oak }}>Thanks!</p>
            <p className="mt-2 text-sm" style={{ color: WOW.muted }}>
              We&apos;ll verify your claim and update the listing.
            </p>
            <button
              onClick={onClose}
              className="mt-4 rounded-full px-4 py-2 text-sm font-medium transition-colors"
              style={{ background: WOW.amber, color: WOW.white }}
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <input type="hidden" name="form_type" value="claim" />
            <input type="hidden" name="distillery_name" value={distilleryName} />

            <div>
              <label htmlFor="claim_name" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Your Name *
              </label>
              <input
                type="text"
                id="claim_name"
                name="contact_name"
                required
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div>
              <label htmlFor="claim_email" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Your Email *
              </label>
              <input
                type="email"
                id="claim_email"
                name="contact_email"
                required
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div>
              <label htmlFor="claim_role" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Your Role *
              </label>
              <input
                type="text"
                id="claim_role"
                name="contact_role"
                required
                placeholder="e.g. Owner, Marketing Manager, Head Distiller"
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div className="border-t pt-4" style={{ borderColor: WOW.parchmentDark }}>
              <p className="text-xs font-medium mb-3" style={{ color: WOW.charcoal }}>
                Update your listing details <span style={{ color: WOW.muted, fontWeight: "normal" }}>(optional)</span>
              </p>
            </div>

            <div>
              <label htmlFor="claim_website" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Website
              </label>
              <input
                type="url"
                id="claim_website"
                name="website"
                placeholder="https://"
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div>
              <label htmlFor="claim_description" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Description / tagline
              </label>
              <textarea
                id="claim_description"
                name="description"
                rows={2}
                placeholder="e.g. Family-owned craft distillery specialising in single pot still whiskey"
                className={`${inputClass} resize-none`}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div>
              <label htmlFor="claim_visitor_info" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Visitor info <span style={{ color: WOW.muted, fontWeight: "normal" }}>(tours, tastings, shop)</span>
              </label>
              <input
                type="text"
                id="claim_visitor_info"
                name="visitor_info"
                placeholder="e.g. Tours daily 10am-5pm, booking recommended"
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            <div>
              <label htmlFor="claim_booking" className="block text-xs font-medium" style={{ color: WOW.charcoal }}>
                Booking / visit link
              </label>
              <input
                type="url"
                id="claim_booking"
                name="booking_link"
                placeholder="https://"
                className={inputClass}
                style={{ borderColor: WOW.parchmentDark, background: WOW.white }}
              />
            </div>

            {status === "error" && (
              <p className="text-xs" style={{ color: "#dc2626" }}>
                Something went wrong. Email{" "}
                <a href="mailto:hello@distillerymap.ie" className="underline">hello@distillerymap.ie</a> instead.
              </p>
            )}

            <button
              type="submit"
              disabled={status === "sending"}
              className="w-full rounded-full px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-50"
              style={{ background: WOW.amber, color: WOW.white }}
              onMouseEnter={(e) => { if (status !== "sending") e.currentTarget.style.background = WOW.amberLight; }}
              onMouseLeave={(e) => (e.currentTarget.style.background = WOW.amber)}
            >
              {status === "sending" ? "Submitting..." : "Claim Listing"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

/* ─── Search Component ─── */
function SearchBar({ features, onSelect }: {
  features: GeoJSON.Feature[];
  onSelect: (coords: [number, number], name: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GeoJSON.Feature[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSearch(q: string) {
    setQuery(q);
    if (q.length < 2) { setResults([]); setOpen(false); return; }
    const lower = q.toLowerCase();
    const matches = features
      .filter((f) => {
        const name = (f.properties as Record<string, string>)?.name || "";
        return name.toLowerCase().includes(lower);
      })
      .slice(0, 8);
    setResults(matches);
    setOpen(matches.length > 0);
  }

  function handleSelect(f: GeoJSON.Feature) {
    const geom = f.geometry as GeoJSON.Point;
    const name = (f.properties as Record<string, string>)?.name || "";
    onSelect(geom.coordinates as [number, number], name);
    setQuery(name);
    setOpen(false);
  }

  return (
    <div ref={ref} className="relative w-full sm:w-64">
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => { if (results.length > 0) setOpen(true); }}
        placeholder="Search distilleries..."
        className="w-full rounded-full px-4 py-1.5 text-xs outline-none"
        style={{ background: WOW.oakLight, color: WOW.parchment, border: "none" }}
        aria-label="Search distilleries"
      />
      {open && (
        <div
          className="absolute top-full left-0 right-0 mt-1 rounded-xl shadow-lg overflow-hidden z-50"
          style={{ background: WOW.parchment, border: `1px solid ${WOW.parchmentDark}` }}
        >
          {results.map((f, i) => {
            const props = f.properties as Record<string, string>;
            return (
              <button
                key={i}
                onClick={() => handleSelect(f)}
                className="w-full text-left px-3 py-2 text-xs transition-colors hover:bg-[#f0e8d4] flex flex-col"
              >
                <span className="font-medium" style={{ color: WOW.oak }}>{props.name}</span>
                {props.region && (
                  <span className="text-[10px] capitalize" style={{ color: WOW.muted }}>{props.region}{props.address ? ` · ${props.address.split(",").slice(-2).join(",").trim()}` : ""}</span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ─── Main Map Page ─── */
export default function DistilleryMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [activeRegion, setActiveRegion] = useState<Region>("all");
  const [distilleryCount, setDistilleryCount] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [showSubmit, setShowSubmit] = useState(false);
  const [showClaim, setShowClaim] = useState(false);
  const [claimDistillery, setClaimDistillery] = useState("");
  const [allFeatures, setAllFeatures] = useState<GeoJSON.Feature[]>([]);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [0, 30],
      zoom: 2,
      attributionControl: false,
    });

    map.current.addControl(
      new mapboxgl.AttributionControl({ compact: true }),
      "bottom-right"
    );
    map.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    // Listen for claim link clicks (Mapbox popups are outside React)
    function handleClaimClick(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (target.classList.contains("claim-link")) {
        e.preventDefault();
        const name = target.dataset.distillery || "";
        setClaimDistillery(name);
        setShowClaim(true);
      }
    }
    document.addEventListener("click", handleClaimClick);

    map.current.on("load", () => {
      fetch("/data/distilleries.geojson")
        .then((res) => res.json())
        .then((data) => {
          setDistilleryCount(data.features.length);
          setAllFeatures(data.features);

          map.current!.addSource("distilleries", {
            type: "geojson",
            data,
            cluster: true,
            clusterMaxZoom: 12,
            clusterRadius: 50,
          });

          // Cluster circles
          map.current!.addLayer({
            id: "clusters",
            type: "circle",
            source: "distilleries",
            filter: ["has", "point_count"],
            paint: {
              "circle-color": [
                "step",
                ["get", "point_count"],
                WOW.amberGlow,
                10,
                WOW.amber,
                50,
                WOW.copper,
              ],
              "circle-radius": [
                "step",
                ["get", "point_count"],
                18,
                10,
                24,
                50,
                32,
              ],
              "circle-stroke-width": 2,
              "circle-stroke-color": WOW.parchment,
            },
          });

          // Cluster count labels
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
            paint: {
              "text-color": WOW.white,
            },
          });

          // Individual distillery points
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

          // Click on cluster to zoom
          map.current!.on("click", "clusters", (e) => {
            const features = map.current!.queryRenderedFeatures(e.point, {
              layers: ["clusters"],
            });
            const clusterId = features[0]?.properties?.cluster_id;
            if (clusterId === undefined) return;

            (
              map.current!.getSource("distilleries") as mapboxgl.GeoJSONSource
            ).getClusterExpansionZoom(clusterId, (err, zoom) => {
              if (err || !features[0]?.geometry) return;
              const geom = features[0].geometry as GeoJSON.Point;
              map.current!.easeTo({
                center: geom.coordinates as [number, number],
                zoom: zoom ?? undefined,
              });
            });
          });

          // Click on individual point for popup
          map.current!.on("click", "unclustered-point", (e) => {
            if (!e.features?.[0]) return;
            const geom = e.features[0].geometry as GeoJSON.Point;
            const coords = geom.coordinates.slice() as [number, number];
            const props = e.features[0].properties!;

            const hasRichData = props.visitor_info || props.booking_link;
            const escapedName = (props.name || "").replace(/"/g, "&quot;").replace(/'/g, "&#39;");

            const html = `
              <div style="font-family: system-ui, sans-serif; max-width: 260px;">
                <strong style="font-size: 14px; color: ${WOW.oak};">${props.name}</strong>
                ${props.region ? `<div style="font-size: 11px; color: ${WOW.muted}; margin-top: 2px; text-transform: capitalize;">${props.region}</div>` : ""}
                ${props.address ? `<div style="font-size: 11px; color: ${WOW.muted}; margin-top: 3px;">${props.address}</div>` : ""}
                ${props.description ? `<p style="font-size: 12px; color: #555; margin-top: 6px; line-height: 1.4;">${props.description}</p>` : ""}
                ${hasRichData && props.visitor_info ? `<div style="font-size: 11px; color: ${WOW.charcoal}; margin-top: 6px; padding: 6px 8px; background: ${WOW.parchmentDark}; border-radius: 6px;">${props.visitor_info}</div>` : ""}
                <div style="margin-top: 8px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                  ${props.website ? `<a href="${props.website}" target="_blank" rel="noopener noreferrer" style="font-size: 12px; color: ${WOW.amber}; font-weight: 500;">Visit website &rarr;</a>` : ""}
                  ${hasRichData && props.booking_link ? `<a href="${props.booking_link}" target="_blank" rel="noopener noreferrer" style="font-size: 12px; color: ${WOW.amber}; font-weight: 500;">Book a visit &rarr;</a>` : ""}
                </div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid ${WOW.parchmentDark};">
                  <a href="#" class="claim-link" data-distillery="${escapedName}" style="font-size: 11px; color: ${WOW.muted}; text-decoration: none;">Is this your distillery? Claim it.</a>
                </div>
              </div>
            `;

            new mapboxgl.Popup({ offset: 12, maxWidth: "280px" })
              .setLngLat(coords)
              .setHTML(html)
              .addTo(map.current!);
          });

          // Cursor styles
          map.current!.on("mouseenter", "clusters", () => {
            map.current!.getCanvas().style.cursor = "pointer";
          });
          map.current!.on("mouseleave", "clusters", () => {
            map.current!.getCanvas().style.cursor = "";
          });
          map.current!.on("mouseenter", "unclustered-point", () => {
            map.current!.getCanvas().style.cursor = "pointer";
          });
          map.current!.on("mouseleave", "unclustered-point", () => {
            map.current!.getCanvas().style.cursor = "";
          });

          setLoaded(true);
        });
    });

    return () => {
      document.removeEventListener("click", handleClaimClick);
      map.current?.remove();
      map.current = null;
    };
  }, []);

  function flyTo(region: Region) {
    setActiveRegion(region);
    const view = regionViews[region];
    map.current?.flyTo({
      center: view.center,
      zoom: view.zoom,
      duration: 1500,
    });
  }

  return (
    <div className="relative flex flex-col h-dvh overflow-hidden">
      {/* Header bar */}
      <div
        className="px-4 py-3 sm:px-6 z-10"
        style={{ background: WOW.oak, borderBottom: `1px solid ${WOW.oakLight}` }}
      >
        <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1
              className="text-xl font-bold font-[family-name:var(--font-fraunces)]"
              style={{ color: WOW.amberGlow }}
            >
              Distillery Map
            </h1>
            {loaded && (
              <p className="text-xs" style={{ color: WOW.parchmentDark }}>
                {distilleryCount.toLocaleString()} locations and counting &middot;{" "}
                <button
                  onClick={() => setShowSubmit(true)}
                  className="underline transition-colors"
                  style={{ color: WOW.amberGlow }}
                >
                  Know somewhere we&apos;re missing?
                </button>
              </p>
            )}
          </div>

          {/* Search + Region filters */}
          <div className="flex flex-wrap items-center gap-2">
            {loaded && (
              <SearchBar
                features={allFeatures}
                onSelect={(coords, name) => {
                  map.current?.flyTo({ center: coords, zoom: 14, duration: 1500 });
                  setTimeout(() => {
                    new mapboxgl.Popup({ offset: 12, maxWidth: "280px" })
                      .setLngLat(coords)
                      .setHTML(`<div style="font-family: system-ui, sans-serif;"><strong style="font-size: 14px; color: ${WOW.oak};">${name}</strong></div>`)
                      .addTo(map.current!);
                  }, 1600);
                }}
              />
            )}
            <div className="hidden sm:block w-px h-5" style={{ background: WOW.oakLight }} />
            {(Object.keys(regionLabels) as Region[]).map((region) => (
              <button
                key={region}
                onClick={() => flyTo(region)}
                className="rounded-full px-3 py-1.5 text-xs font-medium transition-colors"
                style={{
                  background: activeRegion === region ? WOW.amber : WOW.oakLight,
                  color: activeRegion === region ? WOW.white : WOW.parchmentDark,
                }}
              >
                {regionLabels[region]}
              </button>
            ))}

            <div className="hidden sm:block w-px h-5 mx-1" style={{ background: WOW.oakLight }} />

            <button
              onClick={() => setShowSubmit(true)}
              className="rounded-full px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1"
              style={{ background: WOW.amber, color: WOW.white }}
              title="Contribute a place"
            >
              + Contribute
            </button>
          </div>
        </div>
      </div>

      {/* Map */}
      <div ref={mapContainer} className="flex-1 relative">
        {/* Welcome overlay */}
        {showWelcome && loaded && (
          <WelcomeOverlay
            onClose={() => setShowWelcome(false)}
            count={distilleryCount}
          />
        )}

        {/* Submit panel */}
        {showSubmit && <SubmitPanel onClose={() => setShowSubmit(false)} />}

        {/* Claim panel */}
        {showClaim && (
          <ClaimPanel
            distilleryName={claimDistillery}
            onClose={() => setShowClaim(false)}
          />
        )}
      </div>

      {/* Footer bar */}
      <div
        className="px-4 py-2 sm:px-6 z-10"
        style={{ background: WOW.oak, borderTop: `1px solid ${WOW.oakLight}` }}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between text-[10px]" style={{ color: WOW.muted }}>
          <span>
            Data: Google Places, OpenStreetMap, Wikidata &middot;{" "}
            <a href="mailto:hello@distillerymap.ie" style={{ color: WOW.amberGlow }}>
              hello@distillerymap.ie
            </a>
          </span>
          <span>
            &copy; {new Date().getFullYear()} Distillery Map
          </span>
        </div>
      </div>
    </div>
  );
}
