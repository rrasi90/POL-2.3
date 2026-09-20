"use client";

import { useState, useCallback } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge, PriorityBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api/client";

interface SupportMessage {
  id: string;
  sender: string;
  content: string;
  created_at: string;
}

interface SupportCase {
  id: string;
  subject: string;
  status: string;
  priority: string;
  created_at: string;
  messages: SupportMessage[];
}

const STATUS_TABS = [
  { key: "OPEN", label: "باز" },
  { key: "IN_PROGRESS", label: "در حال بررسی" },
  { key: "PENDING", label: "در انتظار" },
  { key: "RESOLVED", label: "حل شده" },
  { key: "all", label: "همه" },
] as const;

const NEXT_STATUS: Record<string, string> = {
  OPEN: "IN_PROGRESS",
  IN_PROGRESS: "PENDING",
  PENDING: "RESOLVED",
};

const NEXT_STATUS_LABEL: Record<string, string> = {
  OPEN: "شروع بررسی",
  IN_PROGRESS: "انتقال به انتظار",
  PENDING: "علامت حل شده",
};

function CaseSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="mb-3 h-4 w-48 animate-pulse rounded bg-gray-200" />
          <div className="mb-2 h-3 w-32 animate-pulse rounded bg-gray-200" />
          <div className="h-3 w-24 animate-pulse rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState<string>("OPEN");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [messageText, setMessageText] = useState("");
  const [sending, setSending] = useState(false);

  const params = activeTab !== "all" ? { status: activeTab } : undefined;
  const { data: cases, isLoading: loading, mutate } = useApi<SupportCase[]>(
    "/api/v1/support/cases",
    params,
  );

  const toggleExpand = useCallback(
    (id: string) => setExpandedId((prev) => (prev === id ? null : id)),
    [],
  );

  const handleSendMessage = useCallback(
    async (caseId: string) => {
      const text = messageText.trim();
      if (!text) return;
      setSending(true);
      try {
        await api.post(`/api/v1/support/cases/${caseId}/messages`, { content: text });
        setMessageText("");
        mutate();
      } finally {
        setSending(false);
      }
    },
    [messageText, mutate],
  );

  const handleStatusTransition = useCallback(
    async (caseId: string, currentStatus: string) => {
      const next = NEXT_STATUS[currentStatus];
      if (!next) return;
      await api.patch(`/api/v1/support/cases/${caseId}`, { status: next });
      mutate();
    },
    [mutate],
  );

  const filteredCases = cases ?? [];

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">پشتیبانی</h1>
          <Button size="sm">ایجاد پرونده جدید</Button>
        </div>

        <div className="flex gap-2 overflow-x-auto">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-gray-900 text-white"
                  : "bg-white text-gray-600 hover:bg-gray-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <CaseSkeleton />
        ) : filteredCases.length === 0 ? (
          <EmptyState
            title="پرونده‌ای یافت نشد"
            description="هنوز پرونده پشتیبانی وجود ندارد"
          />
        ) : (
          <div className="space-y-3">
            {filteredCases.map((c) => (
              <div key={c.id} className="rounded-xl border border-gray-100 bg-white shadow-sm">
                <button
                  onClick={() => toggleExpand(c.id)}
                  className="flex w-full items-center justify-between p-5 text-right"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-gray-900">{c.subject}</span>
                    <PriorityBadge priority={c.priority} />
                    <StatusBadge status={c.status} />
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(c.created_at).toLocaleDateString("fa-IR")}
                  </span>
                </button>

                {expandedId === c.id && (
                  <div className="border-t border-gray-100 px-5 pb-5">
                    <div className="mb-4 max-h-64 space-y-3 overflow-y-auto pt-4">
                      {c.messages.length === 0 && (
                        <p className="text-center text-sm text-gray-400">هنوز پیامی ارسال نشده</p>
                      )}
                      {c.messages.map((msg) => (
                        <div key={msg.id} className="rounded-lg bg-gray-50 p-3">
                          <div className="mb-1 flex items-center justify-between">
                            <span className="text-xs font-medium text-gray-700">{msg.sender}</span>
                            <span className="text-[11px] text-gray-400">
                              {new Date(msg.created_at).toLocaleString("fa-IR")}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{msg.content}</p>
                        </div>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <textarea
                        value={messageText}
                        onChange={(e) => setMessageText(e.target.value)}
                        placeholder="پیام خود را بنویسید..."
                        className="flex-1 resize-none rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-gray-400 focus:outline-none"
                        rows={2}
                      />
                      <Button
                        size="sm"
                        onClick={() => handleSendMessage(c.id)}
                        disabled={sending || !messageText.trim()}
                      >
                        ارسال
                      </Button>
                    </div>

                    {NEXT_STATUS[c.status] && (
                      <div className="mt-3 border-t border-gray-100 pt-3">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleStatusTransition(c.id, c.status)}
                        >
                          {NEXT_STATUS_LABEL[c.status]}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
