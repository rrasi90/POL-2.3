/**
 * Normalizes Persian and Arabic numerals to ASCII digits.
 */
export function toAsciiDigits(str: string): string {
  if (!str) return '';
  return str
    .replace(/[۰-۹]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1728))
    .replace(/[٠-٩]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1584));
}

export function toE164(raw: string): string | null {
  const digits = toAsciiDigits(raw).replace(/\D/g, "");
  if (/^98\d{10}$/.test(digits)) return `+${digits}`;
  if (/^09\d{9}$/.test(digits)) return `+98${digits.slice(1)}`;
  if (/^9\d{9}$/.test(digits)) return `+98${digits}`;
  return null;
}
