import Link from "next/link";
import { getProfitByCategory, getLowStock } from "@/lib/data/products";
import { getRecentOrders } from "@/lib/data/orders";
import { isSupabaseConfigured } from "@/lib/supabase/env";

export default async function AdminDashboard() {
  const [categories, alerts, orders] = await Promise.all([
    getProfitByCategory(),
    getLowStock(),
    getRecentOrders(),
  ]);
  const newOrders = orders.filter((o) => o.status === "new");
  const totalProfit = categories.reduce((sum, c) => sum + c.profitPotential, 0);
  const totalUnits = categories.reduce((sum, c) => sum + c.unitsInStock, 0);

  return (
    <div>
      <h1 className="mb-6 text-2xl">Dashboard</h1>

      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile label="Profit potential" value={`$${totalProfit.toLocaleString()}`} />
        <StatTile label="Units in stock" value={totalUnits.toString()} />
        <StatTile label="Low stock alerts" value={alerts.length.toString()} tone={alerts.length ? "warn" : "default"} />
        <StatTile label="New orders" value={newOrders.length.toString()} tone={newOrders.length ? "accent" : "default"} />
      </div>

      {alerts.length > 0 && (
        <div className="mb-8 rounded-2xl border border-[#e3b98f] bg-[#fbf1e4] p-4">
          <p className="mb-2 text-sm font-semibold text-[#8a5a1f]">
            {alerts.length} product{alerts.length > 1 ? "s" : ""} running low
          </p>
          <ul className="flex flex-col gap-1">
            {alerts.map((p) => (
              <li key={p.id} className="flex justify-between text-sm text-[#8a5a1f]">
                <span>{p.name}</span>
                <span className="font-semibold tabular-nums">{p.stockQuantity} left</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-line">
          <div className="border-b border-line px-5 py-4">
            <h2 className="text-sm font-semibold">Profit &amp; stock by category</h2>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-ink-soft">
                <th className="px-5 py-2 font-medium">Category</th>
                <th className="px-5 py-2 font-medium">In stock</th>
                <th className="px-5 py-2 text-right font-medium">Profit potential</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.category} className="border-t border-line">
                  <td className="px-5 py-3 font-medium">{c.label}</td>
                  <td className="px-5 py-3 tabular-nums text-ink-soft">{c.unitsInStock}</td>
                  <td className="px-5 py-3 text-right font-semibold tabular-nums">
                    ${c.profitPotential.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="rounded-2xl border border-line">
          <div className="flex items-center justify-between border-b border-line px-5 py-4">
            <h2 className="text-sm font-semibold">Order notifications</h2>
            <Link href="/admin/orders" className="text-xs text-rose">
              View all
            </Link>
          </div>
          <ul className="divide-y divide-line">
            {orders.slice(0, 3).map((o) => (
              <li key={o.id} className="flex items-start justify-between px-5 py-3.5">
                <div>
                  <p className="flex items-center gap-2 text-sm font-medium">
                    {o.status === "new" && (
                      <span className="h-1.5 w-1.5 rounded-full bg-rose" aria-hidden />
                    )}
                    {o.customerName}
                  </p>
                  <p className="text-xs text-ink-soft">{o.items}</p>
                </div>
                <p className="text-sm font-semibold tabular-nums">${o.total}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="text-xs text-ink-soft">
        {isSupabaseConfigured()
          ? "Figures above are live from Supabase."
          : "Figures above are computed from mock catalog data — add Supabase credentials to .env.local to see real numbers here (see README)."}
      </p>
    </div>
  );
}

function StatTile({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "warn" | "accent";
}) {
  const toneClass =
    tone === "warn"
      ? "text-[#8a5a1f]"
      : tone === "accent"
      ? "text-rose-dark"
      : "text-ink";
  return (
    <div className="rounded-2xl border border-line p-4">
      <p className="mb-1 text-xs text-ink-soft">{label}</p>
      <p className={`text-xl font-semibold tabular-nums ${toneClass}`}>{value}</p>
    </div>
  );
}
