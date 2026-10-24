import Link from "next/link";
import { Button } from "@pol/ui";

export default function LegalPage() {
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
            PRECISION COMMERCE · شفافیت حقوقی و امنیت
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            قوانین، شرایط استفاده و حریم خصوصی
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            سیاست‌های ناظر بر فرآیند سفارش‌گذاری، حریم خصوصی شماره‌های تماس، اعتبار فاکتورها و ممیزی تراکنش‌های تجاری در پلتفرم پُل.
          </p>

          <div className="mt-10 space-y-5">
            <section className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                ۱. حریم خصوصی و اطلاعات هویتی
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پلتفرم پُل تنها داده‌های ضروری برای احراز هویت، ثبت سفارش، صدور فاکتور و هماهنگی ارسال را ذخیره می‌کند. شماره تلفن همراه تنها جهت ارسال کد یکبار مصرف (OTP) و پیامک‌های ردیابی سفارش به کار گرفته شده و در اختیار اشخاص ثالث تبلیغاتی قرار نخواهد گرفت.
              </p>
            </section>

            <section className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                ۲. احراز هویت، کنترل دسترسی و ممیزی (D-018)
              </h2>
              <ul className="mt-2 list-disc space-y-1.5 ps-5 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                <li>ورود کاربران صرفاً از طریق پیامک رمز یکبار مصرف ۶ رقمی (OTP) با طول عمر ۱۲۰ ثانیه امکان‌پذیر است.</li>
                <li>سامانه مبتنی بر تفکیک دقیق نقش‌های کاربری (RBAC) طراحی شده است.</li>
                <li>تمامی رویدادهای مالی، تغییر قیمت و تغییر وضعیت سفارشات دارای ردپای ممیزی (Audit Trail) و زمان دقیق هستند.</li>
              </ul>
            </section>

            <section className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                ۳. شرایط سفارش، تسویه و عدم نگهداری وجوه (D-021 / D-025)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                پلتفرم پُل یک سامانه مدیریت سفارش است و نه یک نهاد بانکی یا واسط مالی؛ هیچ‌گونه کیف پول اعتباری یا حساب اسکرو در سیستم وجود ندارد. تسویه‌حساب‌ها طبق فاکتورهای رسمی و توافقات عرفی میان خریدار و تأمین‌کننده انجام می‌گیرد.
              </p>
            </section>

            <section className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
              <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                ۴. فرآیند تحویل و مرجوعی کالا (D-023)
              </h2>
              <p className="mt-2 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                تحویل بار با ارائه لینک رمزنگاری‌شده و ثبت تأیید تحویل از سوی تحویل‌گیرنده نهایی می‌شود. در صورت کسری بار، آسیب یا مغایرت اقلام، مراتب از طریق بخش پشتیبانی و استثناهای سفارش ظرف مهلت مقرر ثبت خواهد شد.
              </p>
            </section>
          </div>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/">
              <Button size="md">بازگشت به خانه</Button>
            </Link>
            <Link href="/about">
              <Button variant="secondary" size="md">درباره پلتفرم POL</Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-6">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4 px-6 text-[12px] text-[var(--pol-light-text-muted)]">
          <span>POL — قوانین و شرایط استفاده</span>
          <nav aria-label="پیوندهای کمکی" className="flex gap-4">
            <Link href="/" className="hover:underline">خانه</Link>
            <Link href="/how" className="hover:underline">نحوه کارکرد</Link>
            <Link href="/pilot" className="hover:underline">پایلوت اهواز</Link>
            <Link href="/contact" className="hover:underline">تماس</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
