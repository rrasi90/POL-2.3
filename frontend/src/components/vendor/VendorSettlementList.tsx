"use client";

interface Settlement {
  id: string;
  settlement_batch_id: string;
  order_id: string;
  gross_amount_toman: number;
  commission_amount_toman: number;
  net_vendor_amount_toman: number;
  status: string;
  settled_at: string | null;
}

interface VendorSettlementListProps {
  settlements: Settlement[];
}

export function VendorSettlementList({ settlements }: VendorSettlementListProps) {
  return (
    <div className="space-y-3">
      {settlements.map((s) => (
        <div key={s.id} className="p-4 bg-white border rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">Batch: {s.settlement_batch_id?.slice(0, 8)}</p>
              <p className="text-xs text-gray-400">Order: {s.order_id?.slice(0, 8)}</p>
            </div>
            <div className="text-left">
              <p className="text-xs text-gray-500">
                Gross: {s.gross_amount_toman.toLocaleString("fa-IR")}
              </p>
              <p className="text-xs text-red-500">
                Commission: {s.commission_amount_toman.toLocaleString("fa-IR")}
              </p>
              <p className="font-bold text-green-700">
                Net: {s.net_vendor_amount_toman.toLocaleString("fa-IR")} تومان
              </p>
              {s.settled_at && (
                <p className="text-xs text-gray-400">
                  Settled: {new Date(s.settled_at).toLocaleDateString("fa-IR")}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
      {settlements.length === 0 && (
        <p className="text-center text-gray-500 py-8">No settlements yet</p>
      )}
    </div>
  );
}
