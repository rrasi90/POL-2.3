const ORDER_STATUS_LABELS: Readonly<Record<string, string>> = {
  CREATED: "ایجادشده",
  SUBMITTED: "ثبت‌شده",
  PENDING: "در انتظار پذیرش",
  ACCEPTED: "پذیرفته‌شده",
  PARTIALLY_ACCEPTED: "پذیرش جزئی",
  REJECTED: "ردشده",
  PROCESSING: "در حال پردازش",
  PREPARING: "در حال آماده‌سازی",
  READY: "آمادهٔ ارسال",
  DISPATCHED: "ارسال‌شده",
  PICKED_UP: "جمع‌آوری‌شده",
  IN_TRANSIT: "در مسیر",
  ARRIVED: "رسیده به مقصد",
  DELIVERED: "تحویل‌شده",
  FAILED: "تحویل ناموفق",
  RETURNED: "مرجوع‌شده",
  CANCELLED: "لغوشده",
};

export function formatOrderStatus(status: string | null | undefined): string {
  if (!status) return "نامشخص";
  return ORDER_STATUS_LABELS[status] ?? "وضعیت نامشخص";
}

export function formatDeliveryStatus(status: string | null | undefined): string {
  return formatOrderStatus(status);
}
