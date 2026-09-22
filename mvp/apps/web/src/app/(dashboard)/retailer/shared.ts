import type { StatusTone } from "@pol/ui";

export const orderStatusTone: Record<string, StatusTone> = {
  PENDING: "warning",
  CREATED: "neutral",
  SUBMITTED: "info",
  ACCEPTED: "info",
  PARTIALLY_ACCEPTED: "warning",
  PROCESSING: "info",
  PREPARING: "info",
  READY: "info",
  DISPATCHED: "info",
  SHIPPED: "info",
  DELIVERED: "success",
  CANCELLED: "danger",
  REJECTED: "danger",
};

export const orderStatusLabel: Record<string, string> = {
  PENDING: "در انتظار پذیرش",
  CREATED: "ایجادشده",
  SUBMITTED: "ثبت‌شده",
  ACCEPTED: "پذیرفته‌شده",
  PARTIALLY_ACCEPTED: "پذیرش جزئی",
  PROCESSING: "در حال آماده‌سازی",
  PREPARING: "در حال آماده‌سازی",
  READY: "آماده ارسال",
  DISPATCHED: "ارسال‌شده",
  SHIPPED: "ارسال‌شده",
  DELIVERED: "تحویل‌شده",
  CANCELLED: "لغوشده",
  REJECTED: "ردشده",
};

export const groupStatusTone: Record<string, StatusTone> = {
  DRAFT: "neutral",
  ACTIVE: "info",
  COMPLETED: "success",
  PARTIALLY_COMPLETED: "warning",
  CANCELLED: "danger",
};

export const groupStatusLabel: Record<string, string> = {
  DRAFT: "پیش‌نویس",
  ACTIVE: "فعال",
  COMPLETED: "تکمیل‌شده",
  PARTIALLY_COMPLETED: "تکمیل جزئی",
  CANCELLED: "لغوشده",
};

export const disputeTone: Record<string, StatusTone> = {
  NONE: "neutral",
  OPEN: "danger",
  INVESTIGATING: "warning",
  RESOLVED: "success",
  CLOSED: "neutral",
};

export const disputeLabel: Record<string, string> = {
  NONE: "بدون اختلاف",
  OPEN: "اختلاف باز",
  INVESTIGATING: "در حال بررسی",
  RESOLVED: "اختلاف حل‌شده",
  CLOSED: "اختلاف بسته",
};

export const returnStatusTone: Record<string, StatusTone> = {
  REQUESTED: "info",
  PENDING: "warning",
  APPROVED: "success",
  REJECTED: "danger",
  RECEIVED: "info",
  REFUNDED: "success",
  CANCELLED: "neutral",
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

export const supportPriorityTone: Record<string, StatusTone> = {
  URGENT: "danger",
  HIGH: "warning",
  NORMAL: "info",
  LOW: "neutral",
};

export const supportStatusLabel: Record<string, string> = {
  OPEN: "باز",
  IN_PROGRESS: "در حال بررسی",
  WAITING_ON_USER: "در انتظار پاسخ شما",
  RESOLVED: "حل‌شده",
  CLOSED: "بسته",
};

const OPEN_ORDER_STATUSES = new Set(["PENDING", "ACCEPTED", "PROCESSING", "SHIPPED"]);

export function isOpenOrderStatus(status: unknown): boolean {
  return typeof status === "string" && OPEN_ORDER_STATUSES.has(status);
}

export function formatToman(value: unknown): string {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(n)) return "—";
  return `${n.toLocaleString("fa-IR")} تومان`;
}

export function formatDateTime(iso: unknown): string {
  if (typeof iso !== "string" || !iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("fa-IR", { dateStyle: "medium", timeStyle: "short" });
}

export interface OrderListItem {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | string | null;
  created_at?: string | null;
  updated_at?: string | null;
  vendor_id?: string | null;
  retailer_id?: string | null;
  order_group_id?: string | null;
  group_status?: string | null;
  vendor_name?: string | null;
}

export interface NormalizedOrderList {
  items: OrderListItem[];
  total: number | null;
  offset: number;
  limit: number;
}

/**
 * GET /orders success data may be {orders,limit,offset} (current backend),
 * {data,total,offset,limit} (API_MAP note), or a bare array.
 */
export function normalizeOrderList(raw: unknown, fallbackLimit = 50): NormalizedOrderList {
  if (Array.isArray(raw)) {
    return {
      items: raw as OrderListItem[],
      total: raw.length,
      offset: 0,
      limit: fallbackLimit,
    };
  }
  const obj = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  let items: unknown = obj.orders ?? obj.items ?? obj.data;
  if (items && typeof items === "object" && !Array.isArray(items)) {
    const nested = items as Record<string, unknown>;
    items = nested.orders ?? nested.items ?? (Array.isArray(nested.data) ? nested.data : []);
  }
  if (!Array.isArray(items)) items = [];
  const offset =
    typeof obj.offset === "number" && Number.isFinite(obj.offset) ? obj.offset : 0;
  const limit =
    typeof obj.limit === "number" && Number.isFinite(obj.limit) && obj.limit > 0
      ? obj.limit
      : fallbackLimit;
  const total =
    typeof obj.total === "number" && Number.isFinite(obj.total) ? obj.total : null;
  return { items: items as OrderListItem[], total, offset, limit };
}

export function asRecordArray(raw: unknown): Record<string, unknown>[] {
  if (Array.isArray(raw)) return raw as Record<string, unknown>[];
  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    if (Array.isArray(obj.data)) return obj.data as Record<string, unknown>[];
    if (Array.isArray(obj.items)) return obj.items as Record<string, unknown>[];
    if (Array.isArray(obj.returns)) return obj.returns as Record<string, unknown>[];
    if (Array.isArray(obj.disputes)) return obj.disputes as Record<string, unknown>[];
    if (Array.isArray(obj.events)) return obj.events as Record<string, unknown>[];
    if (Array.isArray(obj.orders)) return obj.orders as Record<string, unknown>[];
  }
  return [];
}
