import type { StatusTone } from "@pol/ui";

export type LoadState = "loading" | "error" | "ready";

export const cardCls = [
  "rounded-xl border border-[var(--pol-light-border-subtle)]",
  "bg-[var(--pol-light-surface-default)] p-4",
  "shadow-[var(--pol-shadow-card)]",
].join(" ");

export const linkCardCls = [
  cardCls,
  "transition-all duration-150 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-surface-subtle)]",
].join(" ");

export const inputCls = [
  "h-9 w-full rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3",
  "text-[13px] leading-[20px] text-[var(--pol-light-text-primary)]",
  "placeholder:text-[var(--pol-light-text-muted)]",
  "transition-[border-color,box-shadow] duration-150",
  "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] focus:border-transparent",
  "disabled:opacity-50 disabled:bg-[var(--pol-light-surface-subtle)]",
].join(" ");

export const orderStatusTone: Record<string, StatusTone> = {
  CREATED: "neutral",
  SUBMITTED: "info",
  ACCEPTED: "info",
  PARTIALLY_ACCEPTED: "warning",
  REJECTED: "danger",
  PREPARING: "info",
  READY: "info",
  DISPATCHED: "info",
  DELIVERED: "success",
  CANCELLED: "danger",
};

export const orderStatusLabel: Record<string, string> = {
  PENDING: "در انتظار پذیرش",
  PROCESSING: "در حال پردازش",
  CREATED: "ایجادشده",
  SUBMITTED: "ثبت‌شده",
  ACCEPTED: "پذیرفته‌شده",
  PARTIALLY_ACCEPTED: "پذیرش جزئی",
  REJECTED: "ردشده",
  PREPARING: "در حال آماده‌سازی",
  READY: "آماده ارسال",
  DISPATCHED: "ارسال‌شده",
  PICKED_UP: "جمع‌آوری‌شده",
  IN_TRANSIT: "در مسیر",
  ARRIVED: "رسیده به مقصد",
  DELIVERED: "تحویل‌شده",
  FAILED: "تحویل ناموفق",
  RETURNED: "مرجوع‌شده",
  CANCELLED: "لغوشده",
};

export const disputeStatusTone: Record<string, StatusTone> = {
  NONE: "neutral",
  OPEN: "danger",
  UNDER_REVIEW: "warning",
  RESOLVED_ADJUSTED: "success",
  RESOLVED_REJECTED: "success",
  CLOSED: "neutral",
};

export const disputeStatusLabel: Record<string, string> = {
  NONE: "بدون اختلاف",
  OPEN: "اختلاف باز",
  UNDER_REVIEW: "در حال بررسی",
  RESOLVED_ADJUSTED: "حل‌شده (تأثیرخورده)",
  RESOLVED_REJECTED: "حل‌شده (ردشده)",
  CLOSED: "بسته",
};

export const returnStatusLabel: Record<string, string> = {
  REQUESTED: "درخواست‌شده",
  PENDING: "در انتظار بررسی",
  APPROVED: "تأییدشده",
  REJECTED: "ردشده",
  RECEIVED: "دریافت‌شده",
  REFUNDED: "بازپرداخت‌شده",
  CANCELLED: "لغوشده",
};

export const supportStatusTone: Record<string, StatusTone> = {
  OPEN: "info",
  IN_PROGRESS: "warning",
  WAITING_ON_USER: "warning",
  RESOLVED: "success",
  CLOSED: "neutral",
};

export const supportStatusLabel: Record<string, string> = {
  OPEN: "باز",
  IN_PROGRESS: "در حال بررسی",
  WAITING_ON_USER: "در انتظار کاربر",
  RESOLVED: "حل‌شده",
  CLOSED: "بسته",
};

export const supportPriorityTone: Record<string, StatusTone> = {
  URGENT: "danger",
  HIGH: "warning",
  NORMAL: "info",
  LOW: "neutral",
};

export const supportPriorityLabel: Record<string, string> = {
  URGENT: "فوری",
  HIGH: "زیاد",
  NORMAL: "عادی",
  LOW: "کم",
};

export const supportTypeLabel: Record<string, string> = {
  GENERAL: "عمومی",
  ORDER_INQUIRY: "پیگیری سفارش",
  PAYMENT_ASSISTANCE: "کمک پرداخت",
  DELIVERY_DELAY: "تأخیر تحویل",
  ACCOUNT_ISSUE: "مشکل حساب",
  CATALOG_SUGGESTION: "پیشنهاد کاتالوگ",
  INVOICE_INQUIRY: "پیگیری فاکتور",
};

export const supportTransitions: Record<string, string[]> = {
  OPEN: ["IN_PROGRESS", "WAITING_ON_USER", "RESOLVED", "CLOSED"],
  IN_PROGRESS: ["WAITING_ON_USER", "RESOLVED", "CLOSED"],
  WAITING_ON_USER: ["IN_PROGRESS", "RESOLVED", "CLOSED"],
  RESOLVED: ["CLOSED", "IN_PROGRESS"],
  CLOSED: [],
};

export const reconStatusTone: Record<string, StatusTone> = {
  OPEN: "danger",
  MATCHED: "success",
  PARTIALLY_MATCHED: "warning",
  MISMATCH: "danger",
  RESOLVED: "success",
  CANCELLED: "neutral",
};

export const reconStatusLabel: Record<string, string> = {
  OPEN: "باز",
  MATCHED: "مطابق",
  PARTIALLY_MATCHED: "مطابق جزئی",
  MISMATCH: "عدم تطابق",
  RESOLVED: "تسویه‌شده",
  CANCELLED: "لغوشده",
};

export const notificationPriorityTone: Record<string, StatusTone> = {
  CRITICAL: "danger",
  HIGH: "warning",
  NORMAL: "info",
  LOW: "neutral",
};

export const notificationPriorityLabel: Record<string, string> = {
  CRITICAL: "بحرانی",
  HIGH: "زیاد",
  NORMAL: "عادی",
  LOW: "کم",
};


const OPERATIONAL_STATUS_LABELS: Record<string, string> = {
  PENDING: "در انتظار بررسی",
  ASSIGNED: "راننده تعیین‌شده",
  PICKED_UP: "جمع‌آوری‌شده",
  IN_TRANSIT: "در مسیر",
  OUT_FOR_DELIVERY: "در مسیر تحویل",
  ARRIVED: "رسیده به مقصد",
  FAILED: "تحویل ناموفق",
  RETURNED: "مرجوع‌شده",
  FULFILLED: "تکمیل‌شده",
  PARTIALLY_FULFILLED: "تکمیل جزئی",
  UNFULFILLED: "تکمیل‌نشده",
  PROPOSED: "پیشنهادشده",
  DECLINED: "ردشده",
  EXPIRED: "منقضی‌شده",
  MATCHED: "مطابق",
  PARTIALLY_MATCHED: "مطابق جزئی",
  MISMATCH: "عدم تطابق",
  ACTIVE: "فعال",
  COMPLETED: "تکمیل‌شده",
  PARTIALLY_COMPLETED: "تکمیل جزئی",
  DRAFT: "پیش‌نویس",
  START: "شروع",
  END: "پایان",
};

const DELIVERY_STATUS_LABELS: Record<string, string> = {
  PENDING: "در انتظار تخصیص",
  ASSIGNED: "راننده تعیین‌شده",
  PICKED_UP: "جمع‌آوری‌شده",
  IN_TRANSIT: "در مسیر",
  OUT_FOR_DELIVERY: "در مسیر تحویل",
  ARRIVED: "رسیده به مقصد",
  DELIVERED: "تحویل‌شده",
  FAILED: "تحویل ناموفق",
  RETURNED: "مرجوع‌شده",
  CANCELLED: "لغوشده",
  EXPIRED: "منقضی‌شده",
};

const FULFILLMENT_STATUS_LABELS: Record<string, string> = {
  PENDING: "در انتظار تکمیل",
  ACCEPTED: "پذیرفته‌شده",
  PARTIALLY_ACCEPTED: "پذیرش جزئی",
  FULFILLED: "تکمیل‌شده",
  PARTIALLY_FULFILLED: "تکمیل جزئی",
  UNFULFILLED: "تکمیل‌نشده",
  REJECTED: "ردشده",
  CANCELLED: "لغوشده",
};

const TIMELINE_EVENT_LABELS: Record<string, string> = {
  ORDER_CREATED: "سفارش ایجاد شد",
  ORDER_SUBMITTED: "سفارش ثبت شد",
  ORDER_ACCEPTED: "سفارش پذیرفته شد",
  ORDER_PARTIALLY_ACCEPTED: "پذیرش جزئی سفارش",
  ORDER_REJECTED: "سفارش رد شد",
  ORDER_CANCELLED: "سفارش لغو شد",
  ORDER_PREPARING: "آماده‌سازی سفارش آغاز شد",
  ORDER_READY: "سفارش آمادهٔ ارسال شد",
  ORDER_DISPATCHED: "سفارش ارسال شد",
  ORDER_DELIVERED: "سفارش تحویل شد",
  ORDER_PARTIAL_ACCEPTANCE_PROPOSED: "پیشنهاد پذیرش جزئی ثبت شد",
  ORDER_PARTIAL_ACCEPTANCE_APPROVED: "پیشنهاد پذیرش جزئی تأیید شد",
  ORDER_PARTIAL_ACCEPTANCE_DECLINED: "پیشنهاد پذیرش جزئی رد شد",
  DELIVERY_ASSIGNED: "راننده تعیین شد",
  DELIVERY_PICKED_UP: "کالا جمع‌آوری شد",
  DELIVERY_IN_TRANSIT: "محموله در مسیر است",
  DELIVERY_ARRIVED: "محموله به مقصد رسید",
  DELIVERY_COMPLETED: "تحویل ثبت شد",
  DELIVERY_FAILED: "تحویل ناموفق بود",
  PROOF_OF_DELIVERY_CREATED: "مدرک تحویل ثبت شد",
  DISPUTE_OPENED: "اختلاف ثبت شد",
  RETURN_REQUESTED: "درخواست مرجوعی ثبت شد",
  PAYMENT_RECEIPT_SUBMITTED: "رسید پرداخت ثبت شد",
  INVOICE_ISSUED: "فاکتور صادر شد",
  SUPPORT_CASE_CREATED: "درخواست پشتیبانی ثبت شد",
  SUPPORT_MESSAGE_SENT: "پیام پشتیبانی ثبت شد",
};

export function formatOperationalStatus(value: unknown, fallback = "—"): string {
  if (typeof value !== "string" || !value.trim()) return fallback;
  const status = value.trim();
  return orderStatusLabel[status]
    ?? disputeStatusLabel[status]
    ?? returnStatusLabel[status]
    ?? supportStatusLabel[status]
    ?? reconStatusLabel[status]
    ?? OPERATIONAL_STATUS_LABELS[status]
    ?? status.replace(/_/g, " ");
}

export function formatDeliveryStatus(value: unknown, fallback = "نامشخص"): string {
  if (typeof value !== "string" || !value.trim()) return fallback;
  const status = value.trim();
  return DELIVERY_STATUS_LABELS[status] ?? "وضعیت تحویل نامشخص";
}

export function formatFulfillmentStatus(value: unknown, fallback = "—"): string {
  if (typeof value !== "string" || !value.trim()) return fallback;
  const status = value.trim();
  return FULFILLMENT_STATUS_LABELS[status] ?? "وضعیت تکمیل نامشخص";
}

export function formatTimelineEventLabel(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) return "رویداد ثبت‌شده";
  const eventType = value.trim();
  return TIMELINE_EVENT_LABELS[eventType] ?? "رویداد ثبت‌شده";
}

export function formatDateTime(iso: unknown): string {
  if (typeof iso !== "string" || !iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("fa-IR", { dateStyle: "medium", timeStyle: "short" });
}

export function formatToman(value: unknown): string {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n)) return "—";
  return `${n.toLocaleString("fa-IR")} تومان`;
}

export function ageLabel(iso: unknown): string {
  if (typeof iso !== "string" || !iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const diffMs = Date.now() - d.getTime();
  if (diffMs < 0) return "—";
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "هم‌اکنون";
  if (minutes < 60) return `${minutes.toLocaleString("fa-IR")} دقیقه پیش`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours.toLocaleString("fa-IR")} ساعت پیش`;
  const days = Math.floor(hours / 24);
  return `${days.toLocaleString("fa-IR")} روز پیش`;
}

export function ageTone(iso: unknown, warnHours = 24, dangerHours = 72): StatusTone {
  if (typeof iso !== "string" || !iso) return "neutral";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "neutral";
  const hours = (Date.now() - d.getTime()) / 3600000;
  if (hours >= dangerHours) return "danger";
  if (hours >= warnHours) return "warning";
  return "info";
}

export function nextActionForOrder(status: unknown, dispute: unknown): string {
  if (typeof dispute === "string" && dispute !== "NONE" && dispute !== "CLOSED")
    return "بررسی اختلاف";
  switch (status) {
    case "CREATED":
    case "SUBMITTED":
      return "پیگیری پذیرش";
    case "PARTIALLY_ACCEPTED":
      return "بررسی پذیرش جزئی";
    case "REJECTED":
      return "بازبینی رد";
    case "PREPARING":
      return "پیگیری آماده‌سازی";
    case "READY":
      return "هماهنگی ارسال";
    case "DISPATCHED":
      return "پیگیری تحویل";
    case "CANCELLED":
      return "بستن پرونده";
    default:
      return "—";
  }
}

export function itemsOf<T>(raw: unknown, ...keys: string[]): T[] {
  if (Array.isArray(raw)) return raw as T[];
  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    for (const key of [...keys, "items", "data"]) {
      const hit = obj[key];
      if (Array.isArray(hit)) return hit as T[];
      if (hit && typeof hit === "object" && !Array.isArray(hit)) {
        const nested = hit as Record<string, unknown>;
        for (const k2 of [...keys, "items", "data"]) {
          if (Array.isArray(nested[k2])) return nested[k2] as T[];
        }
        if (Array.isArray(nested.data)) return nested.data as T[];
      }
    }
  }
  return [];
}

export function str(v: unknown, fallback = "—"): string {
  if (typeof v === "string" && v.trim() !== "") return v;
  if (typeof v === "number") return String(v);
  return fallback;
}

export function idOf(v: unknown): string {
  if (typeof v === "string") return v;
  if (typeof v === "number") return String(v);
  return "";
}
