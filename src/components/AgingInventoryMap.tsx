import {
  MAP_WIDTH,
  MAP_HEIGHT,
  WORLD_BASE_PATH,
  COUNTRY_PATHS,
  project,
} from "@/lib/world-map-paths";
import { ENTRIES, ISO_TIER, TIERS, type Entry } from "@/lib/aging-inventory";

/**
 * Mounds are scaled by AREA, not height — a mound holding twice as much covers
 * twice the ink, not twice the height. Scaling by height is the classic way to
 * make a small producer look like a rival, and it is the main thing wrong with
 * most versions of this chart.
 */
const K = 38; // width in map units for sqrt(millions of casks)
const RATIO = 0.62; // height as a fraction of base width — squat and stable

// Breathing room for labels pulled off their mounds, and a crop at the bottom
// to drop the empty southern ocean.
const PAD = 40;
const PAD_RIGHT = 50;
const CROP_BOTTOM = 33;
const VB = {
  x: -PAD,
  y: -PAD,
  w: MAP_WIDTH + PAD + PAD_RIGHT,
  h: MAP_HEIGHT + PAD - CROP_BOTTOM,
};

const moundWidth = (m: number) => K * Math.sqrt(m);

function fmt(m: number) {
  if (m >= 1) return `${m % 1 === 0 ? m : m.toFixed(1)}m`;
  return `${Math.round(m * 1000)}k`;
}

/**
 * A traditional stacked-cask mound: a triangle built out of rows, with the row
 * divided into individual cask ends. Row i holds i+1 casks, which is how these
 * things were drawn on old trade maps.
 */
function BarrelMound({ entry }: { entry: Entry }) {
  const [x, baseY] = project(entry.lon, entry.lat);
  const w = moundWidth(entry.central);
  const h = w * RATIO;
  const apexY = baseY - h;
  const fill = TIERS[entry.tier].color;

  // Rows scale with the mound so tiny ones don't turn into mush.
  const rows = Math.max(2, Math.min(9, Math.round(h / 9)));
  const rowH = h / rows;
  const halfAt = (y: number) => (w / 2) * ((y - apexY) / h);

  const bands = [];
  for (let i = 0; i < rows; i++) {
    const yTop = apexY + i * rowH;
    const yBot = apexY + (i + 1) * rowH;
    const tHalf = halfAt(yTop);
    const bHalf = halfAt(yBot);
    const d = `M${x - tHalf} ${yTop}L${x + tHalf} ${yTop}L${x + bHalf} ${yBot}L${
      x - bHalf
    } ${yBot}Z`;

    // Cask divisions inside the row — only when there is room to see them.
    const casks = i + 1;
    const ticks = [];
    if (rowH > 5) {
      for (let j = 1; j < casks; j++) {
        const f = j / casks;
        ticks.push(
          <line
            key={j}
            x1={x - tHalf + 2 * tHalf * f}
            y1={yTop}
            x2={x - bHalf + 2 * bHalf * f}
            y2={yBot}
            stroke="#faf6ee"
            strokeWidth={0.9}
            strokeOpacity={0.55}
          />
        );
      }
    }

    bands.push(
      <g key={i}>
        <path d={d} fill={fill} fillOpacity={i % 2 === 0 ? 1 : 0.86} />
        {ticks}
      </g>
    );
  }

  return (
    <g>
      {/* Ground shadow so the mound sits on the map rather than floating. */}
      <ellipse
        cx={x}
        cy={baseY + 1.5}
        rx={w / 2 + 2}
        ry={Math.max(2, w * 0.05)}
        fill="#3b2314"
        opacity={0.13}
      />
      {bands}
      <path
        d={`M${x} ${apexY}L${x + w / 2} ${baseY}L${x - w / 2} ${baseY}Z`}
        fill="none"
        stroke="#3b2314"
        strokeOpacity={0.45}
        strokeWidth={1}
      />
    </g>
  );
}

function Label({ entry }: { entry: Entry }) {
  const [x, baseY] = project(entry.lon, entry.lat);
  const h = moundWidth(entry.central) * RATIO;
  const lx = x + entry.dx;
  const ly = baseY - h + entry.dy;

  const halo = {
    stroke: "#faf6ee",
    strokeWidth: 5,
    strokeLinejoin: "round" as const,
    paintOrder: "stroke" as const,
  };

  return (
    <g>
      {/* Leader from the label back to the mound apex when it is pulled away. */}
      {(Math.abs(entry.dx) > 20 || Math.abs(entry.dy) > 24) && (
        <line
          x1={lx}
          y1={ly + 4}
          x2={x}
          y2={baseY - h}
          stroke="#8a7e6e"
          strokeWidth={0.9}
          strokeDasharray="3 3"
        />
      )}
      <text
        x={lx}
        y={ly}
        textAnchor={entry.anchor}
        fontSize={17}
        fontWeight={700}
        fill="#2a2520"
        {...halo}
      >
        {entry.name}
      </text>
      <text
        x={lx}
        y={ly + 17}
        textAnchor={entry.anchor}
        fontSize={16}
        fontWeight={700}
        fill={TIERS[entry.tier].color}
        {...halo}
      >
        ~{fmt(entry.central)} casks
      </text>
      <text
        x={lx}
        y={ly + 31}
        textAnchor={entry.anchor}
        fontSize={11}
        fill="#8a7e6e"
        {...halo}
      >
        range {fmt(entry.low)}–{fmt(entry.high)}
      </text>
    </g>
  );
}

/** Dot + tie-line for mounds parked offshore to make room. */
function Anchor({ entry }: { entry: Entry }) {
  if (entry.anchorLon === undefined || entry.anchorLat === undefined) return null;
  const [ax, ay] = project(entry.anchorLon, entry.anchorLat);
  const [mx, my] = project(entry.lon, entry.lat);
  return (
    <g>
      <line
        x1={mx}
        y1={my}
        x2={ax}
        y2={ay}
        stroke="#8a4a1c"
        strokeWidth={1.1}
        strokeOpacity={0.55}
        strokeDasharray="4 3"
      />
      <circle cx={ax} cy={ay} r={3.2} fill="#8a4a1c" />
    </g>
  );
}

export default function AgingInventoryMap() {
  // Biggest mounds drawn first so small ones stay on top and legible.
  const ordered = [...ENTRIES].sort((a, b) => b.central - a.central);

  return (
    <svg
      viewBox={`${VB.x} ${VB.y} ${VB.w} ${VB.h}`}
      className="block h-auto w-full"
      role="img"
      aria-label="Flat world map showing estimated whiskey aging inventory by country, drawn as stacked-cask mounds scaled by area."
    >
      <rect x={VB.x} y={VB.y} width={VB.w} height={VB.h} fill="#faf6ee" />

      {/* Land */}
      <path d={WORLD_BASE_PATH} fill="#e6dcc6" stroke="#d6c9ac" strokeWidth={0.5} />
      {Object.entries(COUNTRY_PATHS).map(([iso, d]) => {
        const tier = ISO_TIER[iso];
        return (
          <path
            key={iso}
            d={d}
            fill={tier ? TIERS[tier].color : "#e6dcc6"}
            fillOpacity={tier ? 0.2 : 1}
            stroke="#c9b894"
            strokeWidth={0.6}
          />
        );
      })}

      {ordered.map((e) => (
        <Anchor key={`a-${e.id}`} entry={e} />
      ))}
      {ordered.map((e) => (
        <BarrelMound key={`m-${e.id}`} entry={e} />
      ))}
      {ordered.map((e) => (
        <Label key={`l-${e.id}`} entry={e} />
      ))}
    </svg>
  );
}
