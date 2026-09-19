"use client";

import type { Order } from "@/lib/types";

interface OrderListProps {
  orders: Order[];
  onSelectOrder: (orderId: string) => void;
}

export function OrderList({ orders, onSelectOrder }: OrderListProps) {
  const statusColors: Record<string, string> = {
    CREATED: "bg-gray-100 text-gray-700",
    SUBMITTED: "bg-blue-100 text-blue-700",
    ACCEPTED: "bg-indigo-100 text-indigo-700",
    PREPARING: "bg-yellow-100 text-yellow-700",
    DISPATCHED: "bg-purple-100 text-purple-700",
    DELIVERED: "bg-green-100 text-green-700",
    CANCELLED: "bg-red-100 text-red-700",
  };

  return (
    <div className="space-y-3">
      {orders.map((order) => (
        <div
          key={order.id}
          onClick={() => onSelectOrder(order.id)}
          className="p-4 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 transition"
        >
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">{order.order_number}</p>
              <p className="text-sm text-gray-500">
                {new Date(order.created_at).toLocaleDateString("fa-IR")}
              </p>
            </div>
            <div className="text-left">
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  statusColors[order.order_status] || "bg-gray-100"
                }`}
              >
                {order.order_status}
              </span>
              <p className="text-sm font-medium mt-1">
                {order.total_amount_toman.toLocaleString("fa-IR")} تومان
              </p>
            </div>
          </div>
        </div>
      ))}
      {orders.length === 0 && (
        <p className="text-center text-gray-500 py-8">No orders yet</p>
      )}
    </div>
  );
}
