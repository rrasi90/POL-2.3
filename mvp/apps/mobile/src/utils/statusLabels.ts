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

const DELIVERY_STATUS_LABELS: Readonly<Record<string, string>> = {
  PENDING: "در انتظار تخصیص",
  ASSIGNED: "راننده تخصیص داده‌شده",
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

const RETURN_STATUS_LABELS: Readonly<Record<string, string>> = {
  REQUESTED: "درخواست ثبت‌شده",
  PENDING: "در انتظار بررسی",
  APPROVED: "تأییدشده",
  REJECTED: "ردشده",
  RECEIVED: "دریافت‌شده",
  REFUNDED: "بازپرداخت‌شده",
  CANCELLED: "لغوشده",
  OPEN: "باز",
  INVESTIGATING: "در حال بررسی",
  UNDER_REVIEW: "در حال بررسی",
  RESOLVED: "حل‌شده",
  CLOSED: "بسته",
};

const TIMELINE_EVENT_LABELS: Readonly<Record<string, string>> = {
  ORDER_CREATED: "سفارش ایجاد شد",
  ORDER_SUBMITTED: "سفارش ثبت شد",
  ORDER_ACCEPTED: "سفارش پذیرفته شد",
  ORDER_PARTIALLY_ACCEPTED: "سفارش با پذیرش جزئی تأیید شد",
  ORDER_REJECTED: "سفارش رد شد",
  ORDER_PREPARING: "آماده‌سازی سفارش آغاز شد",
  ORDER_READY: "سفارش آمادهٔ ارسال شد",
  ORDER_DISPATCHED: "سفارش ارسال شد",
  DELIVERY_OTP_GENERATED: "کد تأیید تحویل ایجاد شد",
  DELIVERY_PICKED_UP: "کالا جمع‌آوری شد",
  DELIVERY_IN_TRANSIT: "محموله در مسیر است",
  DELIVERY_ARRIVED: "محموله به مقصد رسید",
  DELIVERY_COMPLETED: "تحویل ثبت شد",
  DELIVERY_FAILED: "تحویل ناموفق بود",
  RETURN_REQUESTED: "درخواست مرجوعی ثبت شد",
  DISPUTE_OPENED: "اختلاف ثبت شد",
  PAYMENT_RECEIPT_SUBMITTED: "رسید پرداخت ثبت شد",
};

export function formatDeliveryStatus(status: string | null | undefined): string {
  if (!status) return "نامشخص";
  return DELIVERY_STATUS_LABELS[status] ?? "وضعیت تحویل نامشخص";
}

export function formatReturnStatus(status: string | null | undefined): string {
  if (!status) return "نامشخص";
  return RETURN_STATUS_LABELS[status] ?? "وضعیت نامشخص";
}

export function formatTimelineEvent(eventType: string | null | undefined): string {
  if (!eventType) return "رویداد سفارش";
  return TIMELINE_EVENT_LABELS[eventType] ?? "رویداد ثبت‌شده";
}
