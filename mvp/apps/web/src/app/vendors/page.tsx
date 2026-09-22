import Link from "next/link";
import { Button } from "@pol/ui";

/** C-03 Vendors corporate landing — static, PUBLIC_ANON (G-006). */
export default function CorporateVendorsPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          برای تأمین‌کنندگان
        </h1>
        <p className="mt-4 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          صف سفارش‌ها، پذیرش/رد/پذیرش جزئی، مدیریت قیمت و موجودی روزانه، ویترین خواندنی و
          تسویه شفاف.
        </p>
        <ul className="mt-6 list-disc space-y-2 ps-5 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          <li>داشبورد صف‌محور بدون شلوغی بصری</li>
          <li>تأیید روزانه موجودی</li>
          <li>ارجاع فقط نسبت‌دهی — بدون پاداش MVP (D-016)</li>
          <li>بدون کیف پول (D-021) و بدون اسکرو (D-025)</li>
        </ul>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/auth/login">
            <Button>شروع ورود</Button>
          </Link>
          <Link href="/retailers">
            <Button variant="secondary">برای خرده‌فروشان</Button>
          </Link>
        </div>
        <nav aria-label="ناوبری شرکتی" className="mt-10 flex flex-wrap gap-4 text-[13px]">
          <Link href="/" className="text-[var(--pol-light-brand-primary)] hover:underline">
            خانه
          </Link>
          <Link href="/about" className="text-[var(--pol-light-brand-primary)] hover:underline">
            درباره
          </Link>
          <Link href="/pilot" className="text-[var(--pol-light-brand-primary)] hover:underline">
            پایلوت اهواز
          </Link>
          <Link href="/contact" className="text-[var(--pol-light-brand-primary)] hover:underline">
            تماس
          </Link>
        </nav>
      </div>
    </main>
  );
}
