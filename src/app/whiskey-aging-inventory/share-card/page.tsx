import type { Metadata } from "next";
import AgingInventoryMap from "@/components/AgingInventoryMap";
import { WOW } from "@/lib/constants";
import {
  TIERS,
  TOTAL,
  BIG_TWO_SHARE,
  US_YEARS_OF_SUPPLY,
  INDIA_SHARE,
  type Tier,
} from "@/lib/aging-inventory";

/**
 * A fixed 1200x1200 card, built to be screenshotted for social rather than
 * browsed. The world map on its own is 2.66:1 — LinkedIn squashes that into an
 * unreadable strip, so the map sits as a band inside a square instead.
 *
 * Regenerate the PNG with:
 *   npm run share-card
 */
export const metadata: Metadata = {
  title: "Share card",
  robots: { index: false, follow: false },
};

const TIER_ORDER: Tier[] = ["counted", "estimate", "producer", "dark"];

export default function ShareCard() {
  return (
    <div
      id="share-card"
      style={{
        width: 1200,
        height: 1200,
        background: WOW.parchment,
        display: "flex",
        flexDirection: "column",
        padding: "48px 44px 0",
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      <style>{"nextjs-portal,#__next-build-watcher{display:none!important}"}</style>
      <div
        style={{
          fontSize: 17,
          fontWeight: 700,
          letterSpacing: "0.18em",
          color: WOW.amber,
          textTransform: "uppercase",
        }}
      >
        DistilleryMap.org
      </div>

      <h1
        className="font-[family-name:var(--font-fraunces)]"
        style={{
          margin: "14px 0 0",
          fontSize: 58,
          lineHeight: 1.05,
          fontWeight: 700,
          color: WOW.oak,
          letterSpacing: "-0.01em",
        }}
      >
        How much whiskey is aging
        <br />
        in the world?
      </h1>

      <div style={{ display: "flex", alignItems: "baseline", gap: 18, marginTop: 20 }}>
        <div
          className="font-[family-name:var(--font-fraunces)]"
          style={{ fontSize: 76, fontWeight: 700, color: WOW.copper, lineHeight: 1 }}
        >
          ~{Math.round(TOTAL.central)} million casks
        </div>
      </div>
      <div style={{ marginTop: 10, fontSize: 21, color: WOW.oakLight }}>
        Range {TOTAL.low}–{TOTAL.high} million. Almost certainly the most ever maturing at
        one time.
      </div>

      <div style={{ marginTop: 20, marginLeft: -44, marginRight: -44 }}>
        <AgingInventoryMap />
      </div>

      <div style={{ display: "flex", gap: 26, marginTop: 18, flexWrap: "wrap" }}>
        {TIER_ORDER.map((t) => (
          <div key={t} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                width: 14,
                height: 14,
                borderRadius: 3,
                background: TIERS[t].color,
                display: "inline-block",
              }}
            />
            <span style={{ fontSize: 16, color: WOW.oakLight, fontWeight: 600 }}>
              {TIERS[t].label}
            </span>
          </div>
        ))}
      </div>

      {/* Fills the band under the legend, and these are the three figures most
          likely to get argued with — which is the point of the post. */}
      <div style={{ display: "flex", gap: 20, marginTop: 26 }}>
        {[
          { v: `${BIG_TWO_SHARE}%`, l: "is held by just two countries: the US and Scotland." },
          { v: `${US_YEARS_OF_SUPPLY} yrs`, l: "of American whiskey supply sitting at current demand." },
          { v: `${INDIA_SHARE}%`, l: "is India's share \u2014 despite outselling everyone on earth." },
        ].map((s) => (
          <div
            key={s.v}
            style={{
              flex: 1,
              background: WOW.white,
              border: `1px solid ${WOW.parchmentDark}`,
              borderRadius: 16,
              padding: "18px 20px",
            }}
          >
            <div
              className="font-[family-name:var(--font-fraunces)]"
              style={{ fontSize: 40, fontWeight: 700, color: WOW.copper, lineHeight: 1 }}
            >
              {s.v}
            </div>
            <div style={{ marginTop: 8, fontSize: 16, lineHeight: 1.3, color: WOW.oakLight }}>
              {s.l}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          background: WOW.oak,
          color: WOW.parchment,
          borderRadius: "22px 22px 0 0",
          padding: "30px 44px 34px",
          marginLeft: -44,
          marginRight: -44,
          marginTop: "auto",
          flexShrink: 0,
        }}
      >
        <div
          style={{ fontSize: 29, lineHeight: 1.3, color: WOW.amberGlow, fontWeight: 700 }}
        >
          Which country have we got wrong? Tell me in the comments.
        </div>
        <div style={{ marginTop: 10, fontSize: 20, color: WOW.parchmentDark }}>
          Every figure, source and caveat is on DistilleryMap.org — including
          the ones that make our own numbers look weak.
        </div>
      </div>
    </div>
  );
}
