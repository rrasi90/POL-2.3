"use client";

import { useState } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

const TASK_TYPE_LABELS: Record<string, string> = {
  ONBOARD_RETAILER: "بازدید از خرده‌فروش",
  TRAIN_RETAILER: "آموزش خرده‌فروش",
  FIRST_ORDER_ASSIST: "کمک سفارش اول",
  FOLLOW_UP: "پیگیری",
  VENDOR_VISIT: "بازدید فروشنده",
  DISPUTE_VISIT: "بازدید مناقشه",
  VENDOR_TIMEOUT: "تاخیر فروشنده",
};

const STATUS_TABS = [
  { key: "ASSIGNED", label: "تخصیص داده شده" },
  { key: "IN_PROGRESS", label: "در حال انجام" },
  { key: "COMPLETED", label: "تکمیل شده" },
  { key: "ALL", label: "همه" },
] as const;

type TabKey = (typeof STATUS_TABS)[number]["key"];

interface FieldTask {
  id: number;
  task_type: string;
  status: string;
  retailer_name?: string;
  vendor_name?: string;
  location?: string;
  scheduled_date?: string;
  notes?: string;
}

export default function FieldTasksPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("ASSIGNED");

  const { data: tasks, isLoading, mutate } = useApi<FieldTask[]>(
    "/api/v1/field/tasks"
  );

  const filteredTasks = tasks?.filter((t) => {
    if (activeTab === "ALL") return true;
    return t.status === activeTab;
  });

  const handleAction = async (task: FieldTask) => {
    const nextStatus = task.status === "ASSIGNED" ? "IN_PROGRESS" : "COMPLETED";
    await fetch(`/api/v1/field/tasks/${task.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: nextStatus }),
    });
    mutate();
  };

  return (
    <div className="space-y-6" dir="rtl">
      <h1 className="text-2xl font-bold">تسک‌های من</h1>

      <div className="flex gap-2 border-b pb-2">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-t transition-colors ${
              activeTab === tab.key
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : !filteredTasks?.length ? (
        <EmptyState title="تسکی یافت نشد" />
      ) : (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="rounded-lg border bg-card p-4 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold">
                  {TASK_TYPE_LABELS[task.task_type] ?? task.task_type}
                </span>
                <StatusBadge status={task.status} />
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                {task.retailer_name && (
                  <span>خرده‌فروش: {task.retailer_name}</span>
                )}
                {task.vendor_name && (
                  <span>فروشنده: {task.vendor_name}</span>
                )}
                {task.location && <span>مکان: {task.location}</span>}
                {task.scheduled_date && (
                  <span>تاریخ: {task.scheduled_date}</span>
                )}
              </div>

              {task.notes && (
                <p className="text-sm text-muted-foreground">{task.notes}</p>
              )}

              {(task.status === "ASSIGNED" || task.status === "IN_PROGRESS") && (
                <Button onClick={() => handleAction(task)}>
                  {task.status === "ASSIGNED" ? "شروع" : "تکمیل"}
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
