import Link from "next/link";
import { Button } from "@pol/ui";

/** C-04 How POL works — static, PUBLIC_ANON (G-006). */
export default function CorporateHowPage() {
  const steps = [
    {
      step: 1,
      title: "ورود امن با شماره همراه",
      body: "بدون نیاز به حفظ رمز عبور پیچیده؛ ورود با کد یکبارمصرف شش‌رقمی که به شماره همراه شما پیامک می‌شود.",
      icon: "📱",
    },
    {
      step: 2,
      title: "جست‌وجو و سبد خرید چندفروشنده‌ای",
      body: "امکان انتخاب اقلام سوپرمارکتی از چندین بنکدار و تأمین‌کننده معتبر به صورت همزمان در یک سبد خرید یکپارچه .",
      icon: "🛒",
    },
    {
      step: 3,
      title: "ثبت گروه سفارش و تفکیک خودکار",
      body: "یک گروه سفارش ثبت می‌شود و سیستم به صورت خودکار آن را به سفارش‌های مجزا برای هر تأمین‌کننده تفکیک می‌کند.",
      icon: "🔀",
    },
    {
      step: 4,
      title: "بررسی و پذیرش توسط تأمین‌کننده",
      body: "تأمین‌کننده سفارش را بررسی نموده و امکان پذیرش کامل، رد یا پیشنهاد مقادیر جایگزین با هماهنگی خریدار را دارد.",
      icon: "📋",
    },
    {
      step: 5,
      title: "ارسال و تحویل چابک با لینک",
      body: "متصدیان پخش و رانندگان بدون نیاز به اپ مجزا، تحویل را با لینک اختصاصی و تأیید بارکد/حواله نهایی می‌کنند.",
      icon: "🚚",
    },
    {
      step: 6,
      title: "تطبیق مالی، پشتیبانی و تسویه شفاف",
      body: "پیگیری اختلافات، مغایرت‌های مالی احتمالی و صدور فاکتور رسمی در میز عملیات پلتفرم با نظارت کامل طرفین.",
      icon: "💳",
    },
  ];

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
            PRECISION COMMERCE · چرخه سفارش‌گذاری
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            سامانه POL چگونه کار می‌کند؟
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            فرآیند ساده، گام‌به‌گام و بدون واسطه خرید عمده برای سوپرمارکت‌ها و فروشندگان مواد غذایی در استان خوزستان
          </p>

          <ol className="mt-10 space-y-4">
            {steps.map((s) => (
              <li
                key={s.step}
                className="flex items-start gap-4 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]"
              >
                <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[20px]">
                  {s.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="rounded-md bg-[var(--pol-light-brand-primary)]/10 px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-brand-primary)]">
                      مرحله {s.step.toLocaleString("fa-IR")}
                    </span>
                    <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                      {s.title}
                    </h2>
                  </div>
                  <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                    {s.body}
                  </p>
                </div>
              </li>
            ))}
          </ol>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/auth/login">
              <Button size="lg">ورود و ثبت سفارش</Button>
            </Link>
            <Link href="/pilot">
              <Button variant="secondary" size="lg">جزئیات پایلوت اهواز</Button>
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
            <Link href="/about" className="hover:underline">درباره</Link>
            <Link href="/retailers" className="hover:underline">خرده‌فروشان</Link>
            <Link href="/vendors" className="hover:underline">تأمین‌کنندگان</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
