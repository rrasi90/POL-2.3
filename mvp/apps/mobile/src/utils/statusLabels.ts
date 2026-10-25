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


const NOTIFICATION_PRIORITY_LABELS: Readonly<Record<string, string>> = {
  CRITICAL: "بحرانی",
  HIGH: "زیاد",
  NORMAL: "عادی",
  LOW: "کم",
};

const SUPPORT_STATUS_LABELS: Readonly<Record<string, string>> = {
  OPEN: "باز",
  IN_PROGRESS: "در حال بررسی",
  WAITING_ON_USER: "در انتظار پاسخ شما",
  WAITING_ON_VENDOR: "در انتظار پاسخ بنکدار",
  WAITING_ON_OPS: "در انتظار بررسی عملیات",
  RESOLVED: "حل‌شده",
  CLOSED: "بسته",
  REOPENED: "دوباره بازشده",
};

const SUPPORT_TYPE_LABELS: Readonly<Record<string, string>> = {
  GENERAL: "درخواست عمومی",
  ORDER_INQUIRY: "پیگیری سفارش",
  PAYMENT_ASSISTANCE: "راهنمایی پرداخت",
  DELIVERY_DELAY: "تأخیر در تحویل",
  ACCOUNT_ISSUE: "مشکل حساب کاربری",
  CATALOG_SUGGESTION: "پیشنهاد اصلاح کاتالوگ",
  INVOICE_INQUIRY: "پیگیری فاکتور",
  RETURN_REQUEST: "درخواست مرجوعی",
  DISPUTE: "اختلاف در سفارش",
};

const RECONCILIATION_STATUS_LABELS: Readonly<Record<string, string>> = {
  OPEN: "باز",
  MATCHED: "مطابق",
  PARTIALLY_MATCHED: "مطابقت جزئی",
  MISMATCH: "عدم تطابق",
  RESOLVED: "رسیدگی‌شده",
  CANCELLED: "لغوشده",
};

const CANDIDATE_STATUS_LABELS: Readonly<Record<string, string>> = {
  PENDING_REVIEW: "در انتظار بررسی",
  APPROVED: "تأییدشده",
  REJECTED: "ردشده",
  MATCHED: "تطبیق‌یافته",
  MERGED: "ادغام‌شده",
  CANCELLED: "لغوشده",
};

const INVOICE_STATUS_LABELS: Readonly<Record<string, string>> = {
  DRAFT: "پیش‌نویس",
  ISSUED: "صادرشده",
  SENT: "ارسال‌شده",
  PENDING: "در انتظار پرداخت",
  PARTIALLY_PAID: "پرداخت جزئی",
  PAID: "پرداخت‌شده",
  OVERDUE: "سررسیدگذشته",
  VOID: "باطل‌شده",
  CANCELLED: "لغوشده",
};

const SETTLEMENT_STATUS_LABELS: Readonly<Record<string, string>> = {
  DRAFT: "پیش‌نویس",
  CALCULATED: "محاسبه‌شده",
  PENDING: "در انتظار تسویه",
  PROCESSING: "در حال پردازش",
  PARTIALLY_PAID: "پرداخت جزئی",
  PAID: "پرداخت‌شده",
  SETTLED: "تسویه‌شده",
  FAILED: "ناموفق",
  CANCELLED: "لغوشده",
};

const ROLE_LABELS: Readonly<Record<string, string>> = {
  ADMIN_SUPER: "مدیر سامانه",
  OPS_AGENT: "کارشناس عملیات",
  FIELD_ACTIVATOR: "کارشناس میدانی",
  VENDOR_OWNER: "مالک بنکداری",
  VENDOR_STAFF: "همکار بنکداری",
  RETAILER_OWNER: "مالک فروشگاه",
  RETAILER_STAFF: "همکار فروشگاه",
  DRIVER: "راننده",
  SUPPORT_AGENT: "کارشناس پشتیبانی",
};

const ORGANIZATION_STATUS_LABELS: Readonly<Record<string, string>> = {
  ACTIVE: "فعال",
  PENDING: "در انتظار تأیید",
  SUSPENDED: "تعلیق‌شده",
  BLOCKED: "مسدود",
  INACTIVE: "غیرفعال",
  CLOSED: "بسته",
};

const ORGANIZATION_TYPE_LABELS: Readonly<Record<string, string>> = {
  VENDOR: "بنکدار / تأمین‌کننده",
  RETAILER: "خرده‌فروش",
  PLATFORM: "سازمان پلتفرم",
  CARRIER: "حمل‌ونقل",
};

const PERMISSION_LABELS: Readonly<Record<string, string>> = {
  "catalog.view": "مشاهده کاتالوگ",
  "catalog.manage": "مدیریت کاتالوگ",
  "inventory.view": "مشاهده موجودی",
  "inventory.scan": "ثبت شمارش موجودی",
  "inventory.adjust": "اصلاح موجودی",
  "price.view": "مشاهده قیمت",
  "price.manage": "مدیریت قیمت",
  "order.view": "مشاهده سفارش",
  "order.fulfillment": "آماده‌سازی سفارش",
  "order.accept": "پذیرش سفارش",
  "order.reject": "رد سفارش",
  "delivery.dispatch": "ثبت ارسال",
  "delivery.confirm": "تأیید تحویل",
  "invoice.view": "مشاهده فاکتور",
  "settlement.view": "مشاهده تسویه",
  "staff.view": "مشاهده همکاران",
  "staff.manage": "مدیریت همکاران",
  "support.view": "مشاهده پشتیبانی",
  "support.manage": "مدیریت پشتیبانی",
};

const RETURN_ISSUE_LABELS: Readonly<Record<string, string>> = {
  DAMAGED: "کالای آسیب‌دیده",
  WRONG_ITEM: "کالای اشتباه",
  EXPIRED: "کالای تاریخ‌گذشته",
  MISSING_ITEM: "کسری کالا",
  QUALITY_ISSUE: "مشکل کیفیت",
  QUANTITY_MISMATCH: "مغایرت تعداد",
  OTHER: "سایر موارد",
};

function mappedLabel(
  value: string | null | undefined,
  labels: Readonly<Record<string, string>>,
  fallback = "وضعیت نامشخص",
): string {
  if (!value) return fallback;
  return labels[value] ?? fallback;
}

export function formatNotificationPriority(value: string | null | undefined): string {
  return mappedLabel(value, NOTIFICATION_PRIORITY_LABELS, "اولویت نامشخص");
}

export function formatSupportStatus(value: string | null | undefined): string {
  return mappedLabel(value, SUPPORT_STATUS_LABELS);
}

export function formatSupportPriority(value: string | null | undefined): string {
  return formatNotificationPriority(value);
}

export function formatSupportType(value: string | null | undefined): string {
  return mappedLabel(value, SUPPORT_TYPE_LABELS, "نوع درخواست دیگر");
}

export function formatReconciliationStatus(value: string | null | undefined): string {
  return mappedLabel(value, RECONCILIATION_STATUS_LABELS);
}

export function formatCandidateStatus(value: string | null | undefined): string {
  return mappedLabel(value, CANDIDATE_STATUS_LABELS, "وضعیت بررسی نامشخص");
}

export function formatInvoiceStatus(value: string | null | undefined): string {
  return mappedLabel(value, INVOICE_STATUS_LABELS, "وضعیت فاکتور نامشخص");
}

export function formatSettlementStatus(value: string | null | undefined): string {
  return mappedLabel(value, SETTLEMENT_STATUS_LABELS, "وضعیت تسویه نامشخص");
}

export function formatRole(value: string | null | undefined): string {
  return mappedLabel(value, ROLE_LABELS, "نقش دیگر");
}

export function formatOrganizationStatus(value: string | null | undefined): string {
  return mappedLabel(value, ORGANIZATION_STATUS_LABELS);
}

export function formatOrganizationType(value: string | null | undefined): string {
  return mappedLabel(value, ORGANIZATION_TYPE_LABELS, "نوع سازمان دیگر");
}

export function formatPermission(value: string | null | undefined): string {
  return mappedLabel(value, PERMISSION_LABELS, "مجوز دیگر");
}

export function formatGrantStatus(value: string | null | undefined): string {
  if (value === "GRANTED") return "اعطاشده";
  if (value === "REVOKED") return "لغوشده";
  return "وضعیت مجوز نامشخص";
}

export function formatReturnIssue(value: string | null | undefined): string {
  return mappedLabel(value, RETURN_ISSUE_LABELS, "علت دیگر");
}

export function formatOperationalStatus(value: string | null | undefined): string {
  if (!value) return "نامشخص";
  return (
    ORDER_STATUS_LABELS[value] ??
    DELIVERY_STATUS_LABELS[value] ??
    RETURN_STATUS_LABELS[value] ??
    SUPPORT_STATUS_LABELS[value] ??
    RECONCILIATION_STATUS_LABELS[value] ??
    CANDIDATE_STATUS_LABELS[value] ??
    INVOICE_STATUS_LABELS[value] ??
    SETTLEMENT_STATUS_LABELS[value] ??
    ORGANIZATION_STATUS_LABELS[value] ??
    "وضعیت نامشخص"
  );
}
