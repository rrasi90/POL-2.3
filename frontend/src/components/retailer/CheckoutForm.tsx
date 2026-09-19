"use client";

interface CartItem {
  productId: string;
  name: string;
  quantity: number;
  unitPrice: number;
}

interface CheckoutFormProps {
  items: CartItem[];
  onSubmit: () => Promise<void>;
  onBack: () => void;
}

export function CheckoutForm({ items, onSubmit, onBack }: CheckoutFormProps) {
  const total = items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);

  return (
    <div className="max-w-lg mx-auto p-4">
      <button onClick={onBack} className="mb-4 text-blue-600 hover:underline">
        ← Back to catalog
      </button>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Checkout</h2>
        <div className="space-y-3 mb-6">
          {items.map((item) => (
            <div key={item.productId} className="flex justify-between text-sm">
              <span>
                {item.name} × {item.quantity}
              </span>
              <span>{(item.quantity * item.unitPrice).toLocaleString("fa-IR")} تومان</span>
            </div>
          ))}
        </div>
        <div className="border-t pt-4 flex justify-between font-bold">
          <span>Total</span>
          <span>{total.toLocaleString("fa-IR")} تومان</span>
        </div>
        <button
          onClick={onSubmit}
          disabled={items.length === 0}
          className="w-full mt-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
        >
          Place Order
        </button>
      </div>
    </div>
  );
}
