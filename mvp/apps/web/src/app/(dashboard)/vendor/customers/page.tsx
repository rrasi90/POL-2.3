import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../_shared";

/**
 * V-09 customers — G-009: no customers list API in inventory or routes.
 * No derive from orders (not documented). GAP shell only; no fake data.
 */
export default function VendorCustomersPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          مشتریان
        </h1>
        <StatusChip tone="warning">G-009</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-09</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          داده در دسترس نیست
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-009: هیچ endpoint فهرست مشتری در inventory یا route map وجود ندارد. مشتق
          گرفتن از سفارش‌ها مستند نشده — انجام نمی‌شود. هیچ مسیر API اختراع نشده است.
        </p>
      </div>

      <div className={cardCls}>
        <EmptyState
          title="فهرست مشتریان"
          description="تا ارائه HTTP از بک‌اند، این صفحه فقط پوسته GAP است."
        />
      </div>
    </div>
  );
}
