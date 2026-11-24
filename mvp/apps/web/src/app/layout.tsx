import type { Metadata } from "next";
import localFont from "next/font/local";
import { SessionCookieSync } from "@/lib/auth/session-cookie-sync";
import "./globals.css";

// Keep the Persian UI font inside the repository so production builds do not
// depend on reaching Google Fonts from CI, staging or private deployments.
const vazirmatn = localFont({
  src: [
    { path: "../../public/fonts/Vazirmatn-Regular.ttf", weight: "400", style: "normal" },
    { path: "../../public/fonts/Vazirmatn-SemiBold.ttf", weight: "600", style: "normal" },
    { path: "../../public/fonts/Vazirmatn-Bold.ttf", weight: "700", style: "normal" },
  ],
  variable: "--font-vazirmatn",
  display: "swap",
});

export const metadata: Metadata = {
  title: "POL — بازار عمده‌فروشی",
  description: "پلتفرم B2B FMCG — MVP",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
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
