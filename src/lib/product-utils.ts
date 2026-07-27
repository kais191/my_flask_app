import type { Product } from "./types";

/**
 * Pure helpers over a `Product[]`, shared by the mock catalog and the real
 * Supabase-backed data layer (`src/lib/data/products.ts`) so the numbers
 * are computed identically regardless of where the rows came from.
 */

export function bestsellers(products: Product[]): Product[] {
  return products.filter((p) => p.bestseller || p.rating >= 4.7).slice(0, 6);
}

export function lowStock(products: Product[]): Product[] {
  return products.filter((p) => p.stockQuantity <= p.lowStockThreshold);
}

export interface CategoryProfit {
  category: Product["category"];
  label: string;
  unitsInStock: number;
  revenuePotential: number;
  profitPotential: number;
}

const CATEGORY_LABELS: Record<Product["category"], string> = {
  makeup: "Makeup",
  skincare: "Skincare",
  handbags: "Handbags",
};

/**
 * "Profit" here = (price - cost) x units currently in stock — a proxy for
 * margin reporting. A future pass could instead sum actual `order_items`
 * against `products.cost` for realized (not projected) profit.
 */
export function profitByCategory(products: Product[]): CategoryProfit[] {
  return (Object.keys(CATEGORY_LABELS) as Product["category"][]).map((category) => {
    const items = products.filter((p) => p.category === category);
    const unitsInStock = items.reduce((sum, p) => sum + p.stockQuantity, 0);
    const revenuePotential = items.reduce((sum, p) => sum + p.price * p.stockQuantity, 0);
    const profitPotential = items.reduce(
      (sum, p) => sum + (p.price - p.cost) * p.stockQuantity,
      0
    );
    return { category, label: CATEGORY_LABELS[category], unitsInStock, revenuePotential, profitPotential };
  });
}
