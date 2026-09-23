import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { colors, spacing } from "../theme";

type Profile = {
  user_profile?: {
    user_id?: string;
    display_name?: string | null;
    email?: string | null;
    preferred_language?: string | null;
    timezone?: string | null;
    bio?: string | null;
    phone_number?: string | null;
  };
  membership?: { organization_id?: string; organization_name?: string | null; role?: string | null } | null;
};
type Notification = {
  id: string;
  event_name?: string | null;
  title?: string | null;
  body?: string | null;
  priority?: string | null;
  created_at?: string | null;
  read?: boolean;
  is_read?: boolean;
};

function notificationsOf(data: unknown): Notification[] {
  if (Array.isArray(data)) return data as Notification[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of ["items", "notifications", "data", "results"]) {
    if (Array.isArray(o[k])) return o[k] as Notification[];
  }
  return [];
}

export function AccountMobileScreen(props: { role: Role; onBack?: () => void }): React.ReactNode {
  const [tab, setTab] = useState<"profile" | "notifications">("profile");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
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
      const [p, c] = await Promise.all([
        api.get<Profile>("/api/v1/profile"),
        api.get<Profile>("/api/v1/profile/context"),
      ]);
      const merged: Profile = {
        user_profile: p.user_profile,
        membership: c.membership ?? p.membership ?? null,
      };
      setProfile(merged);
      setDisplayName(merged.user_profile?.display_name || "");
      setEmail(merged.user_profile?.email || "");
      setTimezone(merged.user_profile?.timezone || "Asia/Tehran");
      setBio(merged.user_profile?.bio || "");
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت حساب ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  const loadNotifications = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const d = await api.get<unknown>("/api/v1/notifications?limit=50&offset=0");
      setNotifications(notificationsOf(d));
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت اعلان‌ها ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    void (tab === "profile" ? loadProfile() : loadNotifications());
  }, [tab, loadProfile, loadNotifications]);

  async function saveProfile(): Promise<void> {
    if (!displayName.trim()) { setError("نام نمایشی الزامی است."); return; }
    setLoading(true); setError(null); setNotice(null);
    try {
      await api.put("/api/v1/profile", {
        display_name: displayName.trim(),
        email: email.trim() ? email.trim() : null,
        preferred_language: "fa-IR",
        timezone: timezone.trim(),
        bio: bio.trim() ? bio.trim() : null,
      });
      await loadProfile();
      setNotice("حساب ذخیره شد.");
    } catch (e) { setError(e instanceof Error ? e.message : "ذخیره حساب ناموفق بود"); }
    finally { setLoading(false); }
  }

  return (
    <Screen>
      <ScrollView>
        <Title badge={props.role}>حساب کاربری</Title>
        {props.onBack ? <Btn label="بازگشت" tone="ghost" onPress={props.onBack} /> : null}
        <View style={styles.tabs}>
          <Btn label="پروفایل" onPress={() => setTab("profile")} tone={tab === "profile" ? "primary" : "ghost"} />
          <Btn label="اعلان‌ها" onPress={() => setTab("notifications")} tone={tab === "notifications" ? "primary" : "ghost"} />
        </View>
        <ErrorBox message={error} />
        {notice ? <Text style={styles.notice}>{notice}</Text> : null}
        {tab === "profile" ? (
          <Card>
            <Text style={styles.h2}>اطلاعات حساب</Text>
            <Text style={styles.meta}>نقش: {profile?.membership?.role || props.role}</Text>
            <Text style={styles.meta}>سازمان: {profile?.membership?.organization_name || profile?.membership?.organization_id || "—"}</Text>
            <Text style={styles.meta}>شماره: {profile?.user_profile?.phone_number || "—"}</Text>
            <Input label="نام نمایشی" value={displayName} onChangeText={setDisplayName} maxLength={200} />
            <Input label="ایمیل" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" maxLength={254} />
            <Input label="منطقه زمانی" value={timezone} onChangeText={setTimezone} maxLength={100} />
            <Input label="شرح" value={bio} onChangeText={setBio} multiline numberOfLines={4} maxLength={2000} />
            <Btn label="ذخیره تغییرات" onPress={() => void saveProfile()} loading={loading} disabled={loading} />
          </Card>
        ) : notifications.length === 0 ? (
          <Empty title="اعلانی وجود ندارد" description="در صورت ثبت اعلان، اینجا نمایش داده می‌شود." />
        ) : (
          notifications.map((n) => {
            const unread = typeof n.is_read === "boolean" ? !n.is_read : typeof n.read === "boolean" ? !n.read : null;
            return (
              <Card key={n.id}>
                <View style={styles.row}>
                  <StatusChip label={n.priority || "NORMAL"} tone={n.priority === "CRITICAL" || n.priority === "HIGH" ? "warn" : "info"} />
                  {unread ? <StatusChip label="خوانده‌نشده" tone="info" /> : null}
                </View>
                <Text style={styles.h2}>{n.title || "اعلان"}</Text>
                <Text style={styles.body}>{n.body || "—"}</Text>
                <Text style={styles.meta}>{n.event_name || "—"} · {n.created_at || "—"}</Text>
              </Card>
            );
          })
        )}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  tabs: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.md },
  row: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 6 },
  body: { color: colors.text, fontSize: 13, lineHeight: 20 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18, marginBottom: 3 },
  notice: { color: colors.success, fontSize: 13, marginBottom: spacing.sm },
});
