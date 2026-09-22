import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "POL",
  description: "POL B2B FMCG — MVP",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
