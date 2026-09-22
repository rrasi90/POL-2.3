import Link from "next/link";
import { Button } from "@pol/ui";

/** C-02 Retailers corporate landing — static, PUBLIC_ANON (G-006). */
export default function CorporateRetailersPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          برای خرده‌فروشان
        </h1>
        <p className="mt-4 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          سبد چندفروشنده‌ای، مقایسه قیمت و موجودی تأمین‌کنندگان، ردیابی سفارش و تسویه شفاف —
          بدون کیف پول و بدون Driver App.
        </p>
        <ul className="mt-6 list-disc space-y-2 ps-5 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          <li>تخصیص خودکار سبد به فروشندگان (D-014)</li>
          <li>پذیرش جزئی سفارش توسط تأمین‌کننده</li>
          <li>ورود سریع با OTP چهاررقمی</li>
          <li>پایلوت اهواز — تک‌شهر (D-001)</li>
        </ul>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/auth/login">
            <Button>شروع ورود</Button>
          </Link>
          <Link href="/how">
            <Button variant="secondary">نحوه کار POL</Button>
          </Link>
        </div>
        <nav aria-label="ناوبری شرکتی" className="mt-10 flex flex-wrap gap-4 text-[13px]">
          <Link href="/" className="text-[var(--pol-light-brand-primary)] hover:underline">
            خانه
          </Link>
          <Link href="/vendors" className="text-[var(--pol-light-brand-primary)] hover:underline">
            تأمین‌کنندگان
          </Link>
          <Link href="/about" className="text-[var(--pol-light-brand-primary)] hover:underline">
            درباره
          </Link>
          <Link href="/contact" className="text-[var(--pol-light-brand-primary)] hover:underline">
            تماس
          </Link>
        </nav>
      </div>
    </main>
  );
}
