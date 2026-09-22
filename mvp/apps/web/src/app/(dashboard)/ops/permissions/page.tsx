import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../_shared";

/**
 * OP-11 permission audit — GAP: no permission-list HTTP in inventory.
 * Shell only; no fake audit rows.
 */
export default function OpsPermissionsPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ممیزی دسترسی‌ها
        </h1>
        <StatusChip tone="warning">GAP</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">OP-11</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          داده در دسترس نیست
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          endpoint فهرست مجوزها / نقش‌ها در inventory و route map وجود ندارد. هیچ مسیر API
          اختراع نشده و ردیف ممیزی ساختگی نمایش داده نمی‌شود.
        </p>
      </div>

      <div className={cardCls}>
        <EmptyState
          title="ممیزی دسترسی"
          description="تا ارائه HTTP از بک‌اند، این صفحه فقط پوسته GAP است."
        />
      </div>
    </div>
  );
}
