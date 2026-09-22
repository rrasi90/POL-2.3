import Link from "next/link";
import { Button } from "@pol/ui";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          POL — بازار عمده‌فروشی B2B
        </h1>
        <p className="mt-3 max-w-xl text-[14px] leading-[22px] text-[var(--pol-light-text-secondary)]">
          پلتفرم سفارش‌گذاری چندفروشنده‌ای برای بنکداران و تأمین‌کنندگان — پایلوت اهواز.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/auth/login">
            <Button size="lg">ورود با شماره موبایل</Button>
          </Link>
          <Link href="/retailer">
            <Button variant="secondary" size="lg">
              ورود به بازار
            </Button>
          </Link>
          <Link href="/vendor">
            <Button variant="ghost" size="lg">
              پنل تأمین‌کننده
            </Button>
          </Link>
        </div>
        <div className="mt-12 grid gap-3 text-[13px] text-[var(--pol-light-text-muted)] sm:grid-cols-3">
          <span>سبد چندفروشنده‌ای (D-014)</span>
          <span>OTP چهاررقمی (D-018)</span>
          <span>بدون Driver App — تحویل با لینک (D-023)</span>
        </div>
        <nav aria-label="پیوندهای شرکتی" className="mt-8 flex flex-wrap gap-4 text-[13px]">
          <Link href="/about" className="text-[var(--pol-light-brand-primary)] hover:underline">
            درباره ما
          </Link>
          <Link href="/contact" className="text-[var(--pol-light-brand-primary)] hover:underline">
            تماس
          </Link>
          <Link href="/legal" className="text-[var(--pol-light-brand-primary)] hover:underline">
            قوانین
          </Link>
        </nav>
      </div>
    </main>
  );
}
