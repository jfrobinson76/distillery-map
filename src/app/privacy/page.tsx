import type { Metadata } from "next";
import Link from "next/link";
import { WOW } from "@/lib/constants";

export const metadata: Metadata = {
  title: "Privacy Notice",
  description: "How Distillery Map by Stillbound handles personal information.",
  alternates: { canonical: "/privacy" },
  robots: { index: false, follow: true },
};

const sectionClass = "mt-8 border-t pt-6";

export default function PrivacyPage() {
  return (
    <div className="min-h-dvh" style={{ background: WOW.parchment }}>
      <header
        className="px-4 py-3 sm:px-6"
        style={{ background: WOW.oak, borderBottom: `1px solid ${WOW.oakLight}` }}
      >
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <Link
            href="/"
            className="text-xl font-bold font-[family-name:var(--font-fraunces)]"
            style={{ color: WOW.amberGlow }}
          >
            Distillery Map{" "}
            <span className="text-sm font-normal" style={{ color: WOW.parchmentDark }}>
              by Stillbound
            </span>
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

      <main className="mx-auto max-w-3xl px-4 py-10 text-sm leading-relaxed sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em]" style={{ color: WOW.amber }}>
          Privacy notice
        </p>
        <h1
          className="mt-2 text-3xl font-bold font-[family-name:var(--font-fraunces)]"
          style={{ color: WOW.oak }}
        >
          Your information on Distillery Map
        </h1>
        <p className="mt-3" style={{ color: WOW.muted }}>Last updated: 29 August 2026</p>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            Who is responsible
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            Distillery Map is operated by John Robinson, trading as Stillbound in Ireland.
            Stillbound is the data controller for personal information handled through this
            site. Contact{" "}
            <a className="underline" style={{ color: WOW.amber }} href="mailto:hello@stillbound.ai">
              hello@stillbound.ai
            </a>{" "}
            with any privacy question or request.
          </p>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            What we collect and why
          </h2>
          <ul className="mt-3 list-disc space-y-3 pl-5" style={{ color: WOW.charcoal }}>
            <li>
              <strong>Contributions and corrections:</strong> listing details and, if you
              provide it, your email address. We use this to review the submission, check
              accuracy, publish appropriate listing information, and follow up about that
              submission.
            </li>
            <li>
              <strong>Listing claims:</strong> your name, work email, role, distillery and
              proposed listing updates. We use this only to verify your connection to the
              distillery and manage its listing.
            </li>
            <li>
              <strong>One-time accuracy requests:</strong>{" "}we may use a business contact
              address published on a distillery&apos;s own website, together with the source URL,
              to ask the business to check its public listing. The message identifies the
              source and offers an immediate way to object. We do not use this process for sales.
            </li>
            <li>
              <strong>Technical information:</strong> hosting and map providers receive
              limited request information such as IP address, browser type and timestamps to
              deliver and secure the site and map tiles.
            </li>
          </ul>
          <p className="mt-4" style={{ color: WOW.charcoal }}>
            The legal bases are our legitimate interests in maintaining an accurate, secure
            public directory and responding to requests you make through the forms. We assess
            those interests against your rights and collect only what is needed for those
            purposes.
          </p>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            What is public — and what is not
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            Approved distillery information may be published on the map. Your contact name,
            email address and role are not published in the dataset. Claim and submission
            contact details are not added to marketing lists, sold, or shared with third
            parties for their own commercial purposes.
          </p>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            Service providers and international transfers
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            We use Formspree to receive forms, Google Workspace/Gmail to manage correspondence,
            Vercel to host the site, and Mapbox to display the map. These providers process only
            the information needed to provide their services. Some processing may take place
            outside the European Economic Area; provider data-processing terms and Standard
            Contractual Clauses are used where required for those transfers.
          </p>
          <ul className="mt-3 list-disc space-y-1 pl-5" style={{ color: WOW.charcoal }}>
            <li><a className="underline" style={{ color: WOW.amber }} href="https://formspree.io/legal/privacy-policy/" target="_blank" rel="noopener noreferrer">Formspree privacy</a></li>
            <li><a className="underline" style={{ color: WOW.amber }} href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google privacy</a></li>
            <li><a className="underline" style={{ color: WOW.amber }} href="https://vercel.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer">Vercel privacy</a></li>
            <li><a className="underline" style={{ color: WOW.amber }} href="https://www.mapbox.com/legal/privacy" target="_blank" rel="noopener noreferrer">Mapbox privacy</a></li>
          </ul>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            Analytics and cookies
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            We do not run advertising, behavioural analytics, tracking pixels or marketing
            cookies on Distillery Map. The services needed to host and display the interactive
            map may use limited technical storage or request data to operate and protect their
            services.
          </p>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            How long we keep personal information
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5" style={{ color: WOW.charcoal }}>
            <li>Submission contact details are deleted within 12 months after the submission is resolved.</li>
            <li>Verified-claim contact details are reviewed annually and deleted within 24 months of the last listing-management contact unless an active request still requires them.</li>
            <li>Publicly sourced outreach contact details are deleted within 90 days if there is no response.</li>
            <li>If you object, we keep only the minimum suppression record needed to ensure we do not contact you again.</li>
          </ul>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            Your rights
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            Depending on the circumstances, you can ask to access, correct, erase, restrict or
            receive your personal information, and you can object to processing based on
            legitimate interests. Email{" "}
            <a className="underline" style={{ color: WOW.amber }} href="mailto:hello@stillbound.ai">
              hello@stillbound.ai
            </a>
            . You can also complain to Ireland&apos;s{" "}
            <a className="underline" style={{ color: WOW.amber }} href="https://www.dataprotection.ie" target="_blank" rel="noopener noreferrer">
              Data Protection Commission
            </a>
            .
          </p>
        </section>

        <section className={sectionClass} style={{ borderColor: WOW.parchmentDark }}>
          <h2 className="text-xl font-bold font-[family-name:var(--font-fraunces)]" style={{ color: WOW.oak }}>
            Changes
          </h2>
          <p className="mt-3" style={{ color: WOW.charcoal }}>
            We will update this notice before using personal information for a materially new
            purpose. We will not turn listing-management information into marketing or
            unrelated commercial data without a separate, clear permission and updated notice.
          </p>
        </section>
      </main>
    </div>
  );
}
