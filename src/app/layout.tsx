import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Fraunces } from "next/font/google";
import "./globals.css";

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
  metadataBase: new URL("https://distillerymap.ie"),
  title: "Distillery Map — Every Distillery in the World",
  description:
    "A free, open distillery map with 6,497 distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.",
  openGraph: {
    title: "Distillery Map — Every Distillery in the World",
    description:
      "A free, open distillery map with 6,497 distilleries, tasting rooms, and spirit producers worldwide. Community-built and growing.",
    url: "https://distillerymap.ie",
    siteName: "Distillery Map",
    locale: "en_IE",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Distillery Map — Every Distillery in the World",
    description:
      "A free, open distillery map with 6,497 distilleries, tasting rooms, and spirit producers worldwide.",
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
