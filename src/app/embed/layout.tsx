import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Distillery Map — Embed",
  description: "Embeddable interactive distillery map.",
  robots: "noindex, nofollow",
};

export default function EmbedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
