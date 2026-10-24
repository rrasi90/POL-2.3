"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button, ErrorState, Field } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { toE164 } from "@/lib/auth/phone";
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
  const sessionExpired = useAuthStore((s) => s.sessionExpired);
  const consumeSessionExpired = useAuthStore((s) => s.consumeSessionExpired);
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [mobile, setMobile] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    if (sessionExpired) {
      setError("نشست شما منقضی شده است. برای ادامه دوباره وارد شوید.");
      consumeSessionExpired();
    }
  }, [sessionExpired, consumeSessionExpired]);

  async function requestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const e164 = toE164(phone);
    if (!e164) {
      setError("شماره همراه معتبر نیست. نمونه: ۰۹۱۲۳۴۵۶۷۸۹");
      return;
    }
    setLoading(true);
    try {
      const data = await getApi().post<OtpRequest>("/api/v1/auth/request-otp", {
        mobile_number: e164,
      });
      setMobile(e164);
      setInfo(`کد ۶ رقمی تا ${data.expires_in_seconds.toLocaleString("fa-IR")} ثانیه دیگر معتبر است.`);
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
    if (otp.length !== 6) {
      setError("کد تأیید باید دقیقاً ۶ رقم باشد.");
      return;
    }
    setLoading(true);
    try {
      const data = await getApi().post<VerifyResult>("/api/v1/auth/verify-otp", {
        mobile_number: mobile,
        otp_code: otp,
        client_platform: "web",
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
          mobile_number: data.user?.mobile_number ?? mobile,
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
      setError(err instanceof Error ? err.message : "کد تأیید نادرست یا منقضی شده است");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-[var(--pol-light-bg-canvas)] px-4 py-12">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="mb-6 text-center">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-[var(--pol-light-brand-primary)] text-[20px] font-black text-white shadow-sm">
              پُ
            </span>
            <div className="text-start">
              <span className="block font-black text-[22px] tracking-tight text-[var(--pol-light-text-primary)]">
                پُــــل
              </span>
              <span className="block text-[11px] font-medium tracking-wide text-[var(--pol-light-text-muted)]">
                PRECISION COMMERCE
              </span>
            </div>
          </Link>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-8 shadow-[var(--pol-shadow-card)]">
          <h1 className="text-[20px] leading-[28px] font-bold text-[var(--pol-light-text-primary)]">
            {step === "phone" ? "ورود به سامانه معاملات عمده" : "تأیید شماره تلفن همراه"}
          </h1>
          <p className="mt-1.5 text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
            {step === "phone"
              ? "جهت ورود به حساب کاربری، شماره موبایل خود را وارد نمایید."
              : `کد شش‌رقمی پیامک‌شده به شماره ${mobile || phone} را وارد نمایید.`}
          </p>

          {error ? (
            <div className="mt-4">
              <ErrorState description={error} />
            </div>
          ) : null}

          {info && step === "otp" ? (
            <div className="mt-4 rounded-xl border border-[var(--pol-light-brand-primary)]/20 bg-[var(--pol-light-brand-primary)]/5 p-3 text-[12px] text-[var(--pol-light-brand-primary)]">
              {info}
            </div>
          ) : null}

          {step === "phone" ? (
            <form onSubmit={requestOtp} className="mt-6 flex flex-col gap-4">
              <Field
                label="شماره تلفن همراه"
                inputMode="numeric"
                autoComplete="tel"
                placeholder="۰۹۱۲۳۴۵۶۷۸۹"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
                required
                hint="شماره همراه ۱۱ رقمی معتبر"
                dir="ltr"
              />
              <div className="pt-2">
                <Button type="submit" loading={loading} block size="lg">
                  دریافت کد یکبار مصرف
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={verifyOtp} className="mt-6 flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                  کد تأیید ۶ رقمی
                </label>
                <input
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  placeholder="••••••"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  required
                  className="h-12 w-full rounded-xl border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-center font-mono text-[22px] font-bold tracking-[0.5em] text-[var(--pol-light-text-primary)] focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  dir="ltr"
                  autoFocus
                />
                <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                  اعتبار کد ۱۲۰ ثانیه می‌باشد (D-018)
                </span>
              </div>

              <div className="pt-2 flex flex-col gap-2">
                <Button type="submit" loading={loading} block size="lg">
                  تأیید و ورود به سامانه
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setStep("phone");
                    setOtp("");
                    setError(null);
                    setInfo(null);
                  }}
                >
                  ویرایش شماره همراه ({phone})
                </Button>
              </div>
            </form>
          )}

          <div className="mt-6 border-t border-[var(--pol-light-border-subtle)] pt-4 text-center">
            <span className="text-[11px] text-[var(--pol-light-text-muted)]">
              پایلوت اهواز · دسترسی بنکداران و تأمین‌کنندگان مواد غذایی
            </span>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-6 flex justify-center gap-4 text-[12px] text-[var(--pol-light-text-muted)]">
          <Link href="/how" className="hover:text-[var(--pol-light-text-primary)] hover:underline">
            راهنمای سامانه
          </Link>
          <span>·</span>
          <Link href="/legal" className="hover:text-[var(--pol-light-text-primary)] hover:underline">
            قوانین و حریم خصوصی
          </Link>
          <span>·</span>
          <Link href="/contact" className="hover:text-[var(--pol-light-text-primary)] hover:underline">
            پشتیبانی
          </Link>
        </div>
      </div>
    </main>
  );
}
