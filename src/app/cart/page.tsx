"use client";

import { useState } from "react";
import Link from "next/link";
import { BagIcon, MinusIcon, PlusIcon, TrashIcon } from "@/components/icons";
import { ProductPhoto } from "@/components/product-photo";
import { useCart } from "@/lib/cart/context";

export default function CartPage() {
  const { items, subtotal, setQuantity, removeItem } = useCart();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function checkout() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: items.map((i) => ({ slug: i.slug, variant: i.variant, quantity: i.quantity })),
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.url) {
        setError(data.error ?? "Something went wrong. Please try again.");
        setLoading(false);
        return;
      }
      window.location.href = data.url;
    } catch {
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto flex max-w-6xl flex-col items-center px-4 py-24 text-center sm:px-6 lg:px-8">
        <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-cream-deep">
          <BagIcon className="h-7 w-7 text-rose" />
        </div>
        <h1 className="mb-2 text-xl">Your bag is empty</h1>
        <p className="mb-6 max-w-xs text-sm text-ink-soft">
          Add something from Makeup, Skincare or Handbags to see it here.
        </p>
        <Link
          href="/"
          className="rounded-full bg-rose px-6 py-3 text-sm font-bold text-white transition-transform hover:scale-[1.03]"
        >
          Start shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-2xl">Your bag</h1>

      <div className="mb-8 flex flex-col gap-4">
        {items.map((item) => (
          <div key={`${item.slug}::${item.variant ?? ""}`} className="flex gap-4">
            <div className="relative h-20 w-20 flex-none overflow-hidden rounded-xl">
              <ProductPhoto imageUrl={item.imageUrl} tone={item.art} alt={item.name} className="absolute inset-0" />
            </div>
            <div className="flex flex-1 flex-col justify-between">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-ink">{item.name}</p>
                  {item.variant && <p className="text-xs text-ink-soft">{item.variant}</p>}
                </div>
                <button
                  aria-label={`Remove ${item.name}`}
                  onClick={() => removeItem(item.slug, item.variant)}
                  className="text-ink-soft hover:text-rose-dark"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 rounded-full border border-line px-2 py-1">
                  <button
                    aria-label="Decrease quantity"
                    onClick={() => setQuantity(item.slug, item.variant, item.quantity - 1)}
                    className="flex h-6 w-6 items-center justify-center text-ink-soft hover:text-ink"
                  >
                    <MinusIcon className="h-3.5 w-3.5" />
                  </button>
                  <span className="min-w-4 text-center text-xs font-semibold tabular-nums">
                    {item.quantity}
                  </span>
                  <button
                    aria-label="Increase quantity"
                    onClick={() => setQuantity(item.slug, item.variant, item.quantity + 1)}
                    className="flex h-6 w-6 items-center justify-center text-ink-soft hover:text-ink"
                  >
                    <PlusIcon className="h-3.5 w-3.5" />
                  </button>
                </div>
                <p className="text-sm font-semibold tabular-nums">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-line p-5">
        <div className="mb-1 flex items-center justify-between text-sm">
          <span className="text-ink-soft">Subtotal</span>
          <span className="font-semibold tabular-nums">${subtotal.toFixed(2)}</span>
        </div>
        <p className="mb-4 text-xs text-ink-soft">Shipping and taxes calculated at checkout.</p>

        {error && (
          <p className="mb-4 rounded-xl border border-[#e3b98f] bg-[#fbf1e4] px-4 py-3 text-sm text-[#8a5a1f]">
            {error}
          </p>
        )}

        <button
          onClick={checkout}
          disabled={loading}
          className="w-full rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01] disabled:opacity-60"
        >
          {loading ? "Redirecting to checkout…" : "Checkout"}
        </button>
      </div>
    </div>
  );
}
