import Link from "next/link";
import { Button } from "@pol/ui";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--pol-light-bg-canvas)] text-[var(--pol-light-text-primary)]">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              <span className="flex size-9 items-center justify-center rounded-xl bg-[var(--pol-light-brand-primary)] text-[18px] font-black text-white shadow-sm">
                پُ
              </span>
              <span className="font-black text-[20px] tracking-tight text-[var(--pol-light-text-primary)]">
                پُــــل
              </span>
            </Link>

            <nav aria-label="پیوندهای اصلی" className="hidden md:flex items-center gap-5 text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
              <Link href="/about" className="hover:text-[var(--pol-light-brand-primary)]">
                درباره ما
              </Link>
              <Link href="/how" className="hover:text-[var(--pol-light-brand-primary)]">
                چگونه کار می‌کند
              </Link>
              <Link href="/retailers" className="hover:text-[var(--pol-light-brand-primary)]">
                برای خرده‌فروشان
              </Link>
              <Link href="/vendors" className="hover:text-[var(--pol-light-brand-primary)]">
                برای تأمین‌کنندگان
              </Link>
              <Link href="/pilot" className="hover:text-[var(--pol-light-brand-primary)]">
                پایلوت اهواز
              </Link>
            </nav>
          </div>

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
        <Link href="/about" className="shrink-0 hover:text-[var(--pol-light-brand-primary)]">درباره ما</Link>
        <Link href="/how" className="shrink-0 hover:text-[var(--pol-light-brand-primary)]">نحوه کار</Link>
        <Link href="/retailers" className="shrink-0 hover:text-[var(--pol-light-brand-primary)]">برای خرده‌فروشان</Link>
        <Link href="/vendors" className="shrink-0 hover:text-[var(--pol-light-brand-primary)]">برای تأمین‌کنندگان</Link>
        <Link href="/pilot" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">پایلوت اهواز</Link>
        <Link href="/contact" className="shrink-0 py-1 hover:text-[var(--pol-light-brand-primary)]">تماس با ما</Link>
      </nav>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="mx-auto max-w-5xl px-6 py-20 text-center md:py-28">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--pol-light-brand-primary)]/20 bg-[var(--pol-light-brand-primary)]/10 px-3.5 py-1 text-[12px] font-semibold text-[var(--pol-light-brand-primary)]">
            <span>PRECISION COMMERCE</span>
            <span>·</span>
            <span>پایلوت فعال اهواز</span>
          </div>

          <h1 className="mt-6 text-[36px] font-black leading-[48px] tracking-tight text-[var(--pol-light-text-primary)] sm:text-[46px] sm:leading-[58px]">
            زیرساخت مدرن سفارش‌گذاری و زنجیره تأمین بنکداری B2B
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            پلتفرم سفارش‌گذاری چندفروشنده‌ای برای بنکداران، تأمین‌کنندگان و سوپرمارکت‌ها با تمرکز بر اصالت داده، سرعت سفارش‌گذاری و شفافیت تسویه.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link href="/auth/login">
              <Button size="lg" className="px-6 text-[15px]">
                ورود با شماره موبایل
              </Button>
            </Link>
            <Link href="/retailer">
              <Button variant="secondary" size="lg" className="px-6 text-[15px]">
                ورود به بازار خرده‌فروشی
              </Button>
            </Link>
            <Link href="/vendor">
              <Button variant="ghost" size="lg" className="px-5 text-[15px]">
                پنل تأمین‌کنندگان
              </Button>
            </Link>
          </div>

          {/* Feature Highlights Grid */}
          <div className="mt-16 grid gap-6 text-start sm:grid-cols-3">
            <div className="rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[18px]">
                🛒
              </div>
              <h2 className="mt-4 text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                سبد چندفروشنده‌ای
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                سفارش‌گذاری همزمان از چند تأمین‌کننده در یک سبد خرید یکپارچه با تفکیک خودکار و پیش‌نمایش تخصیص اقلام.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[18px]">
                ⚡
              </div>
              <h2 className="mt-4 text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                عملیات و پردازش سریع
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پذیرش آنی، رد یا پیشنهاد مقادیر جایگزین، مراسم صبحگاهی تأیید موجودی و داشبورد صف‌محور تأمین‌کنندگان.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[18px]">
                📊
              </div>
              <h2 className="mt-4 text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                دقت و تسویه مالی شفاف
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                تطبیق مالی خودکار، ثبت ممیزی تغییرات قیمت و رهگیری دقیق مرجوعی‌ها بدون واسطه‌گری‌های پیچیده بانکی.
              </p>
            </div>
          </div>

          {/* Customer-facing pilot principles */}
          <section
            aria-labelledby="pol-pilot-principles-title"
            className="mt-14 rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 sm:p-6"
          >
            <h2
              id="pol-pilot-principles-title"
              className="text-[15px] font-bold text-[var(--pol-light-text-primary)]"
            >
              خرید عمده با فرایندی روشن و قابل پیگیری
            </h2>
            <p className="mx-auto mt-2 max-w-2xl text-[13px] leading-6 text-[var(--pol-light-text-secondary)]">
              از انتخاب کالا و ثبت سفارش تا پیگیری وضعیت و تأیید تحویل، هر مرحله برای خریدار و تأمین‌کننده روشن است.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <span className="rounded-lg bg-[var(--pol-light-surface-subtle)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                پایلوت متمرکز در اهواز
              </span>
              <span className="rounded-lg bg-[var(--pol-light-surface-subtle)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                سبد یکپارچه از چند بنکدار
              </span>
              <span className="rounded-lg bg-[var(--pol-light-surface-subtle)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                پیگیری سفارش تا تحویل
              </span>
              <span className="rounded-lg bg-[var(--pol-light-surface-subtle)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                تسویه مستقیم میان طرفین
              </span>
            </div>
          </section>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-8">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 text-[13px] text-[var(--pol-light-text-muted)]">
          <div className="flex items-center gap-2">
            <span className="font-bold text-[var(--pol-light-text-primary)]">POL (پُــــل)</span>
            <span>·</span>
            <span>پایلوت بنکداری و زنجیره تأمین FMCG</span>
          </div>

          <nav aria-label="پیوندهای فوتر" className="flex flex-wrap items-center gap-5">
            <Link href="/about" className="hover:text-[var(--pol-light-brand-primary)]">درباره ما</Link>
            <Link href="/how" className="hover:text-[var(--pol-light-brand-primary)]">نحوه کارکرد</Link>
            <Link href="/contact" className="hover:text-[var(--pol-light-brand-primary)]">تماس با ما</Link>
            <Link href="/legal" className="hover:text-[var(--pol-light-brand-primary)]">قوانین و امنیت</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
