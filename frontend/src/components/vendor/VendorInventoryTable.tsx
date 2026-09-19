"use client";

interface InventoryItem {
  id: string;
  product_name: string;
  quantity: number;
  unit: string;
  last_confirmed_at: string | null;
}

interface VendorInventoryTableProps {
  items: InventoryItem[];
  onConfirm: (itemId: string) => void;
}

export function VendorInventoryTable({ items, onConfirm }: VendorInventoryTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b">
            <th className="text-right py-2 px-3">Product</th>
            <th className="text-right py-2 px-3">Quantity</th>
            <th className="text-right py-2 px-3">Unit</th>
            <th className="text-right py-2 px-3">Last Confirmed</th>
            <th className="text-right py-2 px-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b hover:bg-gray-50">
              <td className="py-2 px-3 font-medium">{item.product_name}</td>
              <td className="py-2 px-3">{item.quantity}</td>
              <td className="py-2 px-3">{item.unit}</td>
              <td className="py-2 px-3 text-gray-500">
                {item.last_confirmed_at
                  ? new Date(item.last_confirmed_at).toLocaleDateString("fa-IR")
                  : "Never"}
              </td>
              <td className="py-2 px-3">
                <button
                  onClick={() => onConfirm(item.id)}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Confirm
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 && (
        <p className="text-center text-gray-500 py-8">No inventory items</p>
      )}
    </div>
  );
}
