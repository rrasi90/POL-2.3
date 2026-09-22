import type { StatusTone } from "@pol/ui";

export type LoadState = "loading" | "error" | "ready";

export const cardCls = [
  "rounded-[12px] border border-[var(--pol-light-border-subtle)]",
  "bg-[var(--pol-light-surface-default)] p-4",
].join(" ");

export const linkCardCls = [
  cardCls,
  "transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]",
].join(" ");

export const inputCls = [
  "h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3",
  "text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]",
  "placeholder:text-[var(--pol-light-text-muted)]",
  "transition-[border-color,box-shadow] duration-[160ms]",
  "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] focus:border-transparent",
  "disabled:opacity-50 disabled:bg-[var(--pol-light-surface-subtle)]",
].join(" ");

export const orderStatusTone: Record<string, StatusTone> = {
  CREATED: "warning",
  SUBMITTED: "warning",
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
  CREATED: "ایجادشده",
  SUBMITTED: "در انتظار پذیرش",
  ACCEPTED: "پذیرفته‌شده",
  PARTIALLY_ACCEPTED: "پذیرش جزئی",
  REJECTED: "ردشده",
  PREPARING: "در حال آماده‌سازی",
  READY: "آماده ارسال",
  DISPATCHED: "ارسال‌شده",
  DELIVERED: "تحویل‌شده",
  CANCELLED: "لغوشده",
};

export const disputeStatusLabel: Record<string, string> = {
  NONE: "بدون اختلاف",
  OPEN: "اختلاف باز",
  UNDER_REVIEW: "در حال بررسی",
  RESOLVED_ADJUSTED: "حل‌شده",
  RESOLVED_REJECTED: "حل‌شده (رد)",
  CLOSED: "بسته",
};

export const settlementStatusTone: Record<string, StatusTone> = {
  PENDING: "warning",
  PROCESSING: "info",
  PAID: "success",
  FAILED: "danger",
  CANCELLED: "neutral",
};

export const settlementStatusLabel: Record<string, string> = {
  PENDING: "در انتظار",
  PROCESSING: "در حال پردازش",
  PAID: "پرداخت‌شده",
  FAILED: "ناموفق",
  CANCELLED: "لغوشده",
};

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
  const minutes = Math.floor((Date.now() - d.getTime()) / 60000);
  if (minutes < 1) return "هم‌اکنون";
  if (minutes < 60) return `${minutes.toLocaleString("fa-IR")} دقیقه`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours.toLocaleString("fa-IR")} ساعت`;
  return `${Math.floor(hours / 24).toLocaleString("fa-IR")} روز`;
}

export function ageTone(iso: unknown, warnHours = 4, dangerHours = 12): StatusTone {
  if (typeof iso !== "string" || !iso) return "neutral";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "neutral";
  const hours = (Date.now() - d.getTime()) / 3600000;
  if (hours >= dangerHours) return "danger";
  if (hours >= warnHours) return "warning";
  return "info";
}

export function itemsOf<T>(raw: unknown, ...keys: string[]): T[] {
  if (Array.isArray(raw)) return raw as T[];
  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    for (const key of [...keys, "items", "data", "orders", "products", "rows"]) {
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

export function num(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

/** Acceptable vendor transitions for affordance gating (server remains authoritative). */
export function vendorCanAccept(status: unknown): boolean {
  return status === "CREATED" || status === "SUBMITTED";
}

export function vendorCanFulfill(status: unknown): boolean {
  return (
    status === "ACCEPTED" ||
    status === "PARTIALLY_ACCEPTED" ||
    status === "PREPARING" ||
    status === "READY" ||
    status === "DISPATCHED"
  );
}

export function fulfillmentLabel(status: unknown): string {
  switch (status) {
    case "ACCEPTED":
    case "PARTIALLY_ACCEPTED":
      return "شروع آماده‌سازی";
    case "PREPARING":
      return "علامت‌گذاری آماده";
    case "READY":
      return "ثبت ارسال";
    case "DISPATCHED":
      return "ثبت تحویل";
    default:
      return "";
  }
}
