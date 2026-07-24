import { ImageResponse } from "next/og";
import { getDistilleryCount } from "@/lib/data";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt =
  "Distillery Map — every distillery in the world on one free map";

const WOW = {
  amber: "#c47b2b",
  amberGlow: "#e8a94e",
  oak: "#3b2314",
  parchment: "#faf6ee",
  parchmentDark: "#f0e8d4",
  muted: "#8a7e6e",
};

export default async function Image() {
  const count = await getDistilleryCount();

  // Fixed pseudo-random pin scatter as a map motif (deterministic for stable builds)
  const pins = [
    [80, 120], [180, 90], [140, 210], [280, 160], [90, 300], [240, 320],
    [960, 110], [1060, 170], [1010, 260], [900, 210], [1100, 340], [950, 380],
    [320, 80], [860, 90], [1130, 120], [60, 420], [1140, 460],
  ];

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: WOW.oak,
          position: "relative",
        }}
      >
        {pins.map(([x, y], i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: i % 3 === 0 ? 22 : 12,
              height: i % 3 === 0 ? 22 : 12,
              borderRadius: "50%",
              background: i % 2 === 0 ? WOW.amber : WOW.amberGlow,
              opacity: 0.55,
            }}
          />
        ))}
        <div
          style={{
            fontSize: 92,
            fontWeight: 700,
            color: WOW.amberGlow,
            letterSpacing: "-2px",
          }}
        >
          Distillery Map
        </div>
        <div
          style={{
            marginTop: 24,
            fontSize: 38,
            color: WOW.parchment,
            textAlign: "center",
            maxWidth: 900,
          }}
        >
          {`${count.toLocaleString("en-US")} distilleries, tasting rooms, and spirit producers — on one free map`}
        </div>
        <div
          style={{
            marginTop: 48,
            fontSize: 28,
            color: WOW.muted,
          }}
        >
          distillerymap.org
        </div>
      </div>
    ),
    size
  );
}
