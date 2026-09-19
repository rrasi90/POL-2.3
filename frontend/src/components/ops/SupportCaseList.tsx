"use client";

interface SupportCaseListProps {
  cases: Array<{
    id: string;
    subject: string;
    status: string;
    priority: string;
    created_at: string;
  }>;
  onSelectCase: (caseId: string) => void;
}

export function SupportCaseList({ cases, onSelectCase }: SupportCaseListProps) {
  const statusColors: Record<string, string> = {
    OPEN: "bg-blue-100 text-blue-700",
    IN_PROGRESS: "bg-yellow-100 text-yellow-700",
    WAITING_ON_VENDOR: "bg-orange-100 text-orange-700",
    WAITING_ON_USER: "bg-purple-100 text-purple-700",
    RESOLVED: "bg-green-100 text-green-700",
    CLOSED: "bg-gray-100 text-gray-700",
  };

  const priorityColors: Record<string, string> = {
    LOW: "border-l-gray-300",
    NORMAL: "border-l-blue-400",
    HIGH: "border-l-orange-400",
    CRITICAL: "border-l-red-500",
  };

  return (
    <div className="space-y-3">
      {cases.map((c) => (
        <div
          key={c.id}
          onClick={() => onSelectCase(c.id)}
          className={`p-4 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 border-l-4 ${
            priorityColors[c.priority] || "border-l-gray-300"
          }`}
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{c.subject}</p>
              <p className="text-xs text-gray-400">
                {new Date(c.created_at).toLocaleDateString("fa-IR")}
              </p>
            </div>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                statusColors[c.status] || "bg-gray-100"
              }`}
            >
              {c.status}
            </span>
          </div>
        </div>
      ))}
      {cases.length === 0 && (
        <p className="text-center text-gray-500 py-8">No support cases</p>
      )}
    </div>
  );
}
