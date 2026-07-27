"use client";

import { useState } from "react";
import { BagIcon, CheckIcon } from "./icons";
import { useCart } from "@/lib/cart/context";
import type { Product } from "@/lib/types";

export function QuickAddButton({ product }: { product: Product }) {
  const { addItem } = useCart();
  const [added, setAdded] = useState(false);

  return (
    <button
      aria-label={`Add ${product.name} to bag`}
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        addItem({ slug: product.slug, name: product.name, price: product.price, art: product.art });
        setAdded(true);
        setTimeout(() => setAdded(false), 1200);
      }}
      className="absolute bottom-2 right-2 z-10 flex h-[30px] w-[30px] items-center justify-center rounded-full bg-rose transition-transform hover:scale-110"
    >
      {added ? (
        <CheckIcon className="h-3.5 w-3.5 text-white" strokeWidth={2.5} />
      ) : (
        <BagIcon className="h-3.5 w-3.5 text-white" strokeWidth={2} />
      )}
    </button>
  );
}
