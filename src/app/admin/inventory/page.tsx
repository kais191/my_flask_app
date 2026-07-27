import Link from "next/link";
import { getAllProducts } from "@/lib/data/products";
import { isSupabaseConfigured } from "@/lib/supabase/env";

const STATUS_MESSAGE: Record<string, string> = {
  created: "Product added.",
  updated: "Product updated.",
  deleted: "Product deleted.",
};

export default async function AdminInventory({
  searchParams,
}: {
  searchParams: Promise<{ created?: string; updated?: string; deleted?: string }>;
}) {
  const [products, params] = await Promise.all([getAllProducts(), searchParams]);
  const statusKey = Object.keys(params).find((k) => params[k as keyof typeof params]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl">Inventory</h1>
        <Link
          href="/admin/inventory/new"
          className="rounded-full bg-rose px-5 py-2.5 text-xs font-bold text-white"
        >
          Add product
        </Link>
      </div>

      {statusKey && STATUS_MESSAGE[statusKey] && (
        <p className="mb-4 rounded-xl border border-[#cfe0cb] bg-[#eef5ec] px-4 py-3 text-sm text-[#3f6b3a]">
          {STATUS_MESSAGE[statusKey]}
        </p>
      )}

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
              <th className="px-5 py-3 font-medium" />
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
                  <td className="px-5 py-3.5 text-right">
                    {isSupabaseConfigured() ? (
                      <Link href={`/admin/inventory/${p.id}/edit`} className="text-xs font-semibold text-rose">
                        Edit
                      </Link>
                    ) : (
                      <span className="text-xs text-ink-soft">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-ink-soft">
        {isSupabaseConfigured()
          ? "Crossing the low-stock threshold triggers a live alert on the dashboard."
          : "Connect Supabase to add, edit, or delete products — see README.md."}
      </p>
    </div>
  );
}
