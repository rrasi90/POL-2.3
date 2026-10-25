import Link from "next/link";
import { Button } from "@pol/ui";

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--pol-light-bg-canvas)] text-[var(--pol-light-text-primary)]">
      {/* Header */}
      <header className="border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-4xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-lg bg-[var(--pol-light-brand-primary)] text-[16px] font-black text-white">
              پُ
            </span>
            <span className="font-bold text-[18px]">پُــــل</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/auth/login">
              <Button size="sm">ورود به سامانه</Button>
            </Link>
          </div>
        </div>
      </header>

      <nav
        aria-label="پیوندهای اصلی موبایل"
        className="flex md:hidden flex-wrap items-center justify-center gap-x-4 gap-y-1 border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-4 py-3 text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
      >
        <Link href="/" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">خانه</Link>
        <Link href="/about" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">درباره ما</Link>
        <Link href="/how" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">نحوه کار</Link>
        <Link href="/retailers" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">خرده‌فروشان</Link>
        <Link href="/vendors" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">بنکداران</Link>
        <Link href="/pilot" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">پایلوت اهواز</Link>
        <Link href="/contact" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">تماس</Link>
      </nav>

      <main className="flex-1 py-12 md:py-16">
        <div className="mx-auto max-w-4xl px-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--pol-light-brand-primary)]/20 bg-[var(--pol-light-brand-primary)]/10 px-3 py-0.5 text-[11px] font-semibold text-[var(--pol-light-brand-primary)]">
            PRECISION COMMERCE · درباره پلتفرم
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            درباره پلتفرم معاملات عمده POL
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            POL (پُــــل) زیرساخت دیجیتال سفارش‌گذاری عمده‌فروشی B2B برای بنکداران، شرکت‌های پخش، تأمین‌کنندگان و خرده‌فروشان مواد غذایی (FMCG) است. تمرکز اصلی POL بر حذف خطاهای ثبت سفارش، شفاف‌سازی قیمت‌ها و تسریع فرآیند تدارکات کالا در پایلوت استان خوزستان (شهر اهواز) بنا شده است.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                سبد و تسویه چندفروشنده‌ای
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                خرده‌فروش می‌تواند در یک سبد خرید از چندین بنکدار و شرکت تأمین‌کننده خرید کند. سیستم سفارشات را خودکار تفکیک و به هر فروشنده ابلاغ می‌کند.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                کاتالوگ استاندارد و مقایسه قیمت
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                کدهای کانونیکال کالا، مقایسه زنده قیمت و حداقل سفارش (MOQ) و مشاهده اعتبار تأمین‌کنندگان مختلف با شفافیت کامل.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                تحویل چابک بدون اپلیکیشن راننده
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                رانندگان و متصدیان حمل نیازی به نصب اپ مجزا ندارند؛ ثبت تحویل و بارگذاری عکس حواله با لینک رمزنگاری‌شده اختصاصی صورت می‌گیرد.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                میز عملیات و پشتیبانی یکپارچه
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                ثبت استثناها، اختلافات فاکتور و درخواست‌های مرجوعی در صف‌های خودکار بدون نیاز به چت‌ها یا تماس‌های تلفنی پراکنده.
              </p>
            </div>
          </div>

          <div className="mt-8 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[12px] leading-[20px] text-[var(--pol-light-text-secondary)]">
            <span className="font-semibold text-[var(--pol-light-text-primary)]">یادداشت فنی پایلوت (C-06): </span>
            این برگه اطلاعات سازمانی ایستا بوده و بدون فراخوانی مستقیم API بارگذاری می‌شود.
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/how">
              <Button size="md">مشاهده نحوه کارکرد سامانه</Button>
            </Link>
            <Link href="/contact">
              <Button variant="secondary" size="md">تماس با تیم توسعه</Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-6">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4 px-6 text-[12px] text-[var(--pol-light-text-muted)]">
          <span>POL — Precision Commerce B2B</span>
          <nav aria-label="پیوندهای کمکی" className="flex gap-4">
            <Link href="/" className="hover:underline">خانه</Link>
            <Link href="/how" className="hover:underline">نحوه کار</Link>
            <Link href="/pilot" className="hover:underline">پایلوت اهواز</Link>
            <Link href="/contact" className="hover:underline">تماس</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
