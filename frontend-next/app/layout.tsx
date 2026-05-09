import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Restaurant recommendations",
  description: "Next.js frontend for Phase 6 backend APIs",
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
