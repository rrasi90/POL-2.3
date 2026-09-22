import Link from "next/link";
import { Button } from "@pol/ui";

/** C-04 How POL works — static, PUBLIC_ANON (G-006). */
export default function CorporateHowPage() {
  const steps = [
    {
      title: "ورود با موبایل",
      body: "OTP چهاررقمی (D-018) — بدون رمز عبور.",
    },
    {
      title: "جستجو و سبد چندفروشنده",
      body: "کالاها از چند تأمین‌کننده در یک سبد (D-014) با پیش‌نمایش تخصیص.",
    },
    {
      title: "تأیید و تفکیک سفارش",
      body: "یک گروه سفارش، چند سفارش فرزند — هر فروشنده جدا پردازش می‌کند.",
    },
    {
      title: "پذیرش و اجرا",
      body: "تأمین‌کننده پذیرش/رد/جزئی می‌زند؛ آماده‌سازی، ارسال و تحویل.",
    },
    {
      title: "تحویل با لینک",
      body: "بدون Driver App اختصاصی — تحویل با لینک و مدرک (D-023).",
    },
    {
      title: "استثنا، مرجوعی و تسویه",
      body: "اختلاف، پشتیبانی و تطبیق مالی در میز عملیات.",
    },
  ];

  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          POL چگونه کار می‌کند
        </h1>
        <ol className="mt-8 space-y-5">
          {steps.map((s, i) => (
            <li
              key={s.title}
              className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
            >
              <p className="text-[12px] text-[var(--pol-light-text-muted)]">
                مرحله {(i + 1).toLocaleString("fa-IR")}
              </p>
              <p className="mt-1 text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
                {s.title}
              </p>
              <p className="mt-1 text-[14px] leading-[22px] text-[var(--pol-light-text-secondary)]">
                {s.body}
              </p>
            </li>
          ))}
        </ol>
        <div className="mt-8">
          <Link href="/auth/login">
            <Button>ورود</Button>
          </Link>
        </div>
        <nav aria-label="ناوبری شرکتی" className="mt-10 flex flex-wrap gap-4 text-[13px]">
          <Link href="/" className="text-[var(--pol-light-brand-primary)] hover:underline">
            خانه
          </Link>
          <Link href="/retailers" className="text-[var(--pol-light-brand-primary)] hover:underline">
            خرده‌فروشان
          </Link>
          <Link href="/vendors" className="text-[var(--pol-light-brand-primary)] hover:underline">
            تأمین‌کنندگان
          </Link>
          <Link href="/pilot" className="text-[var(--pol-light-brand-primary)] hover:underline">
            پایلوت
          </Link>
        </nav>
      </div>
    </main>
  );
}
