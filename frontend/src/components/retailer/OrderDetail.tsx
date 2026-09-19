"use client";

import type { Order } from "@/lib/types";

interface OrderDetailProps {
  order: Order;
  onBack: () => void;
}

export function OrderDetail({ order, onBack }: OrderDetailProps) {
  const statusSteps = [
    "CREATED", "SUBMITTED", "ACCEPTED", "PREPARING", "DISPATCHED", "DELIVERED",
  ];
  const currentIdx = statusSteps.indexOf(order.order_status);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <button onClick={onBack} className="mb-4 text-blue-600 hover:underline">
        ← Back to orders
      </button>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold">{order.order_number}</h2>
            <p className="text-gray-500">
              {new Date(order.created_at).toLocaleDateString("fa-IR")}
            </p>
          </div>
          <p className="text-lg font-bold">
            {order.total_amount_toman.toLocaleString("fa-IR")} تومان
          </p>
        </div>

        <div className="flex items-center justify-between mb-8">
          {statusSteps.map((step, i) => (
            <div key={step} className="flex flex-col items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  i <= currentIdx
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {i + 1}
              </div>
              <p className="text-xs mt-1 text-center">{step}</p>
              {i < statusSteps.length - 1 && (
                <div
                  className={`h-0.5 w-full mt-4 ${
                    i < currentIdx ? "bg-blue-600" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="border-t pt-4">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Status:</span> {order.order_status}
          </p>
        </div>
      </div>
    </div>
  );
}
