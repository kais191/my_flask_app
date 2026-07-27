"use client";

import { useEffect } from "react";
import { useCart } from "@/lib/cart/context";

/** Empties the cart once, on mount — used on the order confirmation page. */
export function ClearCartOnLoad() {
  const { clear } = useCart();
  useEffect(() => {
    clear();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return null;
}
