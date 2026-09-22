"use client";

import Link from "next/link";
import { Button } from "@pol/ui";

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)]">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="mb-2 text-[12px] font-semibold tracking-wide text-[var(--pol-light-brand-primary)]">
          Precision Commerce
        </p>
        <h1 className="text-[32px] leading-[40px] font-bold text-[var(--pol-light-text-primary)]">
          تماس با ما
        </h1>
        <p className="mt-4 text-[14px] leading-[24px] text-[var(--pol-light-text-secondary)]">
          برای همکاری، پایلوت یا پرسش درباره POL با ما در تماس باشید. این فرم فقط اعتبارسنجی
          سمت کلاینت دارد — بدون endpoint ارسال (C-07).
        </p>

        <form
          className="mt-8 grid max-w-lg gap-4"
          onSubmit={(e) => {
            e.preventDefault();
          }}
        >
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="contact-name"
              className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              نام
            </label>
            <input
              id="contact-name"
              name="name"
              required
              maxLength={120}
              className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="contact-mobile"
              className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              شماره موبایل
            </label>
            <input
              id="contact-mobile"
              name="mobile"
              type="tel"
              dir="ltr"
              required
              pattern="09[0-9]{9}"
              title="شماره موبایل ۱۱ رقمی"
              className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="contact-message"
              className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              پیام
            </label>
            <textarea
              id="contact-message"
              name="message"
              required
              rows={4}
              maxLength={2000}
              className="min-h-[96px] w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] resize-y"
            />
          </div>
          <p role="status" className="text-[12px] text-[var(--pol-light-text-muted)]">
            ارسال واقعی پس از افزودن endpoint فعال می‌شود — فعلاً فقط اعتبارسنجی محلی.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button type="submit">بررسی فرم</Button>
            <Link href="/">
              <Button variant="ghost">بازگشت</Button>
            </Link>
          </div>
        </form>
      </div>
    </main>
  );
}
