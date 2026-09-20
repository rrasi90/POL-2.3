"use client";

import { useEffect, useState, useCallback } from "react";

type Priority = "low" | "medium" | "high" | "urgent";

interface Notification {
  id: string;
  title: string;
  body: string;
  priority: Priority;
  is_read: boolean;
  created_at: string;
}

type FilterTab = "all" | "unread" | "important";

const TABS: { key: FilterTab; label: string }[] = [
  { key: "all", label: "همه" },
  { key: "unread", label: "خوانده نشده" },
  { key: "important", label: "مهم" },
];

const PRIORITY_CONFIG: Record<
  Priority,
  { label: string; color: string; bgColor: string; borderColor: string }
> = {
  low: {
    label: "کم",
    color: "text-gray-600",
    bgColor: "bg-gray-100",
    borderColor: "border-r-gray-400",
  },
  medium: {
    label: "متوسط",
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    borderColor: "border-r-blue-400",
  },
  high: {
    label: "زیاد",
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    borderColor: "border-r-orange-400",
  },
  urgent: {
    label: "فوری",
    color: "text-red-600",
    bgColor: "bg-red-50",
    borderColor: "border-r-red-500",
  },
};

const toPersianDigits = (s: string) =>
  s.replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[+d]);

function formatRelativeTime(dateStr: string): string {
  const now = new Date();
  const then = new Date(dateStr);
  const diffMs = now.getTime() - then.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffMin < 1) return "همین الان";
  if (diffMin < 60) return `${toPersianDigits(String(diffMin))} دقیقه پیش`;
  if (diffHr < 24) return `${toPersianDigits(String(diffHr))} ساعت پیش`;
  if (diffDay < 7) return `${toPersianDigits(String(diffDay))} روز پیش`;
  return then.toLocaleDateString("fa-IR");
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<FilterTab>("all");

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/notifications");
      if (!res.ok) throw new Error("خطا در دریافت اعلان‌ها");
      const data = await res.json();
      setNotifications(data);
    } catch {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const markAsRead = async (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    try {
      await fetch(`/api/v1/notifications/${id}/read`, { method: "POST" });
    } catch {
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: false } : n))
      );
    }
  };

  const markAllAsRead = async () => {
    const unread = notifications.filter((n) => !n.is_read);
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    try {
      await fetch("/api/v1/notifications/read-all", { method: "POST" });
    } catch {
      setNotifications((prev) =>
        prev.map((n) =>
          unread.some((u) => u.id === n.id) ? { ...n, is_read: false } : n
        )
      );
    }
  };

  const filtered = notifications.filter((n) => {
    if (activeTab === "unread") return !n.is_read;
    if (activeTab === "important")
      return n.priority === "high" || n.priority === "urgent";
    return true;
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">اعلان‌ها</h1>
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full px-2 py-0.5">
                {toPersianDigits(String(unreadCount))}
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
            >
              همه خوانده شد
            </button>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12 text-gray-500 text-sm">
            در حال بارگذاری...
          </div>
        )}

        {/* Empty State */}
        {!loading && filtered.length === 0 && (
          <div className="text-center py-16">
            <div className="text-4xl mb-3">🔔</div>
            <div className="text-gray-500">اعلان جدیدی ندارید</div>
          </div>
        )}

        {/* Notification Cards */}
        <div className="space-y-3">
          {filtered.map((notification) => {
            const config = PRIORITY_CONFIG[notification.priority];
            return (
              <div
                key={notification.id}
                onClick={() => !notification.is_read && markAsRead(notification.id)}
                className={`bg-white rounded-xl border border-gray-200 p-4 cursor-pointer transition-all hover:shadow-sm border-r-4 ${config.borderColor} ${
                  !notification.is_read ? "bg-blue-50/30" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3
                        className={`text-sm ${
                          notification.is_read
                            ? "font-medium text-gray-700"
                            : "font-bold text-gray-900"
                        }`}
                      >
                        {notification.title}
                      </h3>
                      {!notification.is_read && (
                        <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {notification.body}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-gray-400">
                        {formatRelativeTime(notification.created_at)}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${config.bgColor} ${config.color}`}
                      >
                        {config.label}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
