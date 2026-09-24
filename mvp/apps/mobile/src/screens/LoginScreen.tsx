import React, { useState } from "react";
import { StyleSheet, Text } from "react-native";
import { api, setToken } from "../api";
import { Btn, Card, ErrorBox, Input, Screen, Title } from "../components/ui";
import { spacing, useThemedStyles, type Palette } from "../theme";
import type { OtpRequest, Role, VerifyResult } from "../types";
import { normalizeRole } from "../types";

function toAsciiDigits(value: string): string {
  return value
    .replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String("٠١٢٣٤٥٦٧٨٩".indexOf(d)));
}

function toE164(value: string): string | null {
  const raw = toAsciiDigits(value).replace(/[\s()-]/g, "");
  if (/^09\d{9}$/.test(raw)) return "+98" + raw.slice(1);
  if (/^98\d{8,13}$/.test(raw)) return "+" + raw;
  if (/^\+[1-9]\d{7,14}$/.test(raw)) return raw;
  return null;
}

/** SH-AUTH-01/02 — 4-digit OTP login. Role comes only from the backend response. */
export function LoginScreen(props: { onAuthed: (role: Role) => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function requestOtp(): Promise<void> {
    setError(null);
    const mobileNumber = toE164(phone);
    if (!mobileNumber) {
      setError("شماره موبایل باید با فرمت E.164 باشد؛ مثال: +989161112233.");
      return;
    }
    setPhone(mobileNumber);
    setLoading(true);
    try {
      const data = await api.post<OtpRequest>("/api/v1/auth/request-otp", {
        mobile_number: mobileNumber,
      });
      setInfo(
        "کد ۴ رقمی تا " +
          data.expires_in_seconds +
          " ثانیه معتبر است؛ ارسال مجدد هر " +
          data.resend_interval_seconds +
          " ثانیه.",
      );
      setStep("otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : "ارسال کد ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function verifyOtp(): Promise<void> {
    setError(null);
    const mobileNumber = toE164(phone);
    if (!mobileNumber) {
      setError("شماره موبایل باید با فرمت E.164 باشد؛ مثال: +989161112233.");
      return;
    }
    if (otp.length !== 4) {
      setError("کد باید ۴ رقمی باشد (D-018).");
      return;
    }
    setLoading(true);
    try {
      const data = await api.post<VerifyResult>("/api/v1/auth/verify-otp", {
        mobile_number: mobileNumber,
        otp_code: otp,
      });
      const role = normalizeRole(data.current_organization?.role ?? data.role);
      if (!role) {
        setError("نقش کاربر از پاسخ معتبر بک‌اند قابل تعیین نیست.");
        return;
      }
      setToken(data.access_token);
      props.onAuthed(role);
    } catch (err) {
      setError(err instanceof Error ? err.message : "تأیید کد ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Title badge="SH-AUTH">ورود پُل</Title>
      <Card>
        <Text style={styles.sub}>OTP چهاررقمی (D-018) — بدون رمز عبور.</Text>
        <ErrorBox message={error} />
        {info && step === "otp" ? <Text style={styles.info}>{info}</Text> : null}

        {step === "phone" ? (
          <>
            <Input
              label="شماره موبایل"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              autoComplete="tel"
              placeholder="0916xxxxxxxx یا +98916xxxxxxxx"
            />
            <Btn label="ارسال کد" onPress={() => void requestOtp()} loading={loading} disabled={!phone.trim()} />
          </>
        ) : (
          <>
            <Input
              label="کد OTP"
              value={otp}
              onChangeText={(v) => setOtp(v.replace(/\D/g, ""))}
              keyboardType="number-pad"
              maxLength={4}
              autoComplete="one-time-code"
              hint="الگوی بک‌اند: ۴ رقم"
            />
            <Btn label="ورود" onPress={() => void verifyOtp()} loading={loading} disabled={otp.length !== 4} />
            <Btn label="بازگشت" tone="ghost" onPress={() => setStep("phone")} disabled={loading} />
          </>
        )}
      </Card>
    </Screen>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  sub: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.md, lineHeight: 20 },
  info: { fontSize: 12, color: colors.brand, marginBottom: spacing.sm, lineHeight: 18 },
  });
}
