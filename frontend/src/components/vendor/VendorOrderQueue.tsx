"use client";

interface VendorOrder {
  id: string;
  order_number: string;
  retailer_name: string;
  total_amount_toman: number;
  order_status: string;
  created_at: string;
}

interface VendorOrderQueueProps {
  orders: VendorOrder[];
  onAccept: (orderId: string) => void;
  onReject: (orderId: string) => void;
}

export function VendorOrderQueue({ orders, onAccept, onReject }: VendorOrderQueueProps) {
  return (
    <div className="space-y-3">
      {orders.map((order) => (
        <div key={order.id} className="p-4 bg-white border rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{order.order_number}</p>
              <p className="text-sm text-gray-600">{order.retailer_name}</p>
              <p className="text-xs text-gray-400">
                {new Date(order.created_at).toLocaleDateString("fa-IR")}
              </p>
            </div>
            <div className="text-left">
              <p className="font-bold">
                {order.total_amount_toman.toLocaleString("fa-IR")} تومان
              </p>
              {order.order_status === "SUBMITTED" && (
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => onAccept(order.id)}
                    className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => onReject(order.id)}
                    className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
      {orders.length === 0 && (
        <p className="text-center text-gray-500 py-8">No pending orders</p>
      )}
    </div>
  );
}
