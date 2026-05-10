import "./spiceroute.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Restaurant recommendation hub",
  description: "SpiceRoute Select — Phase 6 recommendations (Next.js + Railway API)",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
