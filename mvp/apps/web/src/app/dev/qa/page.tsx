"use client";

import { useState } from "react";
import Link from "next/link";
import type { Role } from "@pol/types";

const roles: Role[] = [
  "RETAILER_OWNER",
  "RETAILER_STAFF",
  "VENDOR_OWNER",
  "VENDOR_STAFF",
  "OPS_AGENT",
  "ADMIN_SUPER",
  "FIELD_ACTIVATOR",
];

const routeGroups = [
  {
    title: "عمومی / احراز هویت",
    role: "PUBLIC",
    routes: [
      ["/", "Home"],
      ["/auth/login", "Login + OTP"],
      ["/retailers", "Retailers"],
      ["/vendors", "Vendors"],
      ["/how", "How POL works"],
      ["/pilot", "Ahvaz pilot"],
      ["/about", "About"],
      ["/contact", "Contact"],
      ["/legal", "Legal"],
    ],
  },
  {
    title: "Retailer",
    role: "RETAILER",
    routes: [
      ["/retailer", "Dashboard"],
      ["/retailer/catalog", "Catalog"],
      ["/retailer/catalog/prd-001", "Product detail"],
      ["/retailer/basket", "Basket"],
      ["/retailer/checkout", "Checkout"],
      ["/retailer/orders", "Orders"],
      ["/retailer/orders/ord-001", "Order detail"],
      ["/retailer/orders/group/grp-qa-001", "Order group"],
      ["/retailer/orders/ord-001/returns", "Returns / disputes"],
      ["/retailer/support", "Support"],
      ["/retailer/finance", "Finance"],
      ["/retailer/vendors", "Vendor search"],
      ["/retailer/vendors/ven-001", "Vendor storefront"],
    ],
  },
  {
    title: "Vendor",
    role: "VENDOR",
    routes: [
      ["/vendor", "Dashboard"],
      ["/vendor/catalog", "Catalog"],
      ["/vendor/catalog/vp-001/prices", "Pricing"],
      ["/vendor/inventory", "Inventory"],
      ["/vendor/inventory/daily", "Daily inventory"],
      ["/vendor/referrals", "Referrals"],
      ["/vendor/customers", "Customers"],
      ["/vendor/settlements", "Settlements"],
      ["/vendor/staff", "Staff"],
      ["/vendor/storefront", "Storefront"],
      ["/vendor/finance", "Finance"],
      ["/vendor/orders", "Orders"],
      ["/vendor/orders/ord-001", "Order detail"],
    ],
  },
  {
    title: "Ops / Admin",
    role: "OPS",
    routes: [
      ["/ops", "Overview"],
      ["/ops/queues", "Unified queues"],
      ["/ops/orders/ord-001", "Object detail (order)"],
      ["/ops/support", "Support workbench"],
      ["/ops/rma", "RMA workbench"],
      ["/ops/reconciliation", "Reconciliation"],
      ["/ops/risk", "Risk / reliability"],
      ["/ops/notifications", "Notification ops"],
      ["/ops/analytics", "Pilot analytics"],
      ["/ops/admin", "Admin context"],
      ["/ops/permissions", "Permission audit"],
      ["/ops/catalog-candidates", "Master SKU / candidates"],
      ["/admin/users", "Admin users"],
      ["/admin/orgs", "Admin organizations"],
    ],
  },
  {
    title: "Field",
    role: "FIELD",
    routes: [
      ["/field", "Task list"],
      ["/field/tasks/task-001", "Task detail"],
    ],
  },
  {
    title: "Shared",
    role: "AUTH",
    routes: [
      ["/profile", "Profile"],
      ["/notifications", "Notifications"],
      ["/notifications/preferences", "Notification preferences"],
      ["/dev/components", "Component gallery"],
    ],
  },
];

function setCookie(name: string, value: string, maxAge = 7 * 24 * 3600) {
  document.cookie = `${name}=${encodeURIComponent(value)}; Path=/; Max-Age=${maxAge}; SameSite=Lax`;
}

function enterAs(role: Role) {
  const userId = `qa-${role.toLowerCase()}`;
  setCookie("pol.session", "1");
  setCookie("pol.role", role);
  setCookie("pol.qa.role", role);
  window.localStorage.setItem(
    "pol.auth",
    JSON.stringify({
      accessToken: `qa-access-${role}`,
      refreshToken: `qa-refresh-${role}`,
      role,
      user: {
        user_id: userId,
        mobile_number: "09120000000",
        organization_id: role.includes("RETAILER")
          ? "org-ret-001"
          : role.includes("VENDOR")
            ? "org-ven-001"
            : "org-pol-001",
        role,
      },
    }),
  );
  window.location.href = role.includes("RETAILER")
    ? "/retailer"
    : role.includes("VENDOR")
      ? "/vendor"
      : role === "FIELD_ACTIVATOR"
        ? "/field"
        : "/ops";
}

function setQa(name: string, value: string) {
  setCookie(`pol.qa.${name}`, value);
  window.location.reload();
}

function resetQa() {
  ["pol.qa.role", "pol.qa.delay", "pol.qa.fail", "pol.qa.dataset", "pol.qa.unauthorized"].forEach((name) =>
    setCookie(name, "", 0),
  );
  document.cookie = "pol.session=; Path=/; Max-Age=0";
  document.cookie = "pol.role=; Path=/; Max-Age=0";
  window.localStorage.removeItem("pol.auth");
  window.localStorage.removeItem("pol.basket");
  window.location.reload();
}

export default function QALabPage() {
  const [now] = useState(() => new Date().toISOString());

  return (
    <main className="min-h-screen bg-[var(--pol-light-bg-canvas)] px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="rounded-[16px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6">
          <div className="flex flex-wrap items-start gap-4">
            <div>
              <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--pol-light-text-muted)]">
                POL-2.3 / Vercel QA Lab
              </p>
              <h1 className="mt-2 text-[28px] font-bold text-[var(--pol-light-text-primary)]">
                محیط تست Frontend و Flow
              </h1>
              <p className="mt-2 max-w-3xl text-[13px] leading-6 text-[var(--pol-light-text-secondary)]">
                این محیط فقط برای تست UI، route، interaction، state، error، latency، accessibility
                و visual regression است. داده‌ها mock هستند و به PostgreSQL یا FastAPI واقعی وصل نمی‌شوند.
              </p>
            </div>
            <div className="ms-auto rounded-[12px] bg-[var(--pol-light-surface-subtle)] px-3 py-2 text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
              {now}
            </div>
          </div>
        </header>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-[16px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5">
            <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
              ورود مستقیم با Role
            </h2>
            <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
              بدون OTP واقعی، session و role آزمایشی تنظیم می‌شود.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {roles.map((role) => (
                <button
                  key={role}
                  type="button"
                  className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-2 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                  onClick={() => enterAs(role)}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-[16px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5">
            <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
              Fault Injection
            </h2>
            <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
              برای تست loading، timeout-like UX، error state و recovery.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <label className="text-[12px] text-[var(--pol-light-text-secondary)]">
                Delay
                <select
                  className="mt-1 h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-2"
                  defaultValue="0"
                  onChange={(e) => setQa("delay", e.target.value)}
                >
                  <option value="0">0 ms</option>
                  <option value="300">300 ms</option>
                  <option value="1200">1200 ms</option>
                  <option value="3000">3000 ms</option>
                </select>
              </label>
              <label className="text-[12px] text-[var(--pol-light-text-secondary)]">
                Failure
                <select
                  className="mt-1 h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-2"
                  defaultValue="none"
                  onChange={(e) => setQa("fail", e.target.value)}
                >
                  <option value="none">None</option>
                  <option value="500">HTTP 500</option>
                  <option value="mutations">Mutations only</option>
                </select>
              </label>
              <label className="text-[12px] text-[var(--pol-light-text-secondary)]">
                Dataset
                <select
                  className="mt-1 h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-2"
                  defaultValue="normal"
                  onChange={(e) => setQa("dataset", e.target.value)}
                >
                  <option value="normal">Normal</option>
                  <option value="large">50-row stress</option>
                </select>
              </label>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-2 text-[12px]"
                onClick={() => {
                  setCookie("pol.qa.unauthorized", "1");
                  window.location.reload();
                }}
              >
                401 / Refresh path
              </button>
              <button
                type="button"
                className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-2 text-[12px]"
                onClick={resetQa}
              >
                Reset QA session
              </button>
            </div>
          </div>
        </section>

        {routeGroups.map((group) => (
          <section
            key={group.title}
            className="rounded-[16px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-5"
          >
            <div className="flex flex-wrap items-baseline gap-2">
              <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">{group.title}</h2>
              <span className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                {group.role}
              </span>
            </div>
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {group.routes.map(([href, label]) => (
                <Link
                  key={href}
                  href={href}
                  className="rounded-[10px] border border-[var(--pol-light-border-subtle)] px-3 py-3 text-[13px] text-[var(--pol-light-text-primary)] hover:border-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  <span className="font-medium">{label}</span>
                  <span className="mt-1 block font-mono text-[10px] text-[var(--pol-light-text-muted)]" dir="ltr">
                    {href}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))}

        <footer className="rounded-[16px] border border-dashed border-[var(--pol-light-border-subtle)] p-5 text-[12px] leading-6 text-[var(--pol-light-text-secondary)]">
          <p>
            معیار خروج این محیط: route smoke + interaction + responsive + accessibility + loading/empty/error
            + visual regression + mock API contract coverage. اعتبارسنجی SQL، transaction، concurrency،
            migration و business-rule backend عمداً خارج از این محیط است.
          </p>
        </footer>
      </div>
    </main>
  );
}
