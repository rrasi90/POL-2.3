import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../../ops/_shared";

export default function AdminOrgsPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          سازمان‌ها
        </h1>
        <StatusChip tone="warning">G-007</StatusChip>
      </header>
      <div className={`${cardCls} border-dashed`}>
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-007: هیچ endpoint فهرست/مدیریت سازمان‌ها وجود ندارد. این صفحه stub است.
        </p>
      </div>
      <EmptyState
        title="فهرست سازمان‌ها در دسترس نیست"
        description="منتظر افزودن endpoint سازمان‌ها در backend باشید."
      />
    </div>
  );
}
