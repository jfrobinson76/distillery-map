import type { Metadata } from "next";
import Script from "next/script";
import { Geist } from "next/font/google";
import { Fraunces } from "next/font/google";
import "./globals.css";

const GA_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://distillerymap.org"),
  title: {
    default: "Distillery Map by Stillbound — Every Distillery in the World",
    template: "%s — Distillery Map by Stillbound",
  },
  description:
    "A free, open map of distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.",
  openGraph: {
    title: "Distillery Map by Stillbound — Every Distillery in the World",
    description:
      "A free, open map of distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.",
    url: "https://distillerymap.org",
    siteName: "Distillery Map by Stillbound",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Distillery Map by Stillbound — Every Distillery in the World",
    description:
      "A free, open map of distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${fraunces.variable} h-full antialiased`}
    >
      <body className="h-full">
        {GA_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
              strategy="afterInteractive"
            />
            {/* Consent Mode v2, default denied — GA runs cookieless, no banner needed (EU) */}
            <Script id="ga4-init" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('consent', 'default', {
                  ad_storage: 'denied',
                  ad_user_data: 'denied',
                  ad_personalization: 'denied',
                  analytics_storage: 'denied'
                });
                gtag('js', new Date());
                gtag('config', '${GA_ID}');
              `}
            </Script>
          </>
        )}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:rounded-lg focus:bg-amber focus:px-4 focus:py-2 focus:text-sm focus:text-white"
        >
          Skip to main content
        </a>
        <main id="main-content" className="h-full">{children}</main>
      </body>
    </html>
  );
}
