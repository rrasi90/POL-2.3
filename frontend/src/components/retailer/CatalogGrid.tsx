"use client";

interface Product {
  id: string;
  name: string;
  brand: string;
  unit: string;
  pack_size: number;
  price_toman: number;
}

interface CatalogGridProps {
  products: Product[];
  onAddToBasket: (product: Product) => void;
}

export function CatalogGrid({ products, onAddToBasket }: CatalogGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {products.map((p) => (
        <div key={p.id} className="bg-white border rounded-lg p-4">
          <div className="h-24 bg-gray-100 rounded mb-3 flex items-center justify-center">
            <span className="text-gray-400 text-sm">No image</span>
          </div>
          <h3 className="font-medium text-sm">{p.name}</h3>
          <p className="text-xs text-gray-500">{p.brand}</p>
          <p className="text-xs text-gray-400">
            {p.pack_size} × {p.unit}
          </p>
          <div className="flex justify-between items-center mt-3">
            <p className="font-bold text-sm">
              {p.price_toman.toLocaleString("fa-IR")} تومان
            </p>
            <button
              onClick={() => onAddToBasket(p)}
              className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
            >
              Add
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
