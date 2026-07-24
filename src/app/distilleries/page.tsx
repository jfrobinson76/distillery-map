import type { Metadata } from "next";
import Link from "next/link";
import { getCountries, getDistilleryCount } from "@/lib/data";
import { WOW } from "@/lib/constants";

export const metadata: Metadata = {
  title: "Distilleries by Country",
  description:
    "Browse the world's distilleries by country — every distillery, tasting room, and spirit producer on the free, community-built Distillery Map.",
  alternates: { canonical: "/distilleries" },
};

export default async function DistilleriesHub() {
  const [countries, total] = await Promise.all([getCountries(), getDistilleryCount()]);

  return (
    <div className="min-h-dvh" style={{ background: WOW.parchment }}>
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
        <h1
          className="text-3xl font-bold font-[family-name:var(--font-fraunces)]"
          style={{ color: WOW.oak }}
        >
          Distilleries by country
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed" style={{ color: WOW.muted }}>
          {total.toLocaleString()} distilleries, tasting rooms, and spirit producers,
          mapped by the community. Pick a country to see every producer we know
          about there — or explore them all on the{" "}
          <Link href="/" className="underline" style={{ color: WOW.amber }}>
            interactive map
          </Link>
          .
        </p>

        <ul className="mt-8 grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
          {countries.map((c) => (
            <li key={c.slug}>
              <Link
                href={`/distilleries/${c.slug}`}
                className="flex items-baseline justify-between rounded-xl px-4 py-3 text-sm transition-colors"
                style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}`, color: WOW.oak }}
              >
                <span className="font-medium">{c.name}</span>
                <span className="text-xs" style={{ color: WOW.muted }}>
                  {c.count.toLocaleString()}
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <p className="mt-8 text-xs" style={{ color: WOW.muted }}>
          Missing somewhere? The map is community-built —{" "}
          <Link href="/" className="underline" style={{ color: WOW.amber }}>
            add a distillery
          </Link>{" "}
          and we&apos;ll review it.
        </p>
      </main>
    </div>
  );
}
