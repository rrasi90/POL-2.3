import assert from "node:assert/strict";

function toAsciiDigits(str) {
  if (!str) return "";
  return str
    .replace(/[۰-۹]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1728))
    .replace(/[٠-٩]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 1584));
}

function distributePastedOtp(rawText, startIndex, currentDigits, totalLength = 6) {
  const normalized = toAsciiDigits(rawText).replace(/\D/g, "");
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

console.log("Running mobile OTP paste & numeral normalization tests...");

// Test 1: Persian digits conversion
assert.equal(toAsciiDigits("۰۱۲۳۴۵۶۷۸۹"), "0123456789");
assert.equal(toAsciiDigits("۱۲۳۴۵۶"), "123456");

// Test 2: Arabic digits conversion
assert.equal(toAsciiDigits("٠١٢٣٤٥٦٧٨٩"), "0123456789");

// Test 3: Leading zero preservation
assert.equal(toAsciiDigits("۰۰۱۲۳۴"), "001234");
assert.equal(toAsciiDigits("۰۵۴۳۲۱"), "054321");

// Test 4: Pasting standard 6-digit OTP from cell 0
const pasteResult1 = distributePastedOtp("123456", 0, ["", "", "", "", "", ""]);
assert.deepEqual(pasteResult1.updatedDigits, ["1", "2", "3", "4", "5", "6"]);
assert.equal(pasteResult1.nextFocusIndex, 5);

// Test 5: Pasting Persian 6-digit OTP with leading zero from cell 0
const pasteResult2 = distributePastedOtp("۰۰۱۲۳۴", 0, ["", "", "", "", "", ""]);
assert.deepEqual(pasteResult2.updatedDigits, ["0", "0", "1", "2", "3", "4"]);
assert.equal(pasteResult2.nextFocusIndex, 5);

// Test 6: Pasting 6-digit OTP starting from cell 2 (should fill up to cell 5)
const pasteResult3 = distributePastedOtp("789012", 2, ["1", "2", "", "", "", ""]);
assert.deepEqual(pasteResult3.updatedDigits, ["1", "2", "7", "8", "9", "0"]);
assert.equal(pasteResult3.nextFocusIndex, 5);

// Test 7: Pasting with whitespace or symbols
const pasteResult4 = distributePastedOtp("  12-34 56  ", 0, ["", "", "", "", "", ""]);
assert.deepEqual(pasteResult4.updatedDigits, ["1", "2", "3", "4", "5", "6"]);

console.log("ALL MOBILE OTP TESTS PASSED SUCCESSFULLY (7/7 tests passed)");
