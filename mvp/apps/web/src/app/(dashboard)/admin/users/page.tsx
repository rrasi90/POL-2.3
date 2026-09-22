import { EmptyState, StatusChip } from "@pol/ui";
import { cardCls } from "../../ops/_shared";

export default function AdminUsersPage() {
  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کاربران
        </h1>
        <StatusChip tone="warning">G-007</StatusChip>
      </header>
      <div className={`${cardCls} border-dashed`}>
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-007: هیچ GET/POST/PATCH/DELETE کاربران در API_MAP یا backend واقعی وجود ندارد.
          فهرست زیر stub است و هیچ عملیات موفق جعلی نشان نمی‌دهد.
        </p>
      </div>
      <EmptyState
        title="فهرست کاربران در دسترس نیست"
        description="منتظر افزودن endpoint کاربران در backend باشید."
      />
    </div>
  );
}
