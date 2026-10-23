import Link from "next/link";

export default function NotFound() {
  return (
    <main
      dir="rtl"
      className="flex min-h-screen flex-col items-center justify-center gap-5 bg-[var(--pol-light-bg-canvas)] px-6 text-center text-[var(--pol-light-text-primary)]"
    >
      <p className="text-sm font-semibold text-[var(--pol-light-text-secondary)]">۴۰۴</p>
      <h1 className="text-2xl font-black">این صفحه پیدا نشد</h1>
      <p className="max-w-md text-sm leading-7 text-[var(--pol-light-text-secondary)]">
        نشانی واردشده وجود ندارد یا دسترسی به آن مجاز نیست. اگر از طریق اعلان یا لینک قدیمی
        وارد شده‌اید، از داشبورد خود ادامه دهید.
      </p>
      <Link
        href="/"
        className="rounded-xl bg-[var(--pol-light-brand-primary)] px-4 py-2 text-sm font-bold text-white"
      >
        بازگشت به صفحهٔ اصلی
      </Link>
    </main>
  );
}
