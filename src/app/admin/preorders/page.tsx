import { redirect } from "next/navigation";
import { getPreorders } from "@/lib/data/preorders";
import { isStripeConfigured } from "@/lib/stripe/env";
import { getStripe } from "@/lib/stripe/server";
import type { PreorderStatus } from "@/lib/types";

const STATUS_LABEL: Record<PreorderStatus, string> = {
  pending_deposit: "Awaiting deposit",
  deposit_paid: "Deposit paid",
  arrived: "Arrived — awaiting balance",
  balance_paid: "Complete",
  cancelled: "Cancelled",
};

const STATUS_TONE: Record<PreorderStatus, string> = {
  pending_deposit: "bg-[#fbf1e4] text-[#8a5a1f]",
  deposit_paid: "bg-cream-deep text-rose-dark",
  arrived: "bg-cream-deep text-rose-dark",
  balance_paid: "bg-[#e9f0e6] text-[#3f6b3a]",
  cancelled: "bg-[#f3e8e8] text-[#8a3a3a]",
};

async function generateBalanceLink(formData: FormData) {
  "use server";

  const id = String(formData.get("id"));
  const brand = String(formData.get("brand"));
  const itemPrice = Number(formData.get("itemPrice"));
  const depositAmount = Number(formData.get("depositAmount"));
  const balance = Math.round((itemPrice - depositAmount) * 100) / 100;

  const stripe = getStripe();
  const price = await stripe.prices.create({
    currency: "usd",
    unit_amount: Math.round(balance * 100),
    product_data: { name: `${brand} reservation — balance due` },
  });
  const link = await stripe.paymentLinks.create({
    line_items: [{ price: price.id, quantity: 1 }],
    metadata: { preorder_id: id, kind: "balance" },
  });

  redirect(`/admin/preorders?link=${encodeURIComponent(link.url)}&for=${id}`);
}

export default async function AdminPreorders({
  searchParams,
}: {
  searchParams: Promise<{ link?: string; for?: string }>;
}) {
  const [preorders, { link, for: linkFor }] = await Promise.all([getPreorders(), searchParams]);
  const stripeReady = isStripeConfigured();

  return (
    <div>
      <h1 className="mb-2 text-2xl">Preorders</h1>
      <p className="mb-6 text-sm text-ink-soft">
        Louis Vuitton, Chanel &amp; Dior reservations — 50% deposit collected
        up front via the Reserve page, balance collected once the piece has
        arrived and been authenticated.
      </p>

      {link && (
        <div className="mb-6 rounded-2xl border border-[#cfe0cb] bg-[#eef5ec] p-4">
          <p className="mb-1 text-sm font-semibold text-[#3f6b3a]">
            Balance payment link ready — send this to the customer
          </p>
          <p className="break-all text-sm text-[#3f6b3a] underline">{link}</p>
        </div>
      )}

      <div className="flex flex-col gap-3">
        {preorders.map((p) => {
          const balance = p.itemPrice - p.depositAmount;
          const canRequestBalance = p.status === "deposit_paid" || p.status === "arrived";
          return (
            <div key={p.id} className="rounded-2xl border border-line p-5">
              <div className="mb-2 flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold">{p.customerName}</p>
                  <p className="text-xs text-ink-soft">{p.customerEmail}</p>
                </div>
                <span
                  className={`whitespace-nowrap rounded-full px-2.5 py-1 text-[11px] font-semibold ${STATUS_TONE[p.status]}`}
                >
                  {STATUS_LABEL[p.status]}
                </span>
              </div>
              <p className="mb-3 text-sm text-ink-soft">
                {p.brand}
                {p.styleReference ? ` — ${p.styleReference}` : ""}
              </p>
              <div className="mb-3 flex gap-6 text-sm tabular-nums">
                <span>
                  Item <b className="font-semibold">${p.itemPrice.toLocaleString()}</b>
                </span>
                <span>
                  Deposit <b className="font-semibold">${p.depositAmount.toLocaleString()}</b>
                </span>
                <span>
                  Balance <b className="font-semibold">${balance.toLocaleString()}</b>
                </span>
              </div>
              {canRequestBalance && stripeReady && (
                <form action={generateBalanceLink}>
                  <input type="hidden" name="id" value={p.id} />
                  <input type="hidden" name="brand" value={p.brand} />
                  <input type="hidden" name="itemPrice" value={p.itemPrice} />
                  <input type="hidden" name="depositAmount" value={p.depositAmount} />
                  <button className="rounded-full border border-line px-4 py-2 text-xs font-semibold text-ink hover:border-rose">
                    {linkFor === p.id ? "Regenerate balance link" : "Generate balance link"}
                  </button>
                </form>
              )}
            </div>
          );
        })}

        {preorders.length === 0 && (
          <p className="py-16 text-center text-sm text-ink-soft">No reservations yet.</p>
        )}
      </div>
    </div>
  );
}
