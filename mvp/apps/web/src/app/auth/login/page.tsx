"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Field, ErrorState } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useAuthStore } from "@/lib/auth/store";
import type { Role } from "@pol/types";

interface OtpRequest {
  otp_request_id: string;
  expires_in_seconds: number;
  resend_interval_seconds: number;
}

interface VerifyResult {
  access_token: string;
  token_type?: string;
  expires_in?: number;
  user?: { user_id?: string; id?: string; mobile_number?: string };
  role?: Role | string;
  organization_id?: string;
  profile?: { role?: Role | string; organization_id?: string };
  current_organization?: { id?: string; role?: Role | string } | null;
}

function normalizeRole(raw: unknown): Role | null {
  const allowed: Role[] = [
    "ADMIN_SUPER",
    "OPS_AGENT",
    "FIELD_ACTIVATOR",
    "VENDOR_OWNER",
    "VENDOR_STAFF",
    "RETAILER_OWNER",
    "RETAILER_STAFF",
  ];
  if (typeof raw === "string" && (allowed as string[]).includes(raw)) return raw as Role;
  return null;
}

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState<string | null>(null);

  async function requestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await getApi().post<OtpRequest>("/api/v1/auth/request-otp", {
        mobile_number: phone,
      });
      setInfo(`کد ۴ رقمی تا ${data.expires_in_seconds} ثانیه معتبر است (ارسال مجدد هر ${data.resend_interval_seconds} ثانیه).`);
      setStep("otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : "ارسال کد ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function verifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (otp.length !== 4) {
      setError("کد باید ۴ رقمی باشد (D-018).");
      return;
    }
    setLoading(true);
    try {
      const data = await getApi().post<VerifyResult>("/api/v1/auth/verify-otp", {
        mobile_number: phone,
        otp_code: otp,
      });
      const role =
        normalizeRole(data.role) ??
        normalizeRole(data.profile?.role) ??
        normalizeRole(data.current_organization?.role) ??
        null;
      setSession({
        accessToken: data.access_token,
        user: {
          user_id: data.user?.user_id ?? data.user?.id ?? "",
          mobile_number: data.user?.mobile_number ?? phone,
          organization_id:
            data.organization_id ??
            data.profile?.organization_id ??
            data.current_organization?.id ??
            null,
        },
        role,
      });
      const home =
        role === "VENDOR_OWNER" || role === "VENDOR_STAFF"
          ? "/vendor"
          : role === "OPS_AGENT" || role === "ADMIN_SUPER"
            ? "/ops"
            : role === "FIELD_ACTIVATOR"
              ? "/field"
              : "/retailer";
      router.replace(home);
    } catch (err) {
      setError(err instanceof Error ? err.message : "کد نادرست است");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--pol-light-bg-canvas)] px-4">
      <div className="w-full max-w-sm rounded-[16px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-6 shadow-sm">
        <h1 className="text-[20px] leading-[28px] font-bold text-[var(--pol-light-text-primary)]">
          ورود به POL
        </h1>
        <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
          {step === "phone" ? "شماره موبایل خود را وارد کنید" : "کد چهاررقمی ارسال‌شده را وارد کنید"}
        </p>

        {error ? (
          <div className="mt-4">
            <ErrorState description={error} />
          </div>
        ) : null}
        {info && step === "otp" ? (
          <p className="mt-4 text-[12px] text-[var(--pol-light-semantic-info)]">{info}</p>
        ) : null}

        {step === "phone" ? (
          <form onSubmit={requestOtp} className="mt-5 flex flex-col gap-4">
            <Field
              label="شماره موبایل"
              inputMode="numeric"
              autoComplete="tel"
              placeholder="09xxxxxxxxx"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
              required
              hint="مثلاً ۰۹۱۲…"
            />
            <Button type="submit" loading={loading} block>
              ارسال کد
            </Button>
          </form>
        ) : (
          <form onSubmit={verifyOtp} className="mt-5 flex flex-col gap-4">
            <Field
              label="کد تأیید"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={4}
              placeholder="••••"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 4))}
              required
              hint="کد ۴ رقمی — TTL ۱۲۰ ثانیه"
            />
            <Button type="submit" loading={loading} block>
              تأیید و ورود
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => {
                setStep("phone");
                setOtp("");
                setError(null);
              }}
            >
              ویرایش شماره
            </Button>
          </form>
        )}
      </div>
    </main>
  );
}
