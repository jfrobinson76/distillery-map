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

/** One barrel seen end-on: staved circle with a hoop ring and a bung dot. */
function Barrel({ cx, cy, r, fill }: { cx: number; cy: number; r: number; fill: string }) {
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={fill} stroke="#3b2314" strokeOpacity={0.55} strokeWidth={1} />
      {r >= 4.5 && (
        <>
          <circle cx={cx} cy={cy} r={r * 0.62} fill="none" stroke="#faf6ee" strokeWidth={0.9} strokeOpacity={0.5} />
          <circle cx={cx} cy={cy} r={Math.max(0.8, r * 0.13)} fill="#faf6ee" fillOpacity={0.55} />
        </>
      )}
    </g>
  );
}

/**
 * A mound built from actual casks: pyramid rows of barrel ends, the way old
 * trade maps drew warehouse stocks. The footprint stays area-proportional
 * (w x h from the sqrt rule); barrel size adapts per mound so each stack
 * stays legible — the honesty lives in the footprint, not the barrel count.
 */
function BarrelMound({ entry }: { entry: Entry }) {
  const [x, baseY] = project(entry.lon, entry.lat);
  const w = moundWidth(entry.central);
  const h = w * RATIO;
  const fill = TIERS[entry.tier].color;

  const shadow = (
    <ellipse
      cx={x}
      cy={baseY + 1.5}
      rx={w / 2 + 2}
      ry={Math.max(2, w * 0.05)}
      fill="#3b2314"
      opacity={0.13}
    />
  );

  // Tiny entries are a single cask — drawn to true scale, which is the point.
  if (w <= 20) {
    return (
      <g>
        {shadow}
        <Barrel cx={x} cy={baseY - w / 2} r={w / 2} fill={fill} />
      </g>
    );
  }

  const d = w / Math.max(3, Math.round(w / 17));
  const r = d / 2;
  const rowStep = d * 0.85; // rows nest into the gaps below
  const rows = Math.max(2, Math.round(h / rowStep));

  const barrels = [];
  for (let k = 0; k < rows; k++) {
    const y = baseY - r - k * rowStep;
    const rowW = w * (1 - k / rows);
    const count = Math.max(1, Math.round(rowW / d));
    const startX = x - ((count - 1) * d) / 2;
    for (let j = 0; j < count; j++) {
      barrels.push(<Barrel key={`${k}-${j}`} cx={startX + j * d} cy={y} r={r} fill={fill} />);
    }
    if (count === 1) break;
  }

  return (
    <g>
      {shadow}
      {barrels}
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
