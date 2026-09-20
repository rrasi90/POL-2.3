"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface OtpVerifyFormProps {
  phoneNumber: string;
  onVerify: (phone: string, code: string) => Promise<void>;
}

export function OtpVerifyForm({ phoneNumber, onVerify }: OtpVerifyFormProps) {
  const [digits, setDigits] = useState<string[]>(["", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = useCallback(
    (index: number, value: string) => {
      const digit = value.replace(/\D/g, "").slice(-1);
      const next = [...digits];
      next[index] = digit;
      setDigits(next);
      setError(null);

      if (digit && index < 3) {
        inputRefs.current[index + 1]?.focus();
      }
    },
    [digits],
  );

  const handleKeyDown = useCallback(
    (index: number, e: React.KeyboardEvent) => {
      if (e.key === "Backspace" && !digits[index] && index > 0) {
        const next = [...digits];
        next[index - 1] = "";
        setDigits(next);
        inputRefs.current[index - 1]?.focus();
      }
    },
    [digits],
  );

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 4);
    if (pasted.length === 0) return;
    const next = ["", "", "", ""];
    for (let i = 0; i < pasted.length; i++) {
      next[i] = pasted[i];
    }
    setDigits(next);
    const focusIndex = Math.min(pasted.length, 3);
    inputRefs.current[focusIndex]?.focus();
  }, []);

  const code = digits.join("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length !== 4) return;
    setLoading(true);
    setError(null);
    try {
      await onVerify(phoneNumber, code);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در تایید کد");
    } finally {
      setLoading(false);
    }
  };

  const maskedPhone = phoneNumber.replace(/(\d{4})(\d{3})(\d{4})/, "$1***$3");

  return (
    <div className="w-full max-w-md mx-auto p-8">
      <h1 className="text-2xl font-bold text-center mb-2">تایید کد</h1>
      <p className="text-sm text-gray-500 text-center mb-8" dir="rtl">
        کد ۴ رقمی ارسال شده به {maskedPhone} را وارد کنید
      </p>
      <form onSubmit={handleSubmit} className="space-y-6" dir="rtl">
        <div className="flex justify-center gap-3" dir="ltr">
          {digits.map((digit, i) => (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              onPaste={handlePaste}
              className="w-14 h-14 text-center text-2xl font-mono border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              disabled={loading}
            />
          ))}
        </div>
        {error && (
          <p className="text-red-600 text-sm text-center" role="alert">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={loading || code.length !== 4}
          className="w-full py-2.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              در حال تایید...
            </span>
          ) : (
            "تایید"
          )}
        </button>
      </form>
    </div>
  );
}
