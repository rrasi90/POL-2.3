import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../_shared";

/**
 * OP-13 master SKU / candidate review — CONTRACT: POST /product-candidates only.
 * No REAL list/read HTTP for candidates → GAP shell; no fake queue.
 */
export default function OpsCatalogCandidatesPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کاندیداهای کاتالوگ
        </h1>
        <StatusChip tone="warning">CONTRACT / GAP</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">OP-13</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          داده در دسترس نیست
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          فقط POST <span dir="ltr">/api/v1/product-candidates</span> در inventory قراردادی
          است — endpoint خواندن/فهرست وجود ندارد. صف بررسی بدون HTTP واقعی ساخته نمی‌شود.
        </p>
      </div>

      <div className={cardCls}>
        <EmptyState
          title="بازبینی SKU اصلی"
          description="تا ارائه HTTP فهرست کاندیدا، این صفحه فقط پوسته GAP است."
        />
      </div>
    </div>
  );
}
