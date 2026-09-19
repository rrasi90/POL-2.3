"use client";

interface FieldTaskListProps {
  tasks: Array<{
    id: string;
    task_type: string;
    status: string;
    notes: string | null;
    created_at: string;
  }>;
  onUpdateTask: (taskId: string, status: string) => void;
}

export function FieldTaskList({ tasks, onUpdateTask }: FieldTaskListProps) {
  const statusColors: Record<string, string> = {
    ASSIGNED: "bg-blue-100 text-blue-700",
    IN_PROGRESS: "bg-yellow-100 text-yellow-700",
    COMPLETED: "bg-green-100 text-green-700",
    FAILED: "bg-red-100 text-red-700",
    CANCELLED: "bg-gray-100 text-gray-700",
  };

  const taskTypeLabels: Record<string, string> = {
    ONBOARD_RETAILER: "Onboard Retailer",
    TRAIN_RETAILER: "Train Retailer",
    FIRST_ORDER_ASSIST: "First Order Assist",
    FOLLOW_UP: "Follow Up",
    VENDOR_VISIT: "Vendor Visit",
    DISPUTE_VISIT: "Dispute Visit",
    VENDOR_TIMEOUT: "Vendor Timeout",
  };

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div key={task.id} className="p-4 bg-white border rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">
                {taskTypeLabels[task.task_type] || task.task_type}
              </p>
              {task.notes && (
                <p className="text-sm text-gray-600 mt-1">{task.notes}</p>
              )}
              <p className="text-xs text-gray-400 mt-1">
                {new Date(task.created_at).toLocaleDateString("fa-IR")}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  statusColors[task.status] || "bg-gray-100"
                }`}
              >
                {task.status}
              </span>
              {task.status === "ASSIGNED" && (
                <button
                  onClick={() => onUpdateTask(task.id, "IN_PROGRESS")}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Start
                </button>
              )}
              {task.status === "IN_PROGRESS" && (
                <button
                  onClick={() => onUpdateTask(task.id, "COMPLETED")}
                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Complete
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
      {tasks.length === 0 && (
        <p className="text-center text-gray-500 py-8">No tasks assigned</p>
      )}
    </div>
  );
}
