import Link from "next/link";
import { Button } from "@pol/ui";

/** C-05 Ahvaz pilot — static, PUBLIC_ANON (G-006, D-001 single-city). */
export default function CorporatePilotPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          پایلوت اهواز
        </h1>
        <p className="mt-4 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          MVP فقط روی یک شهر متمرکز است — اهواز (D-001). چندشهره بودن خارج از دامنه است.
        </p>
        <section className="mt-8 space-y-4">
          <h2 className="text-[18px] leading-[28px] font-semibold text-[var(--pol-light-text-primary)]">
            دامنه پایلوت
          </h2>
          <ul className="list-disc space-y-2 ps-5 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
            <li>خرده‌فروشان محلی و تأمین‌کنندگان منطقه</li>
            <li>سفارش‌گذاری عمده با تخصیص چندفروشنده</li>
            <li>بدون کیف پول، بدون اسکرو، بدون Driver App</li>
            <li>بدون چندشهره — توسعه شهری در نسخه‌های آینده</li>
          </ul>
        </section>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/contact">
            <Button>تماس برای همکاری</Button>
          </Link>
          <Link href="/how">
            <Button variant="secondary">نحوه کار</Button>
          </Link>
        </div>
        <nav aria-label="ناوبری شرکتی" className="mt-10 flex flex-wrap gap-4 text-[13px]">
          <Link href="/" className="text-[var(--pol-light-brand-primary)] hover:underline">
            خانه
          </Link>
          <Link href="/about" className="text-[var(--pol-light-brand-primary)] hover:underline">
            درباره
          </Link>
          <Link href="/legal" className="text-[var(--pol-light-brand-primary)] hover:underline">
            قوانین
          </Link>
        </nav>
      </div>
    </main>
  );
}
