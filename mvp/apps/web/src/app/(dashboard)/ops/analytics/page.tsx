import { EmptyState, StatusChip } from "@pol/ui";

export default function OpsAnalyticsPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تحلیل پایلوت
        </h1>
        <StatusChip tone="warning">G-008</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-09</span>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-4">
        <p className="text-[14px] font-semibold text-[var(--pol-light-semantic-warning)]">
          داده در دسترس نیست
        </p>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-008: هیچ endpoint تحلیلی در inventory وجود ندارد. هیچ مسیر API اختراع نشده و
          هیچ متریک ساختگی نمایش داده نمی‌شود.
        </p>
      </div>

      <EmptyState
        title="شاخص‌های پایلوت"
        description="تا زمانی که بک‌اند خواندنی تحلیل ارائه دهد، این صفحه فقط پوسته GAP است."
      />
    </div>
  );
}
