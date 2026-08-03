import { getRecentOrders } from "@/lib/data/orders";

export default async function AdminOrders() {
  const orders = await getRecentOrders();

  return (
    <div>
      <h1 className="mb-6 text-2xl">Orders</h1>
      <ul className="flex flex-col gap-3">
        {orders.map((o) => (
          <li key={o.id} className="rounded-2xl border border-line p-5">
            <div className="mb-2 flex items-start justify-between">
              <div>
                <p className="flex items-center gap-2 text-sm font-semibold">
                  {o.status === "new" && (
                    <span className="h-1.5 w-1.5 rounded-full bg-rose" aria-hidden />
                  )}
                  {o.customerName}
                </p>
                <p className="text-xs text-ink-soft">{o.customerEmail}</p>
              </div>
              <p className="text-sm font-semibold tabular-nums">${o.total}</p>
            </div>
            <p className="mb-2 text-sm text-ink-soft">{o.items}</p>
            <p className="text-xs text-ink-soft">
              {new Date(o.placedAt).toLocaleString(undefined, {
                dateStyle: "medium",
                timeStyle: "short",
              })}{" "}
              · {o.status === "new" ? "Awaiting fulfillment" : "Fulfilled"}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
