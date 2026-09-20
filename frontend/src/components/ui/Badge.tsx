import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "success" | "warning" | "danger" | "info" | "gray" | "purple";
  size?: "sm" | "md";
}

const variants = {
  success: "bg-success-100 text-success-700",
  warning: "bg-warning-100 text-warning-700",
  danger: "bg-danger-100 text-danger-700",
  info: "bg-info-100 text-info-700",
  gray: "bg-gray-100 text-gray-700",
  purple: "bg-purple-100 text-purple-700",
};

const sizes = {
  sm: "px-2 py-0.5 text-[11px]",
  md: "px-2.5 py-1 text-xs",
};

export function Badge({ children, variant = "gray", size = "sm" }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full font-medium ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { variant: BadgeProps["variant"]; label: string }> = {
    CREATED: { variant: "info", label: "ایجاد شده" },
    SUBMITTED: { variant: "info", label: "ارسال شده" },
    ACCEPTED: { variant: "purple", label: "پذیرفته شده" },
    PARTIALLY_ACCEPTED: { variant: "purple", label: "پذیرش جزئی" },
    PREPARING: { variant: "warning", label: "آماده‌سازی" },
    DISPATCHED: { variant: "purple", label: "ارسال شده" },
    DELIVERED: { variant: "success", label: "تحویل شده" },
    CANCELLED: { variant: "danger", label: "لغو شده" },
    RETURN_REQUESTED: { variant: "warning", label: "درخواست برگشت" },
    DISPUTED: { variant: "danger", label: "مناقشه" },
    OPEN: { variant: "info", label: "باز" },
    IN_PROGRESS: { variant: "warning", label: "در حال انجام" },
    WAITING_ON_VENDOR: { variant: "warning", label: "در انتظار فروشنده" },
    WAITING_ON_USER: { variant: "warning", label: "در انتظار کاربر" },
    RESOLVED: { variant: "success", label: "حل شده" },
    CLOSED: { variant: "gray", label: "بسته شده" },
    ASSIGNED: { variant: "info", label: "تخصیص داده شده" },
    COMPLETED: { variant: "success", label: "تکمیل شده" },
    FAILED: { variant: "danger", label: "ناموفق" },
    PENDING: { variant: "warning", label: "در انتظار" },
    SETTLED: { variant: "success", label: "تسویه شده" },
    ACTIVE: { variant: "success", label: "فعال" },
    INACTIVE: { variant: "gray", label: "غیرفعال" },
    OUT_OF_STOCK: { variant: "danger", label: "ناموجود" },
  };
  const c = config[status] || { variant: "gray" as const, label: status };
  return <Badge variant={c.variant}>{c.label}</Badge>;
}

export function PriorityBadge({ priority }: { priority: string }) {
  const config: Record<string, { variant: BadgeProps["variant"]; label: string }> = {
    LOW: { variant: "gray", label: "پایین" },
    NORMAL: { variant: "info", label: "عادی" },
    HIGH: { variant: "warning", label: "بالا" },
    CRITICAL: { variant: "danger", label: "بحرانی" },
  };
  const c = config[priority] || { variant: "gray" as const, label: priority };
  return <Badge variant={c.variant}>{c.label}</Badge>;
}
