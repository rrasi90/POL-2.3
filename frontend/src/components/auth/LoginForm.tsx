"use client";

import { useState } from "react";

interface LoginFormProps {
  onLogin: (phoneNumber: string) => Promise<void>;
}

export function LoginForm({ onLogin }: LoginFormProps) {
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (value: string): string | null => {
    if (!value) return "شماره موبایل را وارد کنید";
    if (!/^\d+$/.test(value)) return "فقط عدد وارد کنید";
    if (value.length !== 11) return "شماره موبایل باید ۱۱ رقم باشد";
    if (!value.startsWith("09")) return "شماره موبایل باید با ۰۹ شروع شود";
    return null;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, "").slice(0, 11);
    setPhone(raw);
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validate(phone);
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await onLogin(phone);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در ارسال کد تایید");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-8">
      <h1 className="text-2xl font-bold text-center mb-2">ورود به سیستم</h1>
      <p className="text-sm text-gray-500 text-center mb-8">
        شماره موبایل خود را وارد کنید
      </p>
      <form onSubmit={handleSubmit} className="space-y-5" dir="rtl">
        <div>
          <label htmlFor="phone" className="block text-sm font-medium mb-1.5">
            شماره موبایل
          </label>
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center px-3 py-2 bg-gray-100 border border-r-0 border-gray-300 rounded-r-md text-sm text-gray-600 select-none">
              +98
            </span>
            <input
              id="phone"
              type="tel"
              inputMode="numeric"
              autoComplete="tel"
              dir="ltr"
              value={phone}
              onChange={handleChange}
              placeholder="09123456789"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-left placeholder:text-gray-400"
              disabled={loading}
              required
            />
          </div>
        </div>
        {error && (
          <p className="text-red-600 text-sm" role="alert">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              در حال ارسال...
            </span>
          ) : (
            "ارسال کد تایید"
          )}
        </button>
      </form>
    </div>
  );
}
