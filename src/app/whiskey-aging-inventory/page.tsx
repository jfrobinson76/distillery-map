import type { Metadata } from "next";
import Link from "next/link";
import AgingInventoryMap from "@/components/AgingInventoryMap";
import { WOW } from "@/lib/constants";
import { getDistilleryCount } from "@/lib/data";
import {
  ENTRIES,
  TIERS,
  TOTAL,
  BIG_TWO_SHARE,
  DARK_SHARE,
  US_YEARS_OF_SUPPLY,
  BOTTLE_EQUIVALENT_BN,
  INDIA_SHARE,
  type Tier,
} from "@/lib/aging-inventory";

const TITLE = "How Much Whiskey Is Aging in the World?";
const DESCRIPTION = `Best estimate: ${TOTAL.central} million casks of whiskey maturing worldwide. Source-bounded scenarios span ${TOTAL.low}–${TOTAL.high} million, with the data gaps left visible.`;

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  alternates: { canonical: "/whiskey-aging-inventory" },
  openGraph: {
    title: `${TITLE} — Distillery Map by Stillbound`,
    description: DESCRIPTION,
    url: "/whiskey-aging-inventory",
    type: "article",
  },
  // Without this the root layout's generic site copy ("A free, open map of
  // distilleries...") is what X and any twitter-tag reader previews for this
  // article. openGraph was overridden here; twitter was not.
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

const TIER_ORDER: Tier[] = ["counted", "derived", "estimate", "producer", "dark"];

function fmt(m: number) {
  return m >= 1 ? `${m % 1 === 0 ? m : m.toFixed(1)}m` : `${Math.round(m * 1000)}k`;
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div
      className="rounded-2xl px-5 py-5"
      style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
    >
      <div
        className="font-[family-name:var(--font-fraunces)] text-3xl font-bold leading-none"
        style={{ color: WOW.copper }}
      >
        {value}
      </div>
      <div className="mt-2 text-xs leading-relaxed" style={{ color: WOW.muted }}>
        {label}
      </div>
    </div>
  );
}

export default async function AgingInventoryPage() {
  const total = await getDistilleryCount();
  const ranked = [...ENTRIES].sort((a, b) => b.central - a.central);

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Article",
        headline: TITLE,
        description: DESCRIPTION,
        url: "https://distillerymap.org/whiskey-aging-inventory",
        datePublished: "2026-08-02",
        author: { "@type": "Organization", name: "Stillbound", url: "https://stillbound.ai" },
        publisher: { "@type": "Organization", name: "Distillery Map by Stillbound", url: "https://distillerymap.org" },
        about: {
          "@type": "Dataset",
          name: "Global whiskey aging inventory estimate",
          description: `Country-by-country estimate of whiskey casks in maturation, ${TOTAL.central}m central with a ${TOTAL.low}m to ${TOTAL.high}m range, each figure tiered by source quality.`,
          creator: { "@type": "Organization", name: "Stillbound" },
          license: "https://creativecommons.org/licenses/by/4.0/",
        },
      },
      {
        "@type": "FAQPage",
        mainEntity: [
          {
            "@type": "Question",
            name: "How many casks of whiskey are aging in the world?",
            acceptedAnswer: {
              "@type": "Answer",
              text: `About ${TOTAL.central} million casks, with source-bounded scenarios from ${TOTAL.low} million to ${TOTAL.high} million. The United States and Scotland together hold roughly ${BIG_TWO_SHARE}% of it.`,
            },
          },
          {
            "@type": "Question",
            name: "Which countries hold the most maturing whiskey?",
            acceptedAnswer: {
              "@type": "Answer",
              text: ranked
                .slice(0, 5)
                .map((e) => `${e.name}: about ${e.central} million casks`)
                .join("; ") + ".",
            },
          },
          {
            "@type": "Question",
            name: "How reliable are these figures?",
            acceptedAnswer: {
              "@type": "Answer",
              text: `Each country is tiered by source quality, from counted (trade-body or government inventories) to dark (no published figure). About ${DARK_SHARE}% of the central estimate sits in countries with no counted source.`,
            },
          },
        ],
      },
    ],
  };

  return (
    <div className="min-h-dvh" style={{ background: WOW.parchment }}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />
      <header
        className="px-4 py-3 sm:px-6"
        style={{ background: WOW.oak, borderBottom: `1px solid ${WOW.oakLight}` }}
      >
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <Link
            href="/"
            className="text-xl font-bold font-[family-name:var(--font-fraunces)]"
            style={{ color: WOW.amberGlow }}
          >
            Distillery Map
          </Link>
          <Link
            href="/"
            className="rounded-full px-3 py-1.5 text-xs font-medium"
            style={{ background: WOW.amber, color: WOW.white }}
          >
            Open the map
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <p
          className="text-xs font-semibold uppercase tracking-widest"
          style={{ color: WOW.amber }}
        >
          Research
        </p>
        <h1
          className="mt-2 font-[family-name:var(--font-fraunces)] text-3xl font-bold leading-tight sm:text-5xl"
          style={{ color: WOW.oak }}
        >
          How much whisk(e)y is aging in the world?
        </h1>
        <p
          className="mt-4 max-w-2xl text-base leading-relaxed"
          style={{ color: WOW.oakLight }}
        >
          Nobody actually knows. There is no world census of maturing whisk(e)y — no
          registry, no agreed unit, no shared reporting year. What follows is the best
          estimate we can build from what producers and trade bodies publish, with the
          holes left where they are rather than papered over.
        </p>

        <div
          className="mt-8 rounded-2xl px-6 py-7"
          style={{ background: WOW.oak, color: WOW.parchment }}
        >
          <div className="text-xs uppercase tracking-widest" style={{ color: WOW.amberGlow }}>
            Best estimate, August 2026
          </div>
          <div className="mt-2 font-[family-name:var(--font-fraunces)] text-4xl font-bold leading-none sm:text-6xl">
            {TOTAL.central} million<span style={{ color: WOW.amberGlow }}>*</span> casks
          </div>
          <div className="mt-3 text-sm" style={{ color: WOW.parchmentDark }}>
            Source-bounded scenarios: {TOTAL.low}–{TOTAL.high} million. The lower case
            applies every regional low at once; it is not a statistical confidence
            interval. Scotland and America both describe their own maturing stocks as
            record highs, and they hold most of the world&apos;s.
          </div>
          {/* The social card carries the same asterisk. Anyone arriving from it should
              find the footnote here rather than wonder what it pointed at. */}
          <div className="mt-3 text-xs" style={{ color: WOW.parchmentDark }}>
            <span style={{ color: WOW.amberGlow }}>*</span> A total assembled by
            Stillbound from published counts and stated-method derivations. Counted,
            estimated and guessed figures are marked separately for every country below.
          </div>
        </div>

        {/* ---------- The map ---------- */}
        <section className="mt-10">
          {/* The map is 2000 units wide — squeezed onto a phone the labels turn
              to mush, so let it scroll sideways below tablet width. */}
          <div
            className="overflow-x-auto rounded-2xl"
            style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
          >
            <div className="min-w-[720px]">
              <AgingInventoryMap />
            </div>
          </div>
          <p className="mt-2 text-xs sm:hidden" style={{ color: WOW.muted }}>
            Scroll the map sideways to see it all.
          </p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {TIER_ORDER.map((t) => (
              <div key={t} className="flex gap-2.5">
                <span
                  className="mt-1 h-3 w-3 shrink-0 rounded-sm"
                  style={{ background: TIERS[t].color }}
                />
                <div>
                  <div className="text-xs font-semibold" style={{ color: WOW.oak }}>
                    {TIERS[t].label}
                  </div>
                  <div className="mt-0.5 text-xs leading-snug" style={{ color: WOW.muted }}>
                    {TIERS[t].blurb}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <p className="mt-4 text-xs leading-relaxed" style={{ color: WOW.muted }}>
            Mounds are scaled by <strong>area</strong>, not height — twice the whisk(e)y
            covers twice the ink. Every mound is drawn to true scale, which is why England
            is a speck and Tasmania is almost invisible. That is the honest picture.
            Scotland, Ireland and Canada&apos;s mounds are parked offshore for room and
            tied back to the country with a dotted line.
          </p>
        </section>

        {/* ---------- Stats ---------- */}
        <section className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat
            value={`${BIG_TWO_SHARE}%`}
            label="of the world's maturing whisk(e)y sits in just two places: the United States and Scotland."
          />
          <Stat
            value={`${US_YEARS_OF_SUPPLY} yrs`}
            label={`of American whiskey supply at current demand — 1.5bn proof gallons of stock against 103m sold and exported a year.`}
          />
          <Stat
            value={`${DARK_SHARE}%`}
            label="sits in countries where no national count is published at all. Canada, Japan, India and Taiwan among them."
          />
          <Stat
            value={`${BOTTLE_EQUIVALENT_BN}bn`}
            label="bottles' worth, very roughly — about three for every person alive."
          />
        </section>

        {/* ---------- Why this is hard ---------- */}
        <section className="mt-14">
          <h2
            className="font-[family-name:var(--font-fraunces)] text-2xl font-bold"
            style={{ color: WOW.oak }}
          >
            Four rules we held to
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed" style={{ color: WOW.oakLight }}>
            Most published versions of this number are inflated by the same three mistakes.
            Avoiding them is why our total is lower than some and higher than others.
          </p>
          <ol className="mt-6 space-y-5">
            {[
              {
                h: "Money is not barrels.",
                p: "Diageo reports $7.2bn of maturing whisk(e)y; Brown-Forman reports $1.57bn of barrelled whiskey. Both are audited and neither is a cask count. Balance-sheet values prove the scale of the capital tied up in maturation, and they pin down where the warehouses are — they do not convert into barrels without a documented conversion.",
              },
              {
                h: "Capacity is not inventory.",
                p: "Kavalan's much-repeated 300,000 barrels is how much its warehouses hold, not how much is in them. Capacity is a building. The same goes for cooperage output: a barrel made this year is an input flow, not stock under maturation.",
              },
              {
                h: "A state is not a country.",
                p: "Kentucky's 17.1 million barrels gets quoted as the American figure. It is one state, and it counts all spirits, not just whiskey. That 17.1m is 16.1m barrels of bourbon plus about a million of other spirits, filed with the Kentucky Department of Revenue. Nationally the US holds roughly 25 million barrels, derived separately from about 1.5bn proof gallons of whiskey inventory, with Tennessee, Indiana and a couple of thousand craft distillers alongside Kentucky.",
              },
              {
                h: "Sales are not stock.",
                p: `India is the trap. Eight Indian brands sit in the world's twenty best-selling whiskies, together shifting around 141 million cases a year — McDowell's No. 1 outsells every Scotch on earth. Yet India holds an estimated ${INDIA_SHARE}% of the world's maturing casks. The bulk of an Indian blend is extra neutral alcohol, a near-pure column spirit that never goes into a cask — and the biggest brands have moved from molasses to grain feedstock, which changes what it is distilled from, not whether it is matured. The malt that flavours them is frequently imported from Scotland, already aged and already counted there. Add a tropical angel's share of 8–12% a year and whatever is laid down in India turns over in two or three years rather than twelve. A bottle sold is not a cask resting.`,
              },
            ].map((r) => (
              <li key={r.h} className="flex gap-4">
                <span
                  className="mt-1 h-2 w-2 shrink-0 rounded-full"
                  style={{ background: WOW.amber }}
                />
                <div>
                  <div className="text-sm font-semibold" style={{ color: WOW.oak }}>
                    {r.h}
                  </div>
                  <p className="mt-1 text-sm leading-relaxed" style={{ color: WOW.oakLight }}>
                    {r.p}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* ---------- Country detail ---------- */}
        <section className="mt-14">
          <h2
            className="font-[family-name:var(--font-fraunces)] text-2xl font-bold"
            style={{ color: WOW.oak }}
          >
            Every figure, and how good it is
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed" style={{ color: WOW.oakLight }}>
            Sorted by size. The caveat column is the part we would most like to be
            corrected on.
          </p>

          <div className="mt-6 space-y-3">
            {ranked.map((e) => (
              <article
                key={e.id}
                className="rounded-2xl px-5 py-4"
                style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3 className="text-base font-bold" style={{ color: WOW.oak }}>
                    {e.name}
                  </h3>
                  <div className="flex items-baseline gap-3">
                    {/* A counted figure is not an approximation — the tilde belongs on
                        everything else, not on Scotland's and England's published counts. */}
                    <span className="text-base font-bold" style={{ color: WOW.copper }}>
                      {e.tier === "counted" ? "" : "~"}
                      {fmt(e.central)} casks
                    </span>
                    <span className="text-xs" style={{ color: WOW.muted }}>
                      {fmt(e.low)}–{fmt(e.high)}
                    </span>
                  </div>
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <span
                    className="rounded-full px-2.5 py-0.5 text-[11px] font-semibold"
                    style={{ background: TIERS[e.tier].color, color: WOW.white }}
                  >
                    {TIERS[e.tier].label}
                  </span>
                  <span className="text-[11px]" style={{ color: WOW.muted }}>
                    {e.sourceUrl ? (
                      <a
                        href={e.sourceUrl}
                        target="_blank"
                        rel="noopener"
                        className="underline decoration-dotted underline-offset-2"
                      >
                        {e.source}
                      </a>
                    ) : (
                      e.source
                    )}
                    {" · "}
                    {e.asOf}
                  </span>
                </div>

                <p className="mt-3 text-sm leading-relaxed" style={{ color: WOW.oakLight }}>
                  {e.basis}
                </p>
                <p
                  className="mt-2 border-l-2 pl-3 text-sm leading-relaxed"
                  style={{ borderColor: WOW.parchmentDark, color: WOW.muted }}
                >
                  {e.caveat}
                </p>
              </article>
            ))}
          </div>
        </section>

        {/* ---------- CTA ---------- */}
        <section
          className="mt-14 rounded-2xl px-6 py-8"
          style={{ background: WOW.oak, color: WOW.parchment }}
        >
          <h2 className="font-[family-name:var(--font-fraunces)] text-2xl font-bold">
            Help us fill the gaps
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed" style={{ color: WOW.parchmentDark }}>
            Japan is a model built on one reported warehouse complex. So is Canada beyond
            its four reported sites. So is
            every distillery in Africa outside a single Western Cape site. If you work at a
            distillery and you know your own numbers, we would rather publish your figure
            than our estimate.
          </p>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed" style={{ color: WOW.parchmentDark }}>
            Distillery Map is free and community-built — {total.toLocaleString()} distilleries,
            tasting rooms and producers so far. Claim your listing, correct it, or add one
            that is missing.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              href="/"
              className="rounded-full px-5 py-2.5 text-sm font-semibold"
              style={{ background: WOW.amber, color: WOW.white }}
            >
              Open the map
            </Link>
            <Link
              href="/distilleries"
              className="rounded-full px-5 py-2.5 text-sm font-semibold"
              style={{ border: `1px solid ${WOW.amberGlow}`, color: WOW.amberGlow }}
            >
              Browse by country
            </Link>
          </div>
        </section>

        <p className="mt-10 text-xs leading-relaxed" style={{ color: WOW.muted }}>
          Compiled August 2026 from Scotch Whisky Association Facts &amp; Figures, the
          Kentucky Distillers&apos; Association economic impact reports, DISCUS national
          inventory reporting, the LYQD Irish Whiskey Supply Report 2026, the English
          Whisky Guild, Diageo and Brown-Forman annual reports, and company disclosures
          from Crown Royal and Lark. Units differ between sources — physical casks,
          53-gallon barrels and tax proof gallons are not the same thing, and every
          conversion here is stated rather than hidden. This is a discussion piece, not an
          audited census, and not investment advice.
        </p>
      </main>
    </div>
  );
}
