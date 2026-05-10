import "./spiceroute.css";
import type { Metadata } from "next";
import { DM_Sans } from "next/font/google";

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm",
});

export const metadata: Metadata = {
  title: "Restaurant recommendation hub",
  description:
    "Discover dining picks with AI — Zomato-inspired UI (educational demo; not affiliated with Zomato).",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={dmSans.variable}>
      <body className={dmSans.className}>{children}</body>
    </html>
  );
}
