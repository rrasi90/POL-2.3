import React, { useState } from "react";
import { api, setToken } from "../api";
import { Btn, Card, ErrorBox, Input, Screen, Title } from "../components/ui";
import { colors, spacing } from "../theme";
import type { OtpRequest, VerifyResult } from "../types";
import { StyleSheet, Text } from "react-native";

/** SH-AUTH OTP login — 4-digit code (D-018). */
export function LoginScreen(props: { onAuthed: () => void }): React.ReactNode {
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function requestOtp(): Promise<void> {
    setError(null);
    setLoading(true);
    try {
      const data = await api.post<OtpRequest>("/api/v1/auth/request-otp", {
        mobile_number: phone,
      });
      setInfo(
        `کد ۴ رقمی تا ${data.expires_in_seconds} ثانیه معتبر است (ارسال مجدد هر ${data.resend_interval_seconds} ثانیه).`,
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
    if (otp.length !== 4) {
      setError("کد باید ۴ رقمی باشد (D-018).");
      return;
    }
    setLoading(true);
    try {
      const data = await api.post<VerifyResult>("/api/v1/auth/verify-otp", {
        mobile_number: phone,
        otp_code: otp,
      });
      setToken(data.access_token);
      props.onAuthed();
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
              placeholder="09xxxxxxxxx"
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

const styles = StyleSheet.create({
  sub: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.md, lineHeight: 20 },
  info: { fontSize: 12, color: colors.brand, marginBottom: spacing.sm, lineHeight: 18 },
});
