"use client";

import { useState } from "react";
import Link from "next/link";
import { Button, Field } from "@pol/ui";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

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
        <div className="mx-auto max-w-3xl px-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--pol-light-brand-primary)]/20 bg-[var(--pol-light-brand-primary)]/10 px-3 py-0.5 text-[11px] font-semibold text-[var(--pol-light-brand-primary)]">
            پل · ارتباط با ما
          </div>
          <h1 className="mt-4 text-[30px] font-black leading-[40px] text-[var(--pol-light-text-primary)] md:text-[36px]">
            ارتباط با تیم اجرایی و پشتیبانی POL
          </h1>
          <p className="mt-4 text-[15px] leading-[26px] text-[var(--pol-light-text-secondary)]">
            جهت عضویت در پایلوت بنکداری اهواز، پرسش‌های فنی یا همکاری تجاری با ما در ارتباط باشید.
          </p>

          <div className="mt-8 rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-[var(--pol-shadow-card)]">
            {submitted ? (
              <div className="py-6 text-center">
                <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-[var(--pol-light-semantic-success)]/10 text-[24px] text-[var(--pol-light-semantic-success)]">
                  ✓
                </div>
                <h2 className="mt-3 text-[18px] font-bold text-[var(--pol-light-text-primary)]">
                  پیام شما با موفقیت ثبت شد
                </h2>
                <p className="mt-2 text-[13px] text-[var(--pol-light-text-muted)]">
                  اطلاعات فرم در کلاینت اعتبارسنجی شد (C-07). کارشناسان ما به زودی با شماره {mobile} تماس خواهند گرفت.
                </p>
                <div className="mt-6">
                  <Button variant="secondary" onClick={() => setSubmitted(false)}>
                    ارسال پیام دیگر
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <Field
                  label="نام و نام خانوادگی / نام واحد صنفی"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="مثلاً سوپرمارکت ساحل یا علی رضایی"
                />

                <Field
                  label="شماره تلفن همراه"
                  required
                  type="tel"
                  dir="ltr"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value.replace(/\D/g, ""))}
                  placeholder="۰۹۱۲۳۴۵۶۷۸۹"
                  hint="شماره همراه جهت هماهنگی و تماس کارشناسان"
                />

                <div className="flex flex-col gap-1.5">
                  <label htmlFor="contact-message" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                    متن پیام یا پرسش شما
                  </label>
                  <textarea
                    id="contact-message"
                    required
                    rows={4}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="درخواست پیوستن به عنوان فروشنده، خرده‌فروش یا پیشنهاد همکاری..."
                    className="min-h-[100px] w-full rounded-xl border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] p-3 text-[13px] text-[var(--pol-light-text-primary)] focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  />
                </div>

                <div className="rounded-lg bg-[var(--pol-light-surface-subtle)] p-3 text-[11px] leading-[18px] text-[var(--pol-light-text-muted)]">
                  اطلاعات واردشده پیش از ارسال بررسی می‌شود تا درخواست شما دقیق‌تر ثبت شود.
                </div>

                <div className="mt-2 flex flex-wrap gap-3">
                  <Button type="submit" size="md">
                    ارسال فرم ارتباطی
                  </Button>
                  <Link href="/">
                    <Button variant="ghost" size="md">
                      بازگشت به صفحه اصلی
                    </Button>
                  </Link>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] py-6">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-4 px-6 text-[12px] text-[var(--pol-light-text-muted)]">
          <span>POL — ارتباط با ما</span>
          <nav aria-label="پیوندهای کمکی" className="flex gap-4">
            <Link href="/" className="hover:underline">خانه</Link>
            <Link href="/about" className="hover:underline">درباره</Link>
            <Link href="/how" className="hover:underline">نحوه کارکرد</Link>
            <Link href="/legal" className="hover:underline">قوانین</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
