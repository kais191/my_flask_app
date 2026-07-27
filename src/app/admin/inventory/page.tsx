import { products } from "@/lib/mock-data";

export default function AdminInventory() {
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl">Inventory</h1>
        <button className="rounded-full bg-rose px-5 py-2.5 text-xs font-bold text-white">
          Add product
        </button>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-line">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="text-left text-xs text-ink-soft">
              <th className="px-5 py-3 font-medium">Product</th>
              <th className="px-5 py-3 font-medium">Category</th>
              <th className="px-5 py-3 font-medium">Price</th>
              <th className="px-5 py-3 font-medium">Cost</th>
              <th className="px-5 py-3 font-medium">In stock</th>
              <th className="px-5 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => {
              const low = p.stockQuantity <= p.lowStockThreshold;
              return (
                <tr key={p.id} className="border-t border-line">
                  <td className="px-5 py-3.5 font-medium">
                    {p.name}
                    {p.brand && <span className="ml-1.5 text-xs text-ink-soft">{p.brand}</span>}
                  </td>
                  <td className="px-5 py-3.5 capitalize text-ink-soft">{p.category}</td>
                  <td className="px-5 py-3.5 tabular-nums">${p.price}</td>
                  <td className="px-5 py-3.5 tabular-nums text-ink-soft">${p.cost}</td>
                  <td className="px-5 py-3.5 tabular-nums">{p.stockQuantity}</td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                        low ? "bg-[#fbf1e4] text-[#8a5a1f]" : "bg-cream-deep text-ink-soft"
                      }`}
                    >
                      {low ? "Low stock" : "Healthy"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-ink-soft">
        Low-stock threshold is set per product. Once live, crossing it also
        triggers an in-app + email alert to the admin account (Phase 2).
      </p>
    </div>
  );
}
