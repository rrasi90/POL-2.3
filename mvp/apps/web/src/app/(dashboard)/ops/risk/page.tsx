import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../_shared";

export default function OpsRiskPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ریسک و پایداری
        </h1>
        <StatusChip tone="warning">GAP / محدود</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-07</span>
      </header>

      <section className={cardCls}>
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          API ریسک اختصاصی وجود ندارد. تنها سیگنال‌های واقعی در دسترس از داشبورد استثناها و
          تطبیق مالی گرفته می‌شوند — بخش‌های زیر پوسته GAP هستند و داده ساختگی ندارند.
        </p>
      </section>

      <section aria-label="بخش‌های GAP" className="grid gap-3 sm:grid-cols-2">
        <div className={`${cardCls} border-dashed`}>
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-secondary)]">
            قابلیت اطمینان تحویل
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            بدون API اختصاصی — از /ops استثناها مشاهده کنید.
          </p>
        </div>
        <div className={`${cardCls} border-dashed`}>
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-secondary)]">
            امتیاز ریسک طرف حساب
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            بدون منبع داده — هیچ مدل ریسکی تعریف نشده است.
          </p>
        </div>
      </section>

      <EmptyState
        title="متریک ریسکی موجود نیست"
        description="تا تعریف API، این صفحه فقط GAP shell است."
      />
    </div>
  );
}
