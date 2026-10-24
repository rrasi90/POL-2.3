/**
 * Mobile OTP utility functions
 * Normalizes Persian and Arabic numerals to ASCII digits and distributes pasted OTP across 6 cells.
 */

export function toAsciiDigits(str: string): string {
  if (!str) return '';
  return str
    .replace(/[۰-۹]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1728))
    .replace(/[٠-٩]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1584));
}

export function distributePastedOtp(
  rawText: string,
  startIndex: number,
  currentDigits: string[],
  totalLength: number = 6
): { updatedDigits: string[]; nextFocusIndex: number } {
  const normalized = toAsciiDigits(rawText).replace(/\D/g, '');
  if (!normalized) {
    return { updatedDigits: currentDigits, nextFocusIndex: startIndex };
  }

  const updated = [...currentDigits];
  let writeIdx = startIndex;

  for (let i = 0; i < normalized.length && writeIdx < totalLength; i++) {
    updated[writeIdx] = normalized[i];
    writeIdx++;
  }

  const nextFocusIndex = Math.min(writeIdx, totalLength - 1);
  return { updatedDigits: updated, nextFocusIndex };
}
