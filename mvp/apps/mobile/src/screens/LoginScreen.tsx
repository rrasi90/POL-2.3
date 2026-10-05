import React, { useRef, useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { api, persistSession } from "../api";
import { Btn, Card, ErrorBox, Screen } from "../components/ui";
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

/** SH-AUTH-01/02 — same authentication contract, reference-matched presentation. */
export function LoginScreen(props: { onAuthed: (role: Role) => void; allowedRoles?: readonly Role[]; appName?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [digits, setDigits] = useState(["", "", "", ""]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const refs = [useRef<TextInput>(null), useRef<TextInput>(null), useRef<TextInput>(null), useRef<TextInput>(null)];

  async function requestOtp(): Promise<void> {
    setError(null);
    const mobileNumber = toE164(phone);
    if (!mobileNumber) {
      setError("شماره موبایل را با فرمت ۰۹۱۶xxxxxxxx وارد کنید.");
      return;
    }
    setPhone(mobileNumber);
    setLoading(true);
    try {
      const data = await api.post<OtpRequest>("/api/v1/auth/request-otp", { mobile_number: mobileNumber });
      setInfo("کد ۴ رقمی تا " + data.expires_in_seconds + " ثانیه معتبر است.");
      setDigits(["", "", "", ""]);
      setOtp("");
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
      setError("شماره موبایل معتبر نیست.");
      return;
    }
    if (otp.length !== 4) {
      setError("کد باید ۴ رقمی باشد.");
      return;
    }
    setLoading(true);
    try {
      const data = await api.post<VerifyResult>("/api/v1/auth/verify-otp", {
        mobile_number: mobileNumber,
        otp_code: otp,
        client_platform: "mobile",
      });
      const role = normalizeRole(data.current_organization?.role ?? data.role);
      if (!role) {
        setError("نقش کاربر از پاسخ معتبر بک‌اند قابل تعیین نیست.");
        return;
      }
      if (props.allowedRoles && !props.allowedRoles.includes(role)) {
        setError(props.appName === "پل بنکدار" ? "این حساب برای اپلیکیشن بنکدار مجاز نیست." : "این حساب برای این اپلیکیشن مجاز نیست.");
        return;
      }
      await persistSession(data.access_token, data.refresh_token ?? null, role);
      props.onAuthed(role);
    } catch (err) {
      setError(err instanceof Error ? err.message : "تأیید کد ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  function updateDigit(index: number, value: string): void {
    const clean = toAsciiDigits(value).replace(/\D/g, "").slice(-1);
    const next = [...digits];
    next[index] = clean;
    setDigits(next);
    const joined = next.join("");
    setOtp(joined);
    if (clean && index < 3) refs[index + 1].current?.focus();
  }

  return (
    <Screen>
      <View style={styles.wrap}>
        <View style={styles.logoWrap}>
          <View style={styles.logo}><Text style={styles.logoText}>پل</Text></View>
          <Text style={styles.wordmark}>پل</Text>
          <Text style={styles.tagline}>خرید عمده، ساده‌تر از همیشه</Text>
        </View>

        <View style={styles.progress}>
          <View style={[styles.progressDot, styles.progressActive]} />
          <View style={[styles.progressLine, step === "otp" && styles.progressActiveLine]} />
          <View style={[styles.progressDot, step === "otp" && styles.progressActive]} />
        </View>

        <Card style={styles.loginCard}>
          {step === "phone" ? (
            <>
              <Text style={styles.title}>ورود به حساب کاربری</Text>
              <Text style={styles.sub}>شماره موبایل خود را وارد کنید تا وارد بازار عمده‌فروشی پل شوید.</Text>
              <ErrorBox message={error} />
              <View style={styles.phoneField}>
                <Text style={styles.countryPrefix}>+۹۸</Text>
                <TextInput
                  value={phone}
                  onChangeText={setPhone}
                  keyboardType="phone-pad"
                  autoComplete="tel"
                  placeholder="۹۱۶ ۱۱۱ ۲۲۳۳"
                  placeholderTextColor={styles.placeholder.color}
                  style={styles.phoneInput}
                />
              </View>
              <Btn label="دریافت کد" onPress={() => void requestOtp()} loading={loading} disabled={!phone.trim()} />
              <Text style={styles.footnote}>با ورود، قوانین و حریم خصوصی پل را می‌پذیرید.</Text>
            </>
          ) : (
            <>
              <Text style={styles.title}>تأیید کد</Text>
              <Text style={styles.sub}>کد ۴ رقمی ارسال‌شده به {phone} را وارد کنید.</Text>
              {info ? <Text style={styles.info}>{info}</Text> : null}
              <ErrorBox message={error} />
              <View style={styles.otpRow}>
                {digits.map((digit, index) => (
                  <TextInput
                    key={index}
                    ref={refs[index]}
                    value={digit}
                    onChangeText={(value) => updateDigit(index, value)}
                    onKeyPress={(event) => {
                      if (event.nativeEvent.key === "Backspace" && !digits[index] && index > 0) refs[index - 1].current?.focus();
                    }}
                    keyboardType="number-pad"
                    maxLength={1}
                    style={styles.otpCell}
                    textAlign="center"
                    selectTextOnFocus
                  />
                ))}
              </View>
              <Btn label="تأیید و ورود" onPress={() => void verifyOtp()} loading={loading} disabled={otp.length !== 4} />
              <Pressable onPress={() => { setStep("phone"); setError(null); }} disabled={loading} style={styles.changePhone}>
                <Text style={styles.changePhoneText}>تغییر شماره موبایل</Text>
              </Pressable>
            </>
          )}
        </Card>

        <View style={styles.featureRow}>
          <Feature icon="⚡" title="قیمت‌های عمده" />
          <Feature icon="🚚" title="تحویل سریع" />
          <Feature icon="🛡️" title="خرید مطمئن" />
        </View>
      </View>
    </Screen>
  );
}

function Feature(props: { icon: string; title: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <View style={styles.feature}><Text style={styles.featureIcon}>{props.icon}</Text><Text style={styles.featureText}>{props.title}</Text></View>;
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    wrap: { flex: 1, justifyContent: "center", paddingVertical: spacing.xl },
    logoWrap: { alignItems: "center", marginBottom: spacing.xl },
    logo: { width: 82, height: 82, borderRadius: 26, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center", shadowColor: colors.brand, shadowOpacity: 0.22, shadowRadius: 14, elevation: 4 },
    logoText: { color: "#fff", fontSize: 40, fontWeight: "900" },
    wordmark: { color: colors.text, fontSize: 30, fontWeight: "900", marginTop: 10 },
    tagline: { color: colors.textSecondary, fontSize: 12, marginTop: 3 },
    progress: { flexDirection: "row", alignItems: "center", justifyContent: "center", marginBottom: spacing.lg },
    progressDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.border },
    progressActive: { backgroundColor: colors.brand },
    progressLine: { width: 44, height: 2, backgroundColor: colors.border, marginHorizontal: 6 },
    progressActiveLine: { backgroundColor: colors.brand },
    loginCard: { padding: spacing.xl, borderRadius: 22 },
    title: { color: colors.text, fontSize: 21, fontWeight: "900", textAlign: "right", marginBottom: 7 },
    sub: { color: colors.textSecondary, fontSize: 13, lineHeight: 21, textAlign: "right", marginBottom: spacing.lg },
    phoneField: { flexDirection: "row", alignItems: "center", borderWidth: 1, borderColor: colors.border, borderRadius: 14, minHeight: 52, marginBottom: spacing.md, backgroundColor: colors.surface },
    countryPrefix: { color: colors.textSecondary, fontSize: 13, fontWeight: "800", paddingHorizontal: 13 },
    phoneInput: { flex: 1, color: colors.text, fontSize: 16, paddingVertical: 12, textAlign: "right", writingDirection: "ltr" },
    placeholder: { color: colors.textMuted },
    footnote: { color: colors.textMuted, fontSize: 10, lineHeight: 16, textAlign: "center", marginTop: spacing.md },
    info: { color: colors.brand, fontSize: 12, textAlign: "center", marginBottom: spacing.md },
    otpRow: { flexDirection: "row", justifyContent: "center", gap: spacing.sm, marginBottom: spacing.lg, direction: "ltr" },
    otpCell: { width: 54, height: 58, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.surface, color: colors.text, fontSize: 22, fontWeight: "900" },
    changePhone: { marginTop: spacing.md, alignItems: "center" },
    changePhoneText: { color: colors.brand, fontSize: 12, fontWeight: "700" },
    featureRow: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
    feature: { flex: 1, minHeight: 72, alignItems: "center", justifyContent: "center", backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: 16 },
    featureIcon: { fontSize: 18 },
    featureText: { color: colors.textSecondary, fontSize: 10, fontWeight: "700", marginTop: 5 },
  });
}
