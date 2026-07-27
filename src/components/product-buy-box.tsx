"use client";

import { useState } from "react";
import { BagIcon, CheckIcon, HeartIcon } from "./icons";
import { useCart } from "@/lib/cart/context";
import type { Product } from "@/lib/types";

export function ProductBuyBox({ product, isHandbag }: { product: Product; isHandbag: boolean }) {
  const { addItem } = useCart();
  const [variant, setVariant] = useState(product.variants?.[0]);
  const [added, setAdded] = useState(false);

  return (
    <>
      {product.variants && (
        <div className="mb-6">
          <p className="mb-2 text-sm font-semibold">{isHandbag ? "Colour" : "Shade"}</p>
          <div className="flex flex-wrap gap-2">
            {product.variants.map((v) => (
              <button
                key={v}
                onClick={() => setVariant(v)}
                aria-pressed={variant === v}
                className={`rounded-full border px-4 py-2 text-xs font-semibold transition-colors ${
                  variant === v
                    ? "border-ink bg-ink text-cream"
                    : "border-line text-ink hover:border-rose"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      )}

      <p
        className={`mb-6 text-xs font-semibold ${
          product.stockQuantity <= product.lowStockThreshold ? "text-rose-dark" : "text-ink-soft"
        }`}
      >
        {product.stockQuantity <= product.lowStockThreshold
          ? `Only ${product.stockQuantity} left in stock`
          : "In stock, ready to ship"}
      </p>

      <div className="flex gap-3">
        <button
          onClick={() => {
            addItem({
              slug: product.slug,
              name: product.name,
              price: product.price,
              art: product.art,
              variant,
            });
            setAdded(true);
            setTimeout(() => setAdded(false), 1500);
          }}
          className="flex flex-1 items-center justify-center gap-2 rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.02]"
        >
          {added ? (
            <>
              <CheckIcon className="h-4 w-4" strokeWidth={2.5} />
              Added to bag
            </>
          ) : (
            <>
              <BagIcon className="h-4 w-4" strokeWidth={2} />
              Add to bag
            </>
          )}
        </button>
        <button
          aria-label="Add to wishlist"
          className="flex h-[52px] w-[52px] items-center justify-center rounded-full border border-line hover:border-rose"
        >
          <HeartIcon className="h-4.5 w-4.5" />
        </button>
      </div>
    </>
  );
}
