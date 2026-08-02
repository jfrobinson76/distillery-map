import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getCountries,
  getCountryBySlug,
  countryDisplayName,
} from "@/lib/data";
import { SITE_URL, WOW } from "@/lib/constants";
import { countryCopy } from "@/lib/country-copy";
import { CountryMapPreview } from "@/components/CountryMapPreview";

type Props = { params: Promise<{ country: string }> };

export async function generateStaticParams() {
  const countries = await getCountries();
  return countries.map((c) => ({ country: c.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { country } = await params;
  const result = await getCountryBySlug(country);
  if (!result) return {};
  const { entry } = result;
  const inName = countryDisplayName(entry.name);
  return {
    title: `Distilleries in ${entry.name}`,
    description: `All ${entry.count.toLocaleString("en-US")} distilleries, tasting rooms, and spirit producers in ${inName} — names, locations, and websites on the free, community-built Distillery Map.`,
    alternates: { canonical: `/distilleries/${entry.slug}` },
  };
}

export default async function CountryPage({ params }: Props) {
  const { country } = await params;
  const result = await getCountryBySlug(country);
  if (!result) notFound();
  const { entry, features } = result;
  const inName = countryDisplayName(entry.name);
  const countries = await getCountries();
  const others = countries.filter((c) => c.slug !== entry.slug).slice(0, 12);

  const embedSrc =
    entry.kind === "region"
      ? `/embed?region=scotland`
      : `/embed?country=${encodeURIComponent(entry.name)}`;

  const faqs = [
    {
      q: `How many distilleries are there in ${inName}?`,
      a: `There are ${entry.count.toLocaleString("en-US")} distilleries, tasting rooms, and spirit producers in ${inName} on the Distillery Map. The map is community-built and growing, so the number keeps rising.`,
    },
    {
      q: `What counts as a distillery on this map?`,
      a: `The map includes working distilleries, tasting rooms, and other spirit producers — whiskey, gin, rum, brandy, and more — compiled from OpenStreetMap, Wikidata, and community submissions.`,
    },
    {
      q: `I run a distillery in ${inName} — how do I update my listing?`,
      a: `Open the interactive map, find your pin, and choose "Is this your distillery? Claim it." Claiming is free and lets you correct your details and add visitor information like tours and bookings.`,
    },
  ];

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Distillery Map", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Distilleries by country", item: `${SITE_URL}/distilleries` },
          { "@type": "ListItem", position: 3, name: `Distilleries in ${entry.name}`, item: `${SITE_URL}/distilleries/${entry.slug}` },
        ],
      },
      {
        "@type": "ItemList",
        name: `Distilleries in ${entry.name}`,
        numberOfItems: entry.count,
        itemListElement: features.slice(0, 50).map((f, i) => ({
          "@type": "ListItem",
          position: i + 1,
          name: f.properties.name,
        })),
      },
      {
        "@type": "FAQPage",
        mainEntity: faqs.map((f) => ({
          "@type": "Question",
          name: f.q,
          acceptedAnswer: { "@type": "Answer", text: f.a },
        })),
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
        <nav className="text-xs" style={{ color: WOW.muted }}>
          <Link href="/" className="underline">Home</Link>
          {" · "}
          <Link href="/distilleries" className="underline">Distilleries by country</Link>
          {" · "}
          <span>{entry.name}</span>
        </nav>

        <h1
          className="mt-4 text-3xl font-bold font-[family-name:var(--font-fraunces)]"
          style={{ color: WOW.oak }}
        >
          Distilleries in {entry.name}
        </h1>
        <p className="mt-3 text-sm leading-relaxed" style={{ color: WOW.muted }}>
          There are{" "}
          <strong style={{ color: WOW.amber }}>{entry.count.toLocaleString()}</strong>{" "}
          distilleries, tasting rooms, and spirit producers in {inName} on the
          Distillery Map.{" "}
          {countryCopy[entry.slug] ??
            "From household names to one-room craft operations, community-built, free, and growing."}
        </p>

        <CountryMapPreview src={embedSrc} countryName={entry.name} />

        <section className="mt-10">
          <h2
            className="text-xl font-bold font-[family-name:var(--font-fraunces)]"
            style={{ color: WOW.oak }}
          >
            All {entry.count.toLocaleString()} listings
          </h2>
          <ul className="mt-4 grid gap-2 sm:grid-cols-2">
            {features.map((f) => (
              <li
                key={f.properties.slug}
                className="rounded-xl px-4 py-3"
                style={{ background: WOW.white, border: `1px solid ${WOW.parchmentDark}` }}
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-sm font-medium" style={{ color: WOW.oak }}>
                    {f.properties.name}
                    {f.properties.claimed && (
                      <span
                        className="ml-1.5 text-[10px] font-semibold"
                        style={{ color: WOW.amber }}
                        title="Verified by the distillery"
                      >
                        &#10003; Verified
                      </span>
                    )}
                  </span>
                  {f.properties.website && (
                    <a
                      href={f.properties.website}
                      target="_blank"
                      rel="nofollow noopener"
                      className="shrink-0 text-xs underline"
                      style={{ color: WOW.amber }}
                    >
                      Website
                    </a>
                  )}
                </div>
                {(f.properties.address || f.properties.description) && (
                  <p className="mt-1 text-xs" style={{ color: WOW.muted }}>
                    {f.properties.address || f.properties.description}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section
          className="mt-10 rounded-2xl p-6"
          style={{ background: WOW.parchmentDark }}
        >
          <h2
            className="text-lg font-bold font-[family-name:var(--font-fraunces)]"
            style={{ color: WOW.oak }}
          >
            Claim your Verified badge
          </h2>
          <p className="mt-2 text-sm" style={{ color: WOW.charcoal }}>
            The first 50 distilleries to claim their listing get the{" "}
            &#10003; Verified badge and an enhanced profile, free. Open the{" "}
            <Link href="/" className="underline" style={{ color: WOW.amber }}>
              interactive map
            </Link>
            , find your pin, and choose &ldquo;Claim it&rdquo; to correct your
            details and add tours, tastings, and booking links. Not listed yet?
            Use the map&apos;s Contribute button and we&apos;ll add you.
          </p>
        </section>

        <section className="mt-10">
          <h2
            className="text-lg font-bold font-[family-name:var(--font-fraunces)]"
            style={{ color: WOW.oak }}
          >
            Frequently asked questions
          </h2>
          <dl className="mt-3 space-y-4">
            {faqs.map((f) => (
              <div key={f.q}>
                <dt className="text-sm font-semibold" style={{ color: WOW.charcoal }}>
                  {f.q}
                </dt>
                <dd className="mt-1 text-sm" style={{ color: WOW.muted }}>
                  {f.a}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="mt-10">
          <h2 className="text-sm font-semibold" style={{ color: WOW.charcoal }}>
            Browse other countries
          </h2>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: WOW.muted }}>
            {others.map((c, i) => (
              <span key={c.slug}>
                {i > 0 && " · "}
                <Link
                  href={`/distilleries/${c.slug}`}
                  className="underline"
                  style={{ color: WOW.amber }}
                >
                  {c.name}
                </Link>
              </span>
            ))}
            {" · "}
            <Link href="/distilleries" className="underline" style={{ color: WOW.amber }}>
              all countries
            </Link>
          </p>
        </section>
      </main>
    </div>
  );
}
