import Link from "next/link";
import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../ops/_shared";

export default function AdminUsersOrgsPage() {
  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت کاربران و سازمان‌ها
            </h1>
            <StatusChip tone="warning">G-007 GAP</StatusChip>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-10B
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            کنترل هویت کاربران، ساختار سازمان‌های همکار و تعیین وضعیت حساب‌های کاربری
          </p>
        </div>
      </header>

      {/* Architecture GAP Notice */}
      <div className="rounded-xl border border-[var(--pol-light-semantic-warning)]/30 bg-[var(--pol-light-semantic-warning)]/10 p-4">
        <p className="text-[14px] font-bold text-[var(--pol-light-semantic-warning)]">
          اطلاعیه معماری — شکاف داده‌ای G-007
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          در قرارداد فعلی MVP، مسیرهای جامع مدیریت کاربران و سازمان‌ها تنها شامل خواندن اولیه و تغییر وضعیت ادمین است. هیچ‌گونه فرم CRUD جعلی در این صفحات قرار نگرفته تا یکپارچگی سیستمی حفظ شود.
        </p>
      </div>

      {/* Module Navigation Grid */}
      <section className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/admin/users"
          className={[
            cardCls,
            "group block border-dashed transition-all duration-150 hover:border-[var(--pol-light-brand-primary)] hover:shadow-sm",
          ].join(" ")}
        >
          <div className="flex items-center justify-between">
            <p className="text-[15px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)]">
              فهرست کاربران سامانه
            </p>
            <span className="text-[13px] text-[var(--pol-light-brand-primary)]">←</span>
          </div>
          <p className="mt-2 text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
            مشاهده اطلاعات کاربران، شماره تماس، وضعیت فعال/غیرفعال و جست‌وجوی حساب‌ها
          </p>
        </Link>

        <Link
          href="/admin/orgs"
          className={[
            cardCls,
            "group block border-dashed transition-all duration-150 hover:border-[var(--pol-light-brand-primary)] hover:shadow-sm",
          ].join(" ")}
        >
          <div className="flex items-center justify-between">
            <p className="text-[15px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)]">
              فهرست سازمان‌ها و شرکت‌ها
            </p>
            <span className="text-[13px] text-[var(--pol-light-brand-primary)]">←</span>
          </div>
          <p className="mt-2 text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
            بررسی مشخصات شرکت‌ها، شناسه ملی، وضعیت پذیرش و مدیریت تعلیق یا تأیید
          </p>
        </Link>
      </section>

      {/* Related Logs Card */}
      <section className={cardCls}>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
            برای بررسی لاگ کامل ممیزی عملیات، رویدادهای سیستمی و داشبورد استثناها:
          </p>
          <Link
            href="/ops/admin"
            className="inline-flex h-8 items-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            کنسول ممیزی و مانیتورینگ (/ops/admin) ←
          </Link>
        </div>
      </section>

      <EmptyState
        title="دسترسی‌های سریع مدیریتی"
        description="جهت مدیریت حساب‌ها یا سازمان‌ها از پیوندهای بالا استفاده فرمایید."
      />
    </div>
  );
}
