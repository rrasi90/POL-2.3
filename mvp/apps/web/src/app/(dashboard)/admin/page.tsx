import Link from "next/link";
import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../ops/_shared";

export default function AdminUsersOrgsPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          مدیریت کاربران و سازمان‌ها
        </h1>
        <StatusChip tone="warning">G-007</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-10B</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          بدون API — شکاف G-007
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          هیچ endpoint برای فهرست، ایجاد، ویرایش یا حذف کاربران و سازمان‌ها وجود ندارد. این صفحه
          عمداً هیچ CRUD جعلی ارائه نمی‌دهد.
        </p>
      </div>

      <section className="grid gap-3 sm:grid-cols-2">
        <Link
          href="/admin/users"
          className={`${cardCls} border-dashed transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]`}
        >
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-secondary)]">
            کاربران
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            لیست stub — بدون منبع API
          </p>
        </Link>
        <Link
          href="/admin/orgs"
          className={`${cardCls} border-dashed transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]`}
        >
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-secondary)]">
            سازمان‌ها
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            لیست stub — بدون منبع API
          </p>
        </Link>
      </section>

      <section className={cardCls}>
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          لاگ ممیزی و داشبورد استثناها در{" "}
          <Link
            href="/ops/admin"
            className="text-[var(--pol-light-brand-primary)] hover:underline"
          >
            /ops/admin
          </Link>{" "}
          در دسترس است (O-10، API واقعی).
        </p>
      </section>

      <EmptyState
        title="هیچ داده‌ای برای نمایش نیست"
        description="تا زمانی که backend لیست کاربران/سازمان‌ها را ارائه دهد، این صفحه GAP باقی می‌ماند."
      />
    </div>
  );
}
