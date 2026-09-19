"use client";

interface NotificationListProps {
  notifications: Array<{
    id: string;
    event_name: string;
    title: string;
    body: string;
    priority: string;
    created_at: string;
  }>;
}

export function NotificationList({ notifications }: NotificationListProps) {
  const priorityColors: Record<string, string> = {
    LOW: "border-l-gray-300",
    NORMAL: "border-l-blue-400",
    HIGH: "border-l-orange-400",
    CRITICAL: "border-l-red-500",
  };

  return (
    <div className="space-y-3">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`p-4 bg-white border rounded-lg border-l-4 ${
            priorityColors[n.priority] || "border-l-gray-300"
          }`}
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{n.title}</p>
              <p className="text-sm text-gray-600 mt-1">{n.body}</p>
            </div>
            <span className="text-xs text-gray-400">
              {new Date(n.created_at).toLocaleTimeString("fa-IR", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        </div>
      ))}
      {notifications.length === 0 && (
        <p className="text-center text-gray-500 py-8">No notifications</p>
      )}
    </div>
  );
}
