import Link from "next/link";
import { Button } from "@pol/ui";

/** C-03 Vendors corporate landing — static, PUBLIC_ANON (G-006). */
export default function CorporateVendorsPage() {
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
            PRECISION COMMERCE · ویژه بنکداران و شرکت‌های تأمین‌کننده
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            مدیریت هوشمند فروش عمده، صف سفارشات و تسویه مستقیم
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            پلتفرم پُل بستری کارآمد برای شرکت‌های پخش، بنکداران و نمایندگی‌های برندهای FMCG است تا سفارشات سوپرمارکت‌های اهواز را در یک داشبورد عملیاتی منظم مدیریت و ارسال کنند.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <div className="text-[20px]">📋</div>
              <h2 className="mt-2 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                داشبورد صف‌محور عملیاتی
              </h2>
              <p className="mt-1 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                مشاهده آنی سفارش‌های دریافتی با سن سفارش و امکان اقدام سریع برای پذیرش کامل، رد یا پیشنهاد مقادیر جایگزین.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <div className="text-[20px]">🌅</div>
              <h2 className="mt-2 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                آیین صبحگاهی تأیید موجودی
              </h2>
              <p className="mt-1 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                تأیید سریع موجودی روزانه انبار در آغاز روز کاری جهت حفظ رتبه خوش‌قولی و پیشگیری از لغو سفارش‌های خریداران.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <div className="text-[20px]">💰</div>
              <h2 className="mt-2 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                بدون بلوکه شدن وجه و کارمزد پنهان
              </h2>
              <p className="mt-1 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پول شما در کیف پول مجازی مسدود نمی‌شود؛ فاکتورها مستقیماً طبق عرف بازار و روال تجاری خودتان با خریدار تسویه می‌گردد.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <div className="text-[20px]">🚚</div>
              <h2 className="mt-2 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                ارسال و تحویل بدون اپلیکیشن راننده
              </h2>
              <p className="mt-1 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                حواله ارسال با یک پیامک حاوی لینک امن به متصدی تحویل سپرده شده و پس از تحویل، امضا و تأیید بار در سیستم ثبت می‌شود.
              </p>
            </div>
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/auth/login">
              <Button size="lg">ورود به پنل تأمین‌کنندگان</Button>
            </Link>
            <Link href="/retailers">
              <Button variant="secondary" size="lg">مشاهده امکانات خرده‌فروشان</Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-6">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4 px-6 text-[12px] text-[var(--pol-light-text-muted)]">
          <span>POL — ویژه بنکداران و تأمین‌کنندگان</span>
          <nav aria-label="پیوندهای کمکی" className="flex gap-4">
            <Link href="/" className="hover:underline">خانه</Link>
            <Link href="/retailers" className="hover:underline">خرده‌فروشان</Link>
            <Link href="/pilot" className="hover:underline">پایلوت اهواز</Link>
            <Link href="/contact" className="hover:underline">تماس</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
