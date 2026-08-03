"use client";

import { createContext, useContext, useMemo, useSyncExternalStore } from "react";
import type { CartItem } from "@/lib/types";

const STORAGE_KEY = "beauty-house-cart";

function itemKey(slug: string, variant?: string) {
  return `${slug}::${variant ?? ""}`;
}

// A tiny external store backing the cart, so reading it can go through
// useSyncExternalStore — the pattern React designed specifically for
// bridging a server render (no localStorage) with the real client value
// on first paint, without a manual setState-in-effect hydration dance.
function readFromStorage(): CartItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

let cachedItems: CartItem[] = typeof window !== "undefined" ? readFromStorage() : [];
const listeners = new Set<() => void>();

function setItems(items: CartItem[]) {
  cachedItems = items;
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot() {
  return cachedItems;
}

// Must be a stable reference — a fresh [] on every call makes React think
// the snapshot changes every render and warns about a potential loop.
const EMPTY_ITEMS: CartItem[] = [];
function getServerSnapshot() {
  return EMPTY_ITEMS;
}

interface CartContextValue {
  items: CartItem[];
  count: number;
  subtotal: number;
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number) => void;
  setQuantity: (slug: string, variant: string | undefined, quantity: number) => void;
  removeItem: (slug: string, variant: string | undefined) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const items = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const addItem: CartContextValue["addItem"] = (item, quantity = 1) => {
    const key = itemKey(item.slug, item.variant);
    const existing = cachedItems.find((i) => itemKey(i.slug, i.variant) === key);
    setItems(
      existing
        ? cachedItems.map((i) =>
            itemKey(i.slug, i.variant) === key ? { ...i, quantity: i.quantity + quantity } : i
          )
        : [...cachedItems, { ...item, quantity }]
    );
  };

  const setQuantity: CartContextValue["setQuantity"] = (slug, variant, quantity) => {
    const key = itemKey(slug, variant);
    setItems(
      quantity <= 0
        ? cachedItems.filter((i) => itemKey(i.slug, i.variant) !== key)
        : cachedItems.map((i) => (itemKey(i.slug, i.variant) === key ? { ...i, quantity } : i))
    );
  };

  const removeItem: CartContextValue["removeItem"] = (slug, variant) => {
    const key = itemKey(slug, variant);
    setItems(cachedItems.filter((i) => itemKey(i.slug, i.variant) !== key));
  };

  const clear = () => setItems([]);

  const { count, subtotal } = useMemo(
    () => ({
      count: items.reduce((sum, i) => sum + i.quantity, 0),
      subtotal: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }),
    [items]
  );

  return (
    <CartContext.Provider value={{ items, count, subtotal, addItem, setQuantity, removeItem, clear }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within a CartProvider");
  return ctx;
}
