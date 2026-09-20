"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { LoginForm } from "@/components/auth/LoginForm";
import { OtpVerifyForm } from "@/components/auth/OtpVerifyForm";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/store";
import type { User } from "@/lib/types";

interface AuthTokens {
  user: User;
  access_token: string;
  refresh_token?: string;
}

const ROLE_REDIRECT: Record<string, string> = {
  ADMIN_SUPER: "/admin",
  OPS_AGENT: "/ops",
  FIELD_ACTIVATOR: "/field",
  VENDOR_OWNER: "/vendor",
  VENDOR_STAFF: "/vendor",
  RETAILER_OWNER: "/retailer",
  RETAILER_STAFF: "/retailer",
};

function getRedirectPath(role: string): string {
  return ROLE_REDIRECT[role] || "/";
}

export default function AuthPage() {
  const router = useRouter();
  const { setAuth, isAuthenticated, user } = useAuthStore();
  const [step, setStep] = useState<"login" | "verify">("login");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [retryAfter, setRetryAfter] = useState(0);
  const [lockoutMessage, setLockoutMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user) {
      router.replace(getRedirectPath(user.role));
    }
  }, [isAuthenticated, user, router]);

  useEffect(() => {
    if (retryAfter <= 0) return;
    const timer = setInterval(() => {
      setRetryAfter((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [retryAfter]);

  const handleRequestOtp = useCallback(
    async (phone: string) => {
      setLockoutMessage(null);
      setRetryAfter(0);
      try {
        await api.post("/api/v1/auth/request-otp", { mobile_number: phone });
        setPhoneNumber(phone);
        setStep("verify");
      } catch (err: any) {
        if (err.status === 429) {
          const retry = parseInt(err.details?.retry_after || "60", 10);
          setRetryAfter(retry);
          throw new Error("تعداد درخواست‌ها بیش از حد مجاز است. لطفاً صبر کنید.");
        }
        if (err.status === 423) {
          setLockoutMessage("حساب شما به دلیل تلاش‌های ناموفق قفل شده است. لطفاً بعداً تلاش کنید.");
          throw err;
        }
        throw err;
      }
    },
    [],
  );

  const handleVerifyOtp = useCallback(
    async (phone: string, code: string) => {
      const response = await api.post<AuthTokens>("/api/v1/auth/verify-otp", {
        mobile_number: phone,
        otp_code: code,
      });

      if (!response.access_token) {
        throw new Error("احراز هویت بدون توکن دسترسی انجام شد.");
      }

      setAuth(response.user, response.access_token, response.refresh_token);
      router.push(getRedirectPath(response.user.role));
    },
    [setAuth, router],
  );

  const handleBackToLogin = () => {
    setStep("login");
    setRetryAfter(0);
    setLockoutMessage(null);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-4" dir="rtl">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">پلتفرم POL</h1>
          <p className="text-sm text-gray-500 mt-1">بازار B2B FMCG</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {lockoutMessage && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 text-center">
              {lockoutMessage}
            </div>
          )}
          {retryAfter > 0 && !lockoutMessage && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700 text-center">
              لطفاً {retryAfter} ثانیه صبر کنید
            </div>
          )}
          {step === "login" ? (
            <LoginForm onLogin={handleRequestOtp} />
          ) : (
            <div>
              <button
                type="button"
                onClick={handleBackToLogin}
                className="mb-4 text-sm text-blue-600 hover:text-blue-800 transition-colors"
                disabled={retryAfter > 0}
              >
                &rarr; تغییر شماره
              </button>
              <OtpVerifyForm phoneNumber={phoneNumber} onVerify={handleVerifyOtp} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
