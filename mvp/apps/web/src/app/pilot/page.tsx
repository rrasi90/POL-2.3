import Link from "next/link";
import { Button } from "@pol/ui";

/** C-05 Ahvaz pilot — static, PUBLIC_ANON (G-006, D-001 single-city). */
export default function CorporatePilotPage() {
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

      <main className="flex-1 py-12 md:py-16">
        <div className="mx-auto max-w-4xl px-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--pol-light-brand-primary)]/20 bg-[var(--pol-light-brand-primary)]/10 px-3 py-0.5 text-[11px] font-semibold text-[var(--pol-light-brand-primary)]">
            PRECISION COMMERCE · محدوده عملیاتی پایلوت
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            طرح پایلوت بنکداری و زنجیره تأمین اهواز
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            نسخه فعلی پلتفرم پول (MVP) به صورت اختصاصی بر روی بازار بنکداران و سوپرمارکت‌های شهر اهواز متمرکز است (D-001). این تمرکز هدفمند امکان دستیابی به بالاترین نرخ تکمیل موفق سفارش (OTIF) و هماهنگی دقیق میدانی را فراهم می‌سازد.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                تک‌شهره و تمرکز جغرافیایی (D-001)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                تمام تراکنش‌ها، ردیابی ناوگان و انبارها مربوط به منطقه شهری اهواز است؛ توسعه به شهرهای همجوار در فازهای بعدی پس از تثبیت شاخص‌های کلیدی صورت خواهد گرفت.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                دسته کالایی تندمصرف (FMCG)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                تمرکز بر اقلام پرمصرف سوپرمارکتی، شوینده‌ها، لبنیات، خواربار و نوشیدنی‌ها با اعمال حداقل مقدار سفارش (MOQ) و بسته‌بندی کارتن/شرینک رسمی.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                سادگی فرآیند بدون کیف پول واسط (D-021)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پلتفرم حساب بانکی واسط یا پول مسدودشده ندارد؛ پرداخت‌ها مستقیماً بر اساس فاکتورهای رسمی و توافقات مالی بین خریدار و تأمین‌کننده مدیریت می‌شوند.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                ردیابی مدرن تحویل با پیوند اختصاصی (D-023)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پایان وابستگی به اپلیکیشن‌های متعدد رانندگان؛ متصدی ارسال حواله تحویل را با یک لمس روی پیوند امن ثبت و امضا می‌نماید.
              </p>
            </div>
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/contact">
              <Button size="lg">ثبت‌نام و عضویت در پایلوت اهواز</Button>
            </Link>
            <Link href="/how">
              <Button variant="secondary" size="lg">مراحل و نحوه سفارش‌گذاری</Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-6">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4 px-6 text-[12px] text-[var(--pol-light-text-muted)]">
          <span>POL — پایلوت اهواز (B2B FMCG)</span>
          <nav aria-label="پیوندهای کمکی" className="flex gap-4">
            <Link href="/" className="hover:underline">خانه</Link>
            <Link href="/about" className="hover:underline">درباره</Link>
            <Link href="/legal" className="hover:underline">قوانین و امنیت</Link>
            <Link href="/contact" className="hover:underline">تماس</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
