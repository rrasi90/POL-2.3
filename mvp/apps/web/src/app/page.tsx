import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">POL MVP</h1>
      <p className="mt-2 text-sm opacity-80">
        مونوریپوی MVP — فاز ۰ (کشف و مستندات) و فاز ۱ (Foundation) در حال اجرا.
      </p>
      <nav className="mt-6 flex flex-col gap-2">
        <Link href="/auth/login">ورود</Link>
        <Link href="/retailer">پنل خرده‌فروش</Link>
        <Link href="/vendor">پنل تأمین‌کننده</Link>
        <Link href="/ops">پنل عملیات</Link>
        <Link href="/field">پنل میدانی</Link>
      </nav>
    </main>
  );
}
