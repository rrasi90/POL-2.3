import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../_shared";

/**
 * V-11 staff / access — G-010: no membership admin HTTP beyond self-serve profile.
 * Read-only GAP stub; no fake invite success.
 */
export default function VendorStaffPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کارکنان و دسترسی
        </h1>
        <StatusChip tone="warning">G-010</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-11</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          داده در دسترس نیست
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-010: فراتر از profile/membership خودکاربر، HTTP مدیریت عضو وجود ندارد.
          دعوت، تغییر نقش و لغو دسترسی در MVP شبیه‌سازی نمی‌شود.
        </p>
      </div>

      <section aria-label="دسترسی‌ها" className={cardCls}>
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          برای ویرایش حساب خود از <span className="text-[var(--pol-light-brand-primary)]">حساب کاربری</span>{" "}
          استفاده کنید. نقش‌های VENDOR_STAFF طبق Master Tree §38 در سرور محدود می‌شوند.
        </p>
      </section>

      <div className={cardCls}>
        <EmptyState
          title="مدیریت کارکنان"
          description="تا ارائه HTTP دعوت/عضویت، این صفحه فقط پوسته GAP است."
        />
      </div>
    </div>
  );
}
