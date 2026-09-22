"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { useAuthStore } from "@/lib/auth/store";
import { roleHome, pathAllowed } from "@/lib/auth/routes";
import { useTheme } from "@/lib/theme";
import { Button } from "@pol/ui";

interface NavItem {
  href: string;
  label: string;
  roles?: string[];
}

const nav: NavItem[] = [
  { href: "/retailer", label: "بازار خرده‌فروشی", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/orders", label: "سفارش‌ها", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/basket", label: "سبد", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/vendor", label: "پنل تأمین‌کننده", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/orders", label: "سفارش‌های فروشنده", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/ops", label: "عملیات", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/support", label: "پشتیبانی", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/field", label: "فعال‌سازی میدانی", roles: ["FIELD_ACTIVATOR", "OPS_AGENT"] },
  { href: "/notifications", label: "اعلان‌ها", roles: [] },
  { href: "/profile", label: "حساب", roles: [] },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { role, clear } = useAuthStore();
  const { theme, toggle } = useTheme();
  const [open, setOpen] = useState(false);

  const items = nav.filter((n) => {
    if (!n.roles || n.roles.length === 0) return true;
    return role ? n.roles.includes(role) : false;
  });

  function logout() {
    clear();
    router.push("/auth/login");
  }

  return (
    <div className="min-h-screen bg-[var(--pol-light-bg-canvas)] text-[var(--pol-light-text-primary)]">
      <header className="sticky top-0 z-40 border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4">
          <Link href="/" className="font-bold text-[var(--pol-light-brand-primary)]">
            POL
          </Link>
          <nav className="hidden flex-1 items-center gap-1 md:flex">
            {items.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className={[
                  "rounded-[8px] px-3 py-1.5 text-[13px] transition-colors duration-[160ms]",
                  pathname === n.href || pathname.startsWith(`${n.href}/`)
                    ? "bg-[var(--pol-light-surface-subtle)] font-semibold"
                    : "text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
                ].join(" ")}
              >
                {n.label}
              </Link>
            ))}
          </nav>
          <div className="ms-auto flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={toggle} aria-label="تغییر تم">
              {theme === "light" ? "شب" : "روز"}
            </Button>
            <Button variant="ghost" size="sm" onClick={logout}>
              خروج
            </Button>
            <Button
              variant="secondary"
              size="sm"
              className="md:hidden"
              onClick={() => setOpen((v) => !v)}
              aria-expanded={open}
              aria-label="منو"
            >
              ☰
            </Button>
          </div>
        </div>
        {open ? (
          <nav className="flex flex-col gap-1 border-t border-[var(--pol-light-border-subtle)] p-3 md:hidden">
            {items.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                onClick={() => setOpen(false)}
                className="rounded-[8px] px-3 py-2 text-[14px] hover:bg-[var(--pol-light-surface-subtle)]"
              >
                {n.label}
              </Link>
            ))}
          </nav>
        ) : null}
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
}

/** Client-side UX gate — server remains authoritative. */
export function RequireRole({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const role = useAuthStore((s) => s.role);
  const accessToken = useAuthStore((s) => s.accessToken);
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const allowed = pathAllowed(pathname, role);
    if (!allowed) {
      if (!accessToken) router.replace("/auth/login");
      else router.replace(role ? (roleHome[role] ?? "/") : "/");
      return;
    }
    setChecked(true);
  }, [pathname, role, accessToken, router]);

  if (!checked) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-[var(--pol-light-text-muted)]">
        در حال بررسی دسترسی…
      </div>
    );
  }
  return <>{children}</>;
}
