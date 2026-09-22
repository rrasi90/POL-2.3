import Link from "next/link";
import { Button } from "@pol/ui";

export default function LegalPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          قوانین و حریم خصوصی
        </h1>

        <section className="mt-8 space-y-4">
          <h2 className="text-[18px] leading-[28px] font-semibold text-[var(--pol-light-text-primary)]">
            حریم خصوصی
          </h2>
          <p className="text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
            ما فقط داده‌های لازم برای احراز هویت، سفارش و تسویه را پردازش می‌کنیم. شماره موبایل
            برای ورود OTP و اعلان‌های سفارش استفاده می‌شود. داده‌های حساس پرداخت نزد ما ذخیره
            نمی‌شوند.
          </p>
        </section>

        <section className="mt-8 space-y-4">
          <h2 className="text-[18px] leading-[28px] font-semibold text-[var(--pol-light-text-primary)]">
            اعتماد و امنیت
          </h2>
          <ul className="list-disc space-y-2 ps-5 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
            <li>احراز هویت با OTP چهاررقمی و توکن کوتاه‌مدت (D-018)</li>
            <li>نقش‌محور: خرده‌فروش، تأمین‌کننده، عملیات، میدانی و ادمین</li>
            <li>لاگ ممیزی رویدادهای حساس برای شفافیت</li>
          </ul>
        </section>

        <section className="mt-8 space-y-4">
          <h2 className="text-[18px] leading-[28px] font-semibold text-[var(--pol-light-text-primary)]">
            شرایط تسویه
          </h2>
          <p className="text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
            پرداخت و تسویه طبق شرایط ثبت‌شده سفارش و طرفین معامله انجام می‌شود. (D-025)
          </p>
        </section>

        <div className="mt-10 flex flex-wrap gap-3">
          <Link href="/">
            <Button variant="secondary">بازگشت به خانه</Button>
          </Link>
          <Link href="/about">
            <Button variant="ghost">درباره ما</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
