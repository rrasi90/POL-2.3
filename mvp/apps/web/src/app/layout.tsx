import type { Metadata } from "next";
import { Vazirmatn } from "next/font/google";
import { SessionCookieSync } from "@/lib/auth/session-cookie-sync";
import "./globals.css";

const vazirmatn = Vazirmatn({
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-vazirmatn",
  display: "swap",
});

export const metadata: Metadata = {
  title: "پُــــل | بازار و خرید عمده",
  description:
    "پُــــل؛ بازار و ابزار خرید و فروش عمده برای فروشگاه‌ها و بنکدارها، از پیدا کردن کالا تا سفارش و پیگیری تحویل.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <body className={`${vazirmatn.variable} font-sans antialiased`}>
        <SessionCookieSync />
        {children}
      </body>
    </html>
  );
}
