import Link from "next/link";
import { Button } from "@pol/ui";

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          درباره POL
        </h1>
        <p className="mt-4 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          POL پلتفرم سفارش‌گذاری عمده‌فروشی B2B برای بنکداران، تأمین‌کنندگان و خرده‌فروشان
          است — با تمرکز بر دقت قیمت، شفافیت تسویه و پایلوت اهواز.
        </p>

        <section className="mt-8 space-y-4">
          <h2 className="text-[18px] leading-[28px] font-semibold text-[var(--pol-light-text-primary)]">
            چه چیزی ارائه می‌دهیم
          </h2>
          <ul className="list-disc space-y-2 ps-5 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
            <li>سبد و تسویه چندفروشنده‌ای با شفافیت تخصیص</li>
            <li>کاتالوگ و مقایسه قیمت/موجودی تأمین‌کنندگان</li>
            <li>ردیابی سفارش، استثناها و میز پشتیبانی یکپارچه</li>
            <li>بدون Driver App — تحویل با لینک (D-023)</li>
          </ul>
        </section>

        <section className="mt-8 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
            این صفحه محتوای ایستای بازاریابی است (C-06) — بدون API.
          </p>
        </section>

        <div className="mt-10 flex flex-wrap gap-3">
          <Link href="/">
            <Button variant="secondary">بازگشت به خانه</Button>
          </Link>
          <Link href="/contact">
            <Button variant="ghost">تماس با ما</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
