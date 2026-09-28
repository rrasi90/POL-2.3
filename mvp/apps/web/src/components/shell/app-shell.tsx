"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { useAuthStore } from "@/lib/auth/store";
import { pathAllowed } from "@/lib/auth/routes";
import { useTheme } from "@/lib/theme";
import { useBasketStore } from "@/lib/basket";
import { Button, StatusChip } from "@pol/ui";

interface NavItem {
  href: string;
  label: string;
  roles?: string[];
  badge?: "basket";
}

const nav: NavItem[] = [
  { href: "/retailer", label: "بازار", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/catalog", label: "کاتالوگ", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/orders", label: "سفارش‌ها", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/basket", label: "سبد خرید", roles: ["RETAILER_OWNER", "RETAILER_STAFF"], badge: "basket" },
  { href: "/retailer/vendors", label: "تأمین‌کنندگان", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/finance", label: "مالی", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/support", label: "پشتیبانی", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },

  { href: "/vendor", label: "پیشخان", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/orders", label: "سفارش‌ها", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/catalog", label: "کاتالوگ کالاها", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/inventory", label: "موجودی", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/inventory/daily", label: "تأیید روزانه", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/settlements", label: "تسویه و اسناد", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },

  { href: "/ops", label: "دیدبان عملیات", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/queues", label: "صفوف کاری", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/support", label: "میز پشتیبانی", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/reconciliation", label: "تطبیق مالی", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/rma", label: "مرجوعی و اختلاف", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/admin", label: "لاگ ممیزی", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/admin", label: "مدیریت سیستم", roles: ["ADMIN_SUPER"] },

  { href: "/field", label: "فعال‌سازی میدانی", roles: ["FIELD_ACTIVATOR", "OPS_AGENT"] },
  { href: "/notifications", label: "اعلان‌ها", roles: [] },
  { href: "/profile", label: "حساب کاربری", roles: [] },
];

const roleLabels: Record<string, string> = {
  RETAILER_OWNER: "خرده‌فروش (مالک)",
  RETAILER_STAFF: "خرده‌فروش (همکار)",
  VENDOR_OWNER: "تأمین‌کننده (مالک)",
  VENDOR_STAFF: "تأمین‌کننده (همکار)",
  OPS_AGENT: "کارشناس عملیات",
  ADMIN_SUPER: "مدیر ارشد سیستم",
  FIELD_ACTIVATOR: "فعال‌ساز میدانی",
};

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { role, clear } = useAuthStore();
  const { theme, toggle } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const basketLines = useBasketStore((s) => s.lines);
  const basketCount = basketLines.reduce((acc, l) => acc + l.quantity, 0);

  const items = nav.filter((n) => {
    if (!n.roles || n.roles.length === 0) return true;
    return role ? n.roles.includes(role) : false;
  });

  function logout() {
    clear();
    router.push("/auth/login");
  }

  const isRetailer = role?.startsWith("RETAILER");
  const isVendor = role?.startsWith("VENDOR");
  const isOps = role?.startsWith("OPS") || role === "ADMIN_SUPER";

  return (
    <div className="min-h-screen bg-[var(--pol-light-bg-canvas)] text-[var(--pol-light-text-primary)] transition-colors duration-150">
      {/* Top Application Bar */}
      <header className="sticky top-0 z-40 border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]/95 shadow-[var(--pol-shadow-sm)] backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          {/* Logo & Brand Emblem */}
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-2 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)] rounded-[8px]"
              aria-label="پُل - صفحه اصلی"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-[8px] bg-[var(--pol-light-brand-primary)] text-white font-bold text-[18px] shadow-sm transition-transform duration-150 group-hover:scale-105">
                پُل
              </span>
              <div className="hidden sm:flex flex-col">
                <span className="text-[15px] font-bold tracking-tight text-[var(--pol-light-text-primary)] leading-tight">
                  POL
                </span>
                <span className="text-[10px] text-[var(--pol-light-text-muted)] tracking-wider">
                  Precision Commerce
                </span>
              </div>
            </Link>

            {/* Role Badge if Authenticated */}
            {role ? (
              <span className="hidden md:inline-flex items-center rounded-full border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
                {roleLabels[role] ?? role}
              </span>
            ) : null}
          </div>

          {/* Desktop Nav Rail */}
          <nav
            role="navigation"
            aria-label="منوی اصلی"
            className="hidden md:flex flex-1 items-center justify-center gap-1 overflow-x-auto py-1"
          >
            {items.map((n) => {
              const isActive =
                pathname === n.href ||
                (n.href !== "/" && pathname.startsWith(`${n.href}/`));
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  aria-current={isActive ? "page" : undefined}
                  className={[
                    "relative flex items-center gap-1.5 rounded-[8px] px-3 py-1.5 text-[13px] font-medium transition-all duration-[160ms]",
                    isActive
                      ? "bg-[var(--pol-light-brand-primary)]/10 text-[var(--pol-light-brand-primary)] font-semibold shadow-xs"
                      : "text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)]",
                  ].join(" ")}
                >
                  <span>{n.label}</span>
                  {n.badge === "basket" && basketCount > 0 ? (
                    <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[var(--pol-light-brand-primary)] px-1.5 text-[11px] font-bold text-white tabular-nums">
                      {basketCount.toLocaleString("fa-IR")}
                    </span>
                  ) : null}
                  {isActive ? (
                    <span
                      aria-hidden="true"
                      className="absolute bottom-0 inset-x-2 h-0.5 rounded-full bg-[var(--pol-light-brand-primary)]"
                    />
                  ) : null}
                </Link>
              );
            })}
          </nav>

          {/* Right Action Controls: Cart, Theme Toggle, Account, Mobile Drawer */}
          <div className="flex items-center gap-2">
            {/* Quick Cart button for mobile / tablet */}
            {isRetailer ? (
              <Link
                href="/retailer/basket"
                className="relative flex h-9 w-9 items-center justify-center rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-primary)] transition-colors hover:bg-[var(--pol-light-surface-subtle)] md:hidden"
                aria-label={`سبد خرید (${basketCount} قلم)`}
              >
                🛒
                {basketCount > 0 ? (
                  <span className="absolute -top-1.5 -end-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-[var(--pol-light-brand-primary)] px-1 text-[10px] font-bold text-white tabular-nums">
                    {basketCount}
                  </span>
                ) : null}
              </Link>
            ) : null}

            {/* Theme Toggle Button */}
            <button
              type="button"
              onClick={toggle}
              aria-label={theme === "light" ? "تغییر به تم شب" : "تغییر به تم روز"}
              className="flex h-9 items-center gap-1.5 rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-2.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] shadow-xs transition-colors hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)]"
            >
              <span className="text-[14px]" aria-hidden="true">
                {theme === "light" ? "🌙" : "☀️"}
              </span>
              <span className="hidden sm:inline">
                {theme === "light" ? "شب" : "روز"}
              </span>
            </button>

            {/* User Session & Logout */}
            {role ? (
              <div className="flex items-center gap-1">
                <Link
                  href="/profile"
                  className="flex h-9 w-9 items-center justify-center rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] text-[14px] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)]"
                  title="حساب کاربری"
                  aria-label="حساب کاربری"
                >
                  👤
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="hidden sm:inline-flex text-[12px] text-[var(--pol-light-text-muted)] hover:text-[var(--pol-light-semantic-danger)]"
                >
                  خروج
                </Button>
              </div>
            ) : (
              <Link href="/auth/login">
                <Button variant="primary" size="sm">
                  ورود
                </Button>
              </Link>
            )}

            {/* Mobile Menu Toggle Button */}
            <button
              type="button"
              className="flex h-9 w-9 items-center justify-center rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-primary)] md:hidden focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)]"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-expanded={mobileMenuOpen}
              aria-label="منوی ناوبری"
            >
              {mobileMenuOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer Sheet */}
        {mobileMenuOpen ? (
          <div className="border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-4 py-4 md:hidden shadow-[var(--pol-shadow-md)] transition-all animate-in fade-in slide-in-from-top-2 duration-150">
            {role ? (
              <div className="mb-3 flex items-center justify-between border-b border-[var(--pol-light-border-subtle)] pb-2 text-[12px] text-[var(--pol-light-text-muted)]">
                <span>نقش کاربری:</span>
                <span className="font-semibold text-[var(--pol-light-text-primary)]">
                  {roleLabels[role] ?? role}
                </span>
              </div>
            ) : null}

            <nav className="flex flex-col gap-1" role="navigation" aria-label="منوی موبایل">
              {items.map((n) => {
                const isActive =
                  pathname === n.href ||
                  (n.href !== "/" && pathname.startsWith(`${n.href}/`));
                return (
                  <Link
                    key={n.href}
                    href={n.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={[
                      "flex items-center justify-between rounded-[8px] px-3.5 py-2.5 text-[14px] font-medium transition-colors",
                      isActive
                        ? "bg-[var(--pol-light-brand-primary)]/10 text-[var(--pol-light-brand-primary)] font-semibold"
                        : "text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
                    ].join(" ")}
                  >
                    <span>{n.label}</span>
                    {n.badge === "basket" && basketCount > 0 ? (
                      <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[var(--pol-light-brand-primary)] px-2 text-[11px] font-bold text-white tabular-nums">
                        {basketCount}
                      </span>
                    ) : null}
                  </Link>
                );
              })}
              {role ? (
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    logout();
                  }}
                  className="mt-2 flex w-full items-center justify-start rounded-[8px] px-3.5 py-2.5 text-[14px] font-medium text-[var(--pol-light-semantic-danger)] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  خروج از حساب کاربری
                </button>
              ) : null}
            </nav>
          </div>
        ) : null}
      </header>

      {/* Main Surface Container */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 pb-20 md:pb-8">
        {children}
      </main>

      {/* Mobile Bottom Navigation Bar (Persistent Ergonomics for Smartphones) */}
      <nav
        aria-label="ناوبری سریع موبایل"
        className="fixed bottom-0 inset-x-0 z-30 flex h-14 items-center justify-around border-t border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]/95 shadow-lg backdrop-blur md:hidden"
      >
        {isRetailer ? (
          <>
            <Link
              href="/retailer"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/retailer"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🏠</span>
              <span>بازار</span>
            </Link>
            <Link
              href="/retailer/catalog"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/retailer/catalog")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🔍</span>
              <span>کاتالوگ</span>
            </Link>
            <Link
              href="/retailer/basket"
              className={`relative flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/retailer/basket"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🛒</span>
              <span>سبد</span>
              {basketCount > 0 ? (
                <span className="absolute -top-1 end-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-[var(--pol-light-brand-primary)] px-1 text-[9px] font-bold text-white tabular-nums">
                  {basketCount}
                </span>
              ) : null}
            </Link>
            <Link
              href="/retailer/orders"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/retailer/orders")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">📦</span>
              <span>سفارش‌ها</span>
            </Link>
            <Link
              href="/profile"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/profile"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">👤</span>
              <span>حساب</span>
            </Link>
          </>
        ) : isVendor ? (
          <>
            <Link
              href="/vendor"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/vendor"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">📊</span>
              <span>پیشخان</span>
            </Link>
            <Link
              href="/vendor/orders"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/vendor/orders")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">📋</span>
              <span>سفارش‌ها</span>
            </Link>
            <Link
              href="/vendor/inventory/daily"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/vendor/inventory/daily"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">✅</span>
              <span>تأیید روزانه</span>
            </Link>
            <Link
              href="/vendor/inventory"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/vendor/inventory"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">📦</span>
              <span>موجودی</span>
            </Link>
            <Link
              href="/profile"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/profile"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">👤</span>
              <span>پروفایل</span>
            </Link>
          </>
        ) : isOps ? (
          <>
            <Link
              href="/ops"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/ops"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">⚡</span>
              <span>دیدبان</span>
            </Link>
            <Link
              href="/ops/queues"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/ops/queues")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">📑</span>
              <span>صفوف</span>
            </Link>
            <Link
              href="/ops/support"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/ops/support")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🎧</span>
              <span>پشتیبانی</span>
            </Link>
            <Link
              href="/ops/reconciliation"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname.startsWith("/ops/reconciliation")
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">⚖️</span>
              <span>تطبیق</span>
            </Link>
            <Link
              href="/profile"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/profile"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">👤</span>
              <span>حساب</span>
            </Link>
          </>
        ) : (
          <>
            <Link
              href="/"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🏠</span>
              <span>خانه</span>
            </Link>
            <Link
              href="/retailers"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/retailers"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🛍️</span>
              <span>خرده‌فروشان</span>
            </Link>
            <Link
              href="/vendors"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/vendors"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🏢</span>
              <span>تأمین‌کنندگان</span>
            </Link>
            <Link
              href="/auth/login"
              className={`flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium ${
                pathname === "/auth/login"
                  ? "text-[var(--pol-light-brand-primary)] font-bold"
                  : "text-[var(--pol-light-text-muted)]"
              }`}
            >
              <span className="text-[16px]">🔑</span>
              <span>ورود</span>
            </Link>
          </>
        )}
      </nav>
    </div>
  );
}

/** Client-side UX gate — server remains authoritative. */
export function RequireRole({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { role } = useAuthStore();

  useEffect(() => {
    if (!pathAllowed(pathname, role)) {
      router.replace("/auth/login");
    }
  }, [pathname, role, router]);

  if (!pathAllowed(pathname, role)) {
    return null;
  }

  return <>{children}</>;
}
