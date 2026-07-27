import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { products as mockProducts } from "@/lib/mock-data";
import * as productUtils from "@/lib/product-utils";
import type { CategoryProfit } from "@/lib/product-utils";
import type { ArtTone, CategorySlug, Product } from "@/lib/types";

// Products don't have real photography yet (Phase 4 / Cloudinary), so rows
// are assigned a placeholder gradient deterministically from their id —
// stable across requests without needing an `art` column in the database.
const ART_TONES: ArtTone[] = ["rose", "peach", "sand", "moss", "clay"];
function artFor(id: string): ArtTone {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  return ART_TONES[hash % ART_TONES.length];
}

interface ProductRow {
  id: string;
  slug: string;
  name: string;
  brand: string | null;
  price: number;
  compare_at_price: number | null;
  cost: number;
  stock_quantity: number;
  low_stock_threshold: number;
  bestseller: boolean;
  rating: number;
  review_count: number;
  variants: string[] | null;
  concerns: string[] | null;
  is_preorder: boolean;
  deposit_percent: number | null;
  categories: { slug: CategorySlug } | { slug: CategorySlug }[] | null;
}

function fromRow(row: ProductRow): Product {
  const category = Array.isArray(row.categories) ? row.categories[0] : row.categories;
  return {
    id: row.id,
    slug: row.slug,
    name: row.name,
    category: category?.slug ?? "makeup",
    brand: row.brand ?? undefined,
    price: Number(row.price),
    compareAtPrice: row.compare_at_price ? Number(row.compare_at_price) : undefined,
    cost: Number(row.cost),
    art: artFor(row.id),
    stockQuantity: row.stock_quantity,
    lowStockThreshold: row.low_stock_threshold,
    bestseller: row.bestseller,
    rating: Number(row.rating),
    reviewCount: row.review_count,
    variants: row.variants ?? undefined,
    concerns: row.concerns ?? undefined,
    isPreorder: row.is_preorder,
    depositPercent: row.deposit_percent ?? undefined,
  };
}

export async function getAllProducts(): Promise<Product[]> {
  if (!isSupabaseConfigured()) return mockProducts;

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("products")
    .select("*, categories(slug)")
    .order("name");

  if (error || !data) {
    console.error("getAllProducts: falling back to mock data —", error?.message);
    return mockProducts;
  }
  return data.map(fromRow);
}

export async function getProductBySlug(slug: string): Promise<Product | undefined> {
  const products = await getAllProducts();
  return products.find((p) => p.slug === slug);
}

export async function getProductById(id: string): Promise<Product | undefined> {
  const products = await getAllProducts();
  return products.find((p) => p.id === id);
}

export async function getProductsByCategory(category: CategorySlug): Promise<Product[]> {
  const products = await getAllProducts();
  return products.filter((p) => p.category === category);
}

export async function getBestsellers(): Promise<Product[]> {
  return productUtils.bestsellers(await getAllProducts());
}

export async function getLowStock(): Promise<Product[]> {
  return productUtils.lowStock(await getAllProducts());
}

export async function getProfitByCategory(): Promise<CategoryProfit[]> {
  return productUtils.profitByCategory(await getAllProducts());
}
