"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface Organization {
  id: string;
  name: string;
}

interface UserProfile {
  id: string;
  full_name: string;
  phone_number: string;
  role: string;
  organization: Organization;
  organizations: Organization[];
  notification_preferences: {
    push_enabled: boolean;
    sms_enabled: boolean;
    events: {
      order_created: boolean;
      order_delivered: boolean;
      price_drop: boolean;
      stock_alert: boolean;
      promotion: boolean;
      system_message: boolean;
    };
  };
}

interface NotificationEvent {
  key: keyof UserProfile["notification_preferences"]["events"];
  label: string;
}

const NOTIFICATION_EVENTS: NotificationEvent[] = [
  { key: "order_created", label: "ثبت سفارش جدید" },
  { key: "order_delivered", label: "تحویل سفارش" },
  { key: "price_drop", label: "کاهش قیمت" },
  { key: "stock_alert", label: "هشدار موجودی" },
  { key: "promotion", label: "تبلیغات و پیشنهادات" },
  { key: "system_message", label: "پیام سیستمی" },
];

const ROLE_MAP: Record<string, string> = {
  retailer: "خرده‌فروش",
  vendor: "تامین‌کننده",
  admin: "مدیر",
  driver: "راننده",
  warehouse: "انباردار",
};

const toPersianDigits = (s: string) =>
  s.replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[+d]);

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingName, setEditingName] = useState(false);
  const [nameValue, setNameValue] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [switchingOrg, setSwitchingOrg] = useState(false);
  const [savingPrefs, setSavingPrefs] = useState(false);

  const fetchProfile = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/profile");
      if (!res.ok) throw new Error("خطا در دریافت پروفایل");
      const data: UserProfile = await res.json();
      setProfile(data);
      setNameValue(data.full_name);
    } catch {
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const saveName = async () => {
    if (!nameValue.trim() || nameValue === profile?.full_name) {
      setEditingName(false);
      return;
    }
    setSavingName(true);
    try {
      const res = await fetch("/api/v1/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: nameValue.trim() }),
      });
      if (!res.ok) throw new Error("خطا در ذخیره");
      setProfile((prev) =>
        prev ? { ...prev, full_name: nameValue.trim() } : prev
      );
      setEditingName(false);
    } catch {
      setNameValue(profile?.full_name ?? "");
    } finally {
      setSavingName(false);
    }
  };

  const switchOrganization = async (orgId: string) => {
    if (switchingOrg) return;
    setSwitchingOrg(true);
    try {
      const res = await fetch("/api/v1/auth/switch-organization", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ organization_id: orgId }),
      });
      if (!res.ok) throw new Error("خطا در تغییر سازمان");
      const data = await res.json();
      setProfile((prev) =>
        prev
          ? {
              ...prev,
              organization: prev.organizations.find((o) => o.id === orgId) ?? prev.organization,
              token: data.access_token,
            }
          : prev
      );
      window.location.reload();
    } catch {
      // silent
    } finally {
      setSwitchingOrg(false);
    }
  };

  const updatePref = async (
    key: keyof UserProfile["notification_preferences"]["events"],
    value: boolean
  ) => {
    if (!profile) return;
    setSavingPrefs(true);
    const updatedEvents = {
      ...profile.notification_preferences.events,
      [key]: value,
    };
    setProfile((prev) =>
      prev
        ? {
            ...prev,
            notification_preferences: {
              ...prev.notification_preferences,
              events: updatedEvents,
            },
          }
        : prev
    );
    try {
      await fetch("/api/v1/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notification_preferences: { events: updatedEvents },
        }),
      });
    } catch {
      setProfile((prev) =>
        prev
          ? {
              ...prev,
              notification_preferences: {
                ...prev.notification_preferences,
                events: {
                  ...prev.notification_preferences.events,
                  [key]: !value,
                },
              },
            }
          : prev
      );
    } finally {
      setSavingPrefs(false);
    }
  };

  const togglePush = async (enabled: boolean) => {
    if (!profile) return;
    setSavingPrefs(true);
    setProfile((prev) =>
      prev
        ? {
            ...prev,
            notification_preferences: {
              ...prev.notification_preferences,
              push_enabled: enabled,
            },
          }
        : prev
    );
    try {
      await fetch("/api/v1/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notification_preferences: { push_enabled: enabled },
        }),
      });
    } catch {
      setProfile((prev) =>
        prev
          ? {
              ...prev,
              notification_preferences: {
                ...prev.notification_preferences,
                push_enabled: !enabled,
              },
            }
          : prev
      );
    } finally {
      setSavingPrefs(false);
    }
  };

  const toggleSms = async (enabled: boolean) => {
    if (!profile) return;
    setSavingPrefs(true);
    setProfile((prev) =>
      prev
        ? {
            ...prev,
            notification_preferences: {
              ...prev.notification_preferences,
              sms_enabled: enabled,
            },
          }
        : prev
    );
    try {
      await fetch("/api/v1/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notification_preferences: { sms_enabled: enabled },
        }),
      });
    } catch {
      setProfile((prev) =>
        prev
          ? {
              ...prev,
              notification_preferences: {
                ...prev.notification_preferences,
                sms_enabled: !enabled,
              },
            }
          : prev
      );
    } finally {
      setSavingPrefs(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return (
      <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-2xl mx-auto text-center py-12 text-gray-500 text-sm">
          در حال بارگذاری...
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-2xl mx-auto text-center py-12 text-red-500 text-sm">
          خطا در بارگذاری پروفایل
        </div>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">پروفایل کاربری</h1>

        {/* User Info Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">نام</div>
              {editingName ? (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={nameValue}
                    onChange={(e) => setNameValue(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    autoFocus
                    onKeyDown={(e) => e.key === "Enter" && saveName()}
                  />
                  <button
                    onClick={saveName}
                    disabled={savingName}
                    className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {savingName ? "..." : "ذخیره"}
                  </button>
                  <button
                    onClick={() => {
                      setEditingName(false);
                      setNameValue(profile.full_name);
                    }}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    انصراف
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold text-gray-900">
                    {profile.full_name}
                  </span>
                  <button
                    onClick={() => setEditingName(true)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    ویرایش
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t">
            <div>
              <div className="text-xs text-gray-500 mb-1">شماره تماس</div>
              <div className="text-sm font-medium text-gray-900" dir="ltr">
                {toPersianDigits(profile.phone_number)}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">نقش</div>
              <div className="text-sm font-medium text-gray-900">
                {ROLE_MAP[profile.role] ?? profile.role}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">سازمان</div>
              <div className="text-sm font-medium text-gray-900">
                {profile.organization.name}
              </div>
            </div>
          </div>
        </div>

        {/* Switch Organization */}
        {profile.organizations.length > 1 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              تغییر سازمان
            </h2>
            <div className="space-y-2">
              {profile.organizations.map((org) => (
                <button
                  key={org.id}
                  onClick={() => switchOrganization(org.id)}
                  disabled={org.id === profile.organization.id || switchingOrg}
                  className={`w-full text-right px-4 py-3 rounded-lg border text-sm transition-colors ${
                    org.id === profile.organization.id
                      ? "bg-blue-50 border-blue-300 text-blue-800 font-medium"
                      : "border-gray-200 hover:border-blue-300 hover:bg-gray-50 text-gray-700"
                  }`}
                >
                  <div>{org.name}</div>
                  {org.id === profile.organization.id && (
                    <div className="text-xs text-blue-600 mt-0.5">
                      سازمان فعلی
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Notification Preferences */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            تنظیمات اعلان‌ها
          </h2>

          <div className="space-y-4 mb-6">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-sm text-gray-700">اعلان‌های push</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={profile.notification_preferences.push_enabled}
                  onChange={(e) => togglePush(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-checked:bg-blue-600 rounded-full transition-colors" />
                <div className="absolute top-0.5 right-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform peer-checked:translate-x-[-20px]" />
              </div>
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-sm text-gray-700">اعلان‌های پیامکی</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={profile.notification_preferences.sms_enabled}
                  onChange={(e) => toggleSms(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-checked:bg-blue-600 rounded-full transition-colors" />
                <div className="absolute top-0.5 right-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform peer-checked:translate-x-[-20px]" />
              </div>
            </label>
          </div>

          <div className="border-t pt-4">
            <div className="text-sm font-medium text-gray-700 mb-3">
              انواع رویدادها
            </div>
            <div className="space-y-3">
              {NOTIFICATION_EVENTS.map((event) => (
                <label
                  key={event.key}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <span className="text-sm text-gray-600">{event.label}</span>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={
                        profile.notification_preferences.events[event.key]
                      }
                      onChange={(e) => updatePref(event.key, e.target.checked)}
                      disabled={savingPrefs}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-checked:bg-blue-600 rounded-full transition-colors" />
                    <div className="absolute top-0.5 right-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-[-16px]" />
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-full bg-red-600 text-white py-3 rounded-xl font-medium hover:bg-red-700 transition-colors"
        >
          خروج از حساب کاربری
        </button>
      </div>
    </div>
  );
}
