export function toE164(raw: string): string | null {
  const digits = raw.replace(/\D/g, "");
  if (/^98\d{10}$/.test(digits)) return `+${digits}`;
  if (/^09\d{9}$/.test(digits)) return `+98${digits.slice(1)}`;
  if (/^9\d{9}$/.test(digits)) return `+98${digits}`;
  return null;
}
