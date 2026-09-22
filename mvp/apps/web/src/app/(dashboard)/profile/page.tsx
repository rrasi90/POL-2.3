"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useAuthStore } from "@/lib/auth/store";
import type { ProfileContextResponse, ProfileUpdateRequest, UserProfileRecord } from "@pol/types";

const roleLabel: Record<string, string> = {
  ADMIN_SUPER: "مدیر ارشد",
  OPS_AGENT: "کارشناس عملیات",
  FIELD_ACTIVATOR: "فعال‌ساز میدانی",
  VENDOR_OWNER: "مالک تأمین‌کننده",
  VENDOR_STAFF: "کارمند تأمین‌کننده",
  RETAILER_OWNER: "مالک خرده‌فروشی",
  RETAILER_STAFF: "کارمند خرده‌فروشی",
};

interface FormState {
  display_name: string;
  email: string;
  preferred_language: string;
  timezone: string;
  bio: string;
}

type LoadState = "loading" | "error" | "ready";

const inputCls = [
  "h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3",
  "text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]",
  "placeholder:text-[var(--pol-light-text-muted)]",
  "transition-[border-color,box-shadow] duration-[160ms]",
  "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] focus:border-transparent",
  "disabled:opacity-50 disabled:bg-[var(--pol-light-surface-subtle)]",
].join(" ");

export default function ProfilePage() {
  const router = useRouter();
  const storeRole = useAuthStore((s) => s.role);
  const storeMobile = useAuthStore((s) => s.user?.mobile_number);
  const clear = useAuthStore((s) => s.clear);

  const [profile, setProfile] = useState<ProfileContextResponse | null>(null);
  const [context, setContext] = useState<ProfileContextResponse | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>({
    display_name: "",
    email: "",
    preferred_language: "fa-IR",
    timezone: "Asia/Tehran",
    bio: "",
  });
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const [p, c] = await Promise.all([
        getApi().get<ProfileContextResponse>("/api/v1/profile"),
        getApi().get<ProfileContextResponse>("/api/v1/profile/context"),
      ]);
      setProfile(p);
      setContext(c);
      setForm({
        display_name: p.user_profile.display_name ?? "",
        email: p.user_profile.email ?? "",
        preferred_language: p.user_profile.preferred_language ?? "fa-IR",
        timezone: p.user_profile.timezone ?? "Asia/Tehran",
        bio: p.user_profile.bio ?? "",
      });
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت حساب ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function update<K extends keyof FormState>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
    setFieldErrors((e) => ({ ...e, [key]: undefined }));
    setSaved(false);
  }

  function validate(): boolean {
    const errs: Partial<Record<keyof FormState, string>> = {};
    if (!form.display_name.trim()) errs.display_name = "نام نمایشی نمی‌تواند خالی باشد.";
    const email = form.email.trim();
    if (email && (email.length > 254 || !email.includes("@")))
      errs.email = "ایمیل معتبر وارد کنید.";
    if (!form.timezone.trim()) errs.timezone = "منطقه زمانی نمی‌تواند خالی باشد.";
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaveError(null);
    setSaved(false);
    if (!validate()) return;
    const email = form.email.trim();
    const body: ProfileUpdateRequest = {
      display_name: form.display_name.trim(),
      email: email === "" ? null : email,
      preferred_language: form.preferred_language,
      timezone: form.timezone.trim(),
      bio: form.bio.trim() === "" ? null : form.bio.trim(),
    };
    setSaving(true);
    try {
      await getApi().put<UserProfileRecord>("/api/v1/profile", body);
      await load();
      setSaved(true);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "ذخیره حساب ناموفق بود");
    } finally {
      setSaving(false);
    }
  }

  function logout() {
    clear();
    router.replace("/auth/login");
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری حساب">
        <Skeleton className="h-8 w-40" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={3} />
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت اطلاعات حساب ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const membership = context?.membership ?? profile?.membership ?? null;
  const user = profile?.user_profile;
  const mobile = user?.phone_number ?? storeMobile ?? "—";
  const role: string | null = membership?.role ?? storeRole;
  const organization = membership?.organization_name ?? membership?.organization_id ?? "—";

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          حساب کاربری
        </h1>
      </header>

      <section
        aria-label="اطلاعات حساب"
        className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <dl className="grid gap-4 sm:grid-cols-3">
          <div>
            <dt className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]">
              شماره موبایل
            </dt>
            <dd className="mt-1 text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]" dir="ltr">
              {mobile}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]">
              نقش
            </dt>
            <dd className="mt-1">
              <StatusChip tone="info">
                {role ? (roleLabel[role] ?? role) : "—"}
              </StatusChip>
            </dd>
          </div>
          <div>
            <dt className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]">
              سازمان
            </dt>
            <dd className="mt-1 text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]">
              {organization}
            </dd>
          </div>
        </dl>
      </section>

      <section aria-label="ویرایش پروفایل">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          پروفایل
        </h2>
        {saveError ? (
          <div className="mt-3">
            <ErrorState title="ذخیره ناموفق بود" description={saveError} />
          </div>
        ) : null}
        {saved ? (
          <p
            role="status"
            className="mt-3 text-[13px] leading-[20px] text-[var(--pol-light-semantic-success)]"
          >
            تغییرات ذخیره شد.
          </p>
        ) : null}

        <form onSubmit={save} className="mt-4 grid max-w-2xl gap-4">
          <Field
            label="نام نمایشی"
            value={form.display_name}
            onChange={(e) => update("display_name", e.target.value)}
            error={fieldErrors.display_name}
            required
            maxLength={120}
            autoComplete="name"
          />
          <Field
            label="ایمیل"
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            error={fieldErrors.email}
            hint="اختیاری"
            autoComplete="email"
            dir="ltr"
          />
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="profile-language"
              className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              زبان ترجیحی
            </label>
            <select
              id="profile-language"
              value={form.preferred_language}
              onChange={(e) => update("preferred_language", e.target.value)}
              className={inputCls}
            >
              <option value="fa-IR">فارسی (fa-IR)</option>
              <option value="en-US">English (en-US)</option>
            </select>
          </div>
          <Field
            label="منطقه زمانی"
            value={form.timezone}
            onChange={(e) => update("timezone", e.target.value)}
            error={fieldErrors.timezone}
            hint="IANA — مثلاً Asia/Tehran"
            dir="ltr"
          />
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="profile-bio"
              className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              درباره من
            </label>
            <textarea
              id="profile-bio"
              value={form.bio}
              onChange={(e) => update("bio", e.target.value)}
              maxLength={500}
              rows={3}
              className={[
                inputCls,
                "h-auto min-h-[88px] py-2 resize-y",
              ].join(" ")}
              placeholder="اختیاری — حداکثر ۵۰۰ نویسه"
            />
            <p className="text-[11px] leading-[16px] text-[var(--pol-light-text-muted)]">
              {form.bio.length}/500
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" loading={saving}>
              ذخیره تغییرات
            </Button>
            <Button variant="ghost" onClick={() => void load()} disabled={saving}>
              انصراف از تغییرات
            </Button>
          </div>
        </form>
      </section>

      <section aria-label="خروج از حساب" className="border-t border-[var(--pol-light-border-subtle)] pt-4">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          خروج
        </h2>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          برای خروج از این دستگاه، دکمه زیر را بزنید.
        </p>
        <div className="mt-3">
          <Button variant="danger" onClick={logout}>
            خروج از حساب
          </Button>
        </div>
      </section>
    </div>
  );
}
