import React, { useCallback, useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { api, clearSession } from "../api";
import { Btn, Card, Empty, ErrorBox, IconBadge, Input, StatusChip, Screen } from "../components/ui";
import type { Role } from "../types";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { formatNotificationPriority } from "../utils/statusLabels";
import { formatTehranDateTime } from "../i18n/fa";

type Profile = {
  user_profile?: { user_id?: string; display_name?: string | null; email?: string | null; preferred_language?: string | null; timezone?: string | null; bio?: string | null; phone_number?: string | null };
  membership?: { organization_id?: string; organization_name?: string | null; role?: string | null } | null;
};
type NotificationPreference = { category: string; push_enabled: boolean; sms_enabled: boolean };
type Preferences = NotificationPreference[];
type Notification = { id: string; event_name?: string | null; title?: string | null; body?: string | null; priority?: string | null; created_at?: string | null; read?: boolean; is_read?: boolean };

function notificationsOf(data: unknown): Notification[] {
  if (Array.isArray(data)) return data as Notification[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of ["items", "notifications", "data", "results"]) if (Array.isArray(o[k])) return o[k] as Notification[];
  return [];
}

export function AccountMobileScreen(props: { role: Role; onBack?: () => void; onLogout?: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { mode, setMode } = useTheme();
  const [view, setView] = useState<"profile" | "notifications" | "preferences">("profile");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<Preferences>({});
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [timezone, setTimezone] = useState("Asia/Tehran");
  const [bio, setBio] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadProfile = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [p, c] = await Promise.all([api.get<Profile>("/api/v1/profile"), api.get<Profile>("/api/v1/profile/context")]);
      const merged: Profile = { user_profile: p.user_profile, membership: c.membership ?? p.membership ?? null };
      setProfile(merged);
      setDisplayName(merged.user_profile?.display_name || "");
      setEmail(merged.user_profile?.email || "");
      setTimezone(merged.user_profile?.timezone || "Asia/Tehran");
      setBio(merged.user_profile?.bio || "");
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت حساب ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  const loadPreferences = useCallback(async () => {
    setLoading(true); setError(null);
    try { const d = await api.get<unknown>("/api/v1/notifications/preferences"); setPreferences(Array.isArray(d) ? d as NotificationPreference[] : []); }
    catch (e) { setError(e instanceof Error ? e.message : "دریافت تنظیمات اعلان ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  const loadNotifications = useCallback(async () => {
    setLoading(true); setError(null);
    try { const d = await api.get<unknown>("/api/v1/notifications?limit=50&offset=0"); setNotifications(notificationsOf(d)); }
    catch (e) { setError(e instanceof Error ? e.message : "دریافت اعلان‌ها ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    void (view === "profile" ? loadProfile() : view === "notifications" ? loadNotifications() : loadPreferences());
  }, [view, loadProfile, loadNotifications, loadPreferences]);

  async function savePreferences(): Promise<void> {
    setLoading(true); setError(null); setNotice(null);
    try {
      for (const preference of preferences) {
        await api.put("/api/v1/notifications/preferences", { event_name: preference.category, channel: "PUSH", is_enabled: Boolean(preference.push_enabled) });
        await api.put("/api/v1/notifications/preferences", { event_name: preference.category, channel: "SMS", is_enabled: Boolean(preference.sms_enabled) });
      }
      setNotice("تنظیمات اعلان ذخیره شد.");
      await loadPreferences();
    } catch (e) {
      try {
        const latest = await api.get<unknown>("/api/v1/notifications/preferences");
        setPreferences(Array.isArray(latest) ? latest as NotificationPreference[] : []);
      } catch { /* Keep the current values visible if the recovery read also fails. */ }
      setError(e instanceof Error ? e.message : "ذخیره تنظیمات اعلان ناموفق بود");
    }
    finally { setLoading(false); }
  }

  async function saveProfile(): Promise<void> {
    if (!displayName.trim()) { setError("نام نمایشی الزامی است."); return; }
    setLoading(true); setError(null); setNotice(null);
    try {
      await api.put("/api/v1/profile", { display_name: displayName.trim(), email: email.trim() ? email.trim() : null, preferred_language: "fa-IR", timezone: timezone.trim(), bio: bio.trim() ? bio.trim() : null });
      await loadProfile();
      setNotice("حساب ذخیره شد.");
    } catch (e) { setError(e instanceof Error ? e.message : "ذخیره حساب ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function logout(): Promise<void> {
    setLoading(true); setError(null); setNotice(null);
    try { await api.delete("/api/v1/auth/sessions/current"); await clearSession(); props.onLogout?.(); }
    catch (e) { setError(e instanceof Error ? e.message : "خروج از حساب ناموفق بود"); }
    finally { setLoading(false); }
  }

  return (
    <Screen>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <Pressable onPress={props.onBack} style={styles.backButton}><Text style={styles.backText}>›</Text></Pressable>
          <Text style={styles.title}>پروفایل</Text>
          <View style={styles.headerSpacer} />
        </View>

        <Card style={styles.profileHero}>
          <View style={styles.avatar}><Text style={styles.avatarText}>👤</Text></View>
          <View style={styles.profileCopy}>
            <Text style={styles.name}>{profile?.user_profile?.display_name || "مغازه‌دار پل"}</Text>
            <Text style={styles.sub}>{profile?.membership?.organization_name || "فروشگاه شما"}</Text>
            <StatusChip label="حساب فعال" tone="ok" />
          </View>
        </Card>

        <ErrorBox message={error} />
        {notice ? <Text style={styles.notice}>{notice}</Text> : null}

        {view === "profile" ? (
          <>
            <SectionRow icon="🏪" title="اطلاعات فروشگاه" subtitle="نام، تلفن و مشخصات حساب" onPress={() => undefined} />
            <Card style={styles.editCard}>
              <Input label="نام نمایشی" value={displayName} onChangeText={setDisplayName} maxLength={200} />
              <Input label="ایمیل" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" maxLength={254} />
              <Input label="منطقه زمانی" value={timezone} onChangeText={setTimezone} maxLength={100} />
              <Input label="شرح" value={bio} onChangeText={setBio} multiline numberOfLines={4} maxLength={2000} />
              <Btn label="ذخیره تغییرات" onPress={() => void saveProfile()} loading={loading} disabled={loading} />
            </Card>

            <SectionRow icon="🔔" title="اعلان‌ها" subtitle="سفارش‌ها، پرداخت‌ها و پیام‌های پل" onPress={() => setView("notifications")} />
            <SectionRow icon="⚙️" title="تنظیمات اعلان" subtitle="اعلان برنامه و پیامک" onPress={() => setView("preferences")} />
            <Card style={styles.menuCard}>
              <View style={styles.menuHeader}>
                <IconBadge symbol="◐" tone="brand" />
                <View style={styles.grow}><Text style={styles.menuTitle}>پوسته نمایش</Text><Text style={styles.menuSub}>{mode === "night" ? "حالت شب" : "حالت روشن"}</Text></View>
              </View>
              <View style={styles.themeRow}>
                <Btn compact label="روشن" onPress={() => setMode("light")} tone={mode === "light" ? "primary" : "ghost"} />
                <Btn compact label="شب" onPress={() => setMode("night")} tone={mode === "night" ? "primary" : "ghost"} />
              </View>
            </Card>

            <SectionRow icon="🎧" title="پشتیبانی" subtitle="رسیدگی به درخواست‌های شما از داخل پل" onPress={() => undefined} />
            <SectionRow icon="ℹ️" title="درباره پل" subtitle="بازار عمده‌فروشی برای مغازه‌داران" onPress={() => undefined} />
            <Btn label="خروج از حساب" tone="danger" onPress={() => void logout()} loading={loading} disabled={loading} />
          </>
        ) : view === "notifications" ? (
          <>
            <BackToProfile onPress={() => setView("profile")} />
            {notifications.length === 0 ? <Empty title="اعلانی وجود ندارد" description="در صورت ثبت اعلان، اینجا نمایش داده می‌شود." /> : notifications.map((n) => {
              const unread = typeof n.is_read === "boolean" ? !n.is_read : typeof n.read === "boolean" ? !n.read : false;
              return (
                <Card key={n.id} style={styles.notificationCard}>
                  <View style={styles.notificationTop}>
                    <StatusChip label={formatNotificationPriority(n.priority)} tone={n.priority === "CRITICAL" || n.priority === "HIGH" ? "warn" : "info"} />
                    {unread ? <StatusChip label="جدید" tone="ok" /> : null}
                  </View>
                  <Text style={styles.menuTitle}>{n.title || "اعلان"}</Text>
                  <Text style={styles.body}>{n.body || "—"}</Text>
                  <Text style={styles.meta}>{formatTehranDateTime(n.created_at)}</Text>
                </Card>
              );
            })}
          </>
        ) : (
          <>
            <BackToProfile onPress={() => setView("profile")} />
            <Text style={styles.menuTitle}>روش‌های دریافت اعلان</Text>
            <Text style={styles.meta}>کانال‌های دریافت اعلان را برای هر دسته انتخاب کنید.</Text>
            {preferences.length === 0 ? (
              <Empty title="تنظیماتی ثبت نشده است" description="برای این حساب هنوز دسته‌ای از اعلان‌ها تعریف نشده است." />
            ) : preferences.map((preference) => (
              <Card key={preference.category} style={styles.notificationCard}>
                <Text style={styles.menuTitle}>{formatNotificationCategory(preference.category)}</Text>
                <ToggleRow
                  label="اعلان برنامه"
                  value={Boolean(preference.push_enabled)}
                  disabled={loading}
                  onPress={() => setPreferences((current) => current.map((item) => item.category === preference.category ? { ...item, push_enabled: !item.push_enabled } : item))}
                />
                <ToggleRow
                  label="پیامک"
                  value={Boolean(preference.sms_enabled)}
                  disabled={loading}
                  onPress={() => setPreferences((current) => current.map((item) => item.category === preference.category ? { ...item, sms_enabled: !item.sms_enabled } : item))}
                />
              </Card>
            ))}
            <Btn label="ذخیره تنظیمات" onPress={() => void savePreferences()} loading={loading} disabled={loading || preferences.length === 0} />
          </>
        )}
      </ScrollView>
    </Screen>
  );
}

function SectionRow(props: { icon: string; title: string; subtitle: string; onPress: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable onPress={props.onPress} style={styles.sectionRow} accessibilityRole="button">
      <Text style={styles.arrow}>‹</Text>
      <View style={styles.grow}><Text style={styles.menuTitle}>{props.title}</Text><Text style={styles.menuSub}>{props.subtitle}</Text></View>
      <View style={styles.menuIcon}><Text>{props.icon}</Text></View>
    </Pressable>
  );
}

function BackToProfile(props: { onPress: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <Pressable onPress={props.onPress} style={styles.backLink}><Text style={styles.backLinkText}>›  بازگشت به پروفایل</Text></Pressable>;
}

const NOTIFICATION_CATEGORY_LABELS: Record<string, string> = {
  ORDER_STATUS_CHANGED: "تغییر وضعیت سفارش",
  DELIVERY_STATUS_CHANGED: "تغییر وضعیت تحویل",
  RETURN_STATUS_CHANGED: "وضعیت مرجوعی",
  PAYMENT_STATUS_CHANGED: "تغییر وضعیت پرداخت",
  SETTLEMENT_UPDATED: "به‌روزرسانی تسویه",
  SUPPORT_CASE_UPDATED: "به‌روزرسانی درخواست پشتیبانی",
  LOW_STOCK_ALERT: "هشدار کاهش موجودی",
  REFERRAL_REDEEMED: "استفاده از معرفی بنکدار",
};

function formatNotificationCategory(category: string): string {
  return NOTIFICATION_CATEGORY_LABELS[category] ?? "سایر اعلان‌ها";
}

function ToggleRow(props: { label: string; value: boolean; disabled?: boolean; onPress: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable
      onPress={props.onPress}
      disabled={props.disabled}
      accessibilityRole="switch"
      accessibilityState={{ checked: props.value, disabled: Boolean(props.disabled) }}
      style={[styles.toggleRow, props.disabled && { opacity: 0.5 }]}
    >
      <View style={[styles.toggle, props.value && styles.toggleOn]}><View style={[styles.toggleKnob, props.value && styles.toggleKnobOn]} /></View>
      <Text style={styles.toggleLabel}>{props.label}</Text>
    </Pressable>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    scroll: { paddingBottom: 36 },
    header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
    backButton: { width: 42, height: 42, borderRadius: 13, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" },
    backText: { color: colors.text, fontSize: 26 },
    headerSpacer: { width: 42 },
    title: { flex: 1, color: colors.text, fontSize: 22, fontWeight: "900", textAlign: "right", marginRight: spacing.sm },
    profileHero: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.xl },
    avatar: { width: 78, height: 78, borderRadius: 39, backgroundColor: colors.neutralBg, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
    avatarText: { fontSize: 32 },
    profileCopy: { flex: 1 },
    name: { color: colors.text, fontSize: 20, fontWeight: "900", textAlign: "right" },
    sub: { color: colors.textSecondary, fontSize: 11, marginTop: 3, marginBottom: 7, textAlign: "right" },
    editCard: { paddingBottom: spacing.md },
    sectionRow: { minHeight: 72, paddingHorizontal: spacing.md, borderRadius: 16, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, flexDirection: "row", alignItems: "center", gap: spacing.md, marginBottom: spacing.sm },
    menuIcon: { width: 42, height: 42, borderRadius: 14, backgroundColor: colors.brandSoft, alignItems: "center", justifyContent: "center" },
    menuTitle: { color: colors.text, fontSize: 14, fontWeight: "800", textAlign: "right" },
    menuSub: { color: colors.textSecondary, fontSize: 11, marginTop: 3, textAlign: "right" },
    arrow: { color: colors.textMuted, fontSize: 24 },
    menuCard: { paddingBottom: spacing.md },
    menuHeader: { flexDirection: "row", alignItems: "center", gap: spacing.md, marginBottom: spacing.md },
    themeRow: { flexDirection: "row", gap: spacing.sm },
    notice: { color: colors.success, fontSize: 12, textAlign: "right", marginBottom: spacing.sm },
    grow: { flex: 1, minWidth: 0 },
    notificationCard: { paddingBottom: spacing.md },
    notificationTop: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: spacing.sm },
    body: { color: colors.text, fontSize: 13, lineHeight: 21, textAlign: "right", marginTop: 4 },
    meta: { color: colors.textMuted, fontSize: 11, lineHeight: 18, textAlign: "right", marginTop: 5 },
    backLink: { marginBottom: spacing.md },
    backLinkText: { color: colors.brand, fontSize: 12, fontWeight: "800", textAlign: "right" },
    toggleRow: { minHeight: 54, borderTopWidth: 1, borderTopColor: colors.border, flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
    toggleLabel: { color: colors.text, fontSize: 13, fontWeight: "700" },
    toggle: { width: 44, height: 26, borderRadius: 13, backgroundColor: colors.neutralBg, borderWidth: 1, borderColor: colors.border, padding: 3, justifyContent: "center" },
    toggleOn: { backgroundColor: colors.brand, borderColor: colors.brand },
    toggleKnob: { width: 18, height: 18, borderRadius: 9, backgroundColor: colors.textMuted },
    toggleKnobOn: { backgroundColor: "#fff", alignSelf: "flex-end" },
  });
}
