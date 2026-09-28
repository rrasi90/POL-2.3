const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";

export function toPersianDigits(value: string): string {
  return value
    .replace(/[0-9]/g, (d) => PERSIAN_DIGITS[Number(d)])
    .replace(/[٠-٩]/g, (d) => PERSIAN_DIGITS[ARABIC_DIGITS.indexOf(d)]);
}

export function formatFaNumber(
  value: number | string | null | undefined,
  maximumFractionDigits = 3,
): string {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "—";
  try {
    return new Intl.NumberFormat("fa-IR-u-nu-arabext", {
      maximumFractionDigits,
      useGrouping: true,
    }).format(numeric);
  } catch {
    return toPersianDigits(
      numeric.toLocaleString("en-US", {
        maximumFractionDigits,
        useGrouping: true,
      }),
    );
  }
}

export function formatToman(value: number | string | null | undefined): string {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "—";
  return `${formatFaNumber(numeric, 0)} تومان`;
}

export function formatTehranDateTime(value: string | Date | null | undefined): string {
  if (!value) return "—";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  try {
    return new Intl.DateTimeFormat("fa-IR-u-ca-persian-u-nu-arabext", {
      timeZone: "Asia/Tehran",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return new Intl.DateTimeFormat("fa-IR", {
      timeZone: "Asia/Tehran",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }
}

export function todayTehranIso(): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tehran",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${byType.year}-${byType.month}-${byType.day}`;
}
