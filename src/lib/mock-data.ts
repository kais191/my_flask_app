import type { Product, PreorderBrand, Order, Preorder } from "./types";

/**
 * Stand-in catalog. Shape mirrors the future Supabase `products` table
 * (see supabase/schema.sql once Phase 2 lands) so swapping this module
 * for real queries later is a drop-in change, not a rewrite.
 */
export const products: Product[] = [
  {
    id: "p1",
    slug: "silk-veil-blush",
    name: "Silk Veil Blush",
    category: "makeup",
    price: 28,
    cost: 9,
    art: "rose",
    stockQuantity: 42,
    lowStockThreshold: 10,
    bestseller: true,
    rating: 4.8,
    reviewCount: 214,
    variants: ["Petal", "Rosewood", "Terracotta", "Berry"],
    concerns: ["everyday-glam", "date-night"],
  },
  {
    id: "p2",
    slug: "dew-drop-serum",
    name: "Dew Drop Serum",
    category: "skincare",
    price: 46,
    cost: 17,
    art: "peach",
    stockQuantity: 8,
    lowStockThreshold: 10,
    rating: 4.7,
    reviewCount: 132,
    concerns: ["glowy-skin"],
  },
  {
    id: "p3",
    slug: "petite-top-handle",
    name: "Petite Top-Handle",
    category: "handbags",
    brand: "Coach",
    price: 118,
    cost: 52,
    art: "sand",
    stockQuantity: 5,
    lowStockThreshold: 6,
    rating: 4.9,
    reviewCount: 58,
    variants: ["Cream", "Blush", "Espresso"],
    concerns: ["everyday-glam", "office-ready"],
  },
  {
    id: "p4",
    slug: "velvet-matte-rouge",
    name: "Velvet Matte Rouge",
    category: "makeup",
    price: 24,
    cost: 8,
    art: "clay",
    stockQuantity: 3,
    lowStockThreshold: 10,
    rating: 4.6,
    reviewCount: 301,
    variants: ["Blush Nude", "Cherry", "Mauve", "Brick"],
    concerns: ["date-night", "everyday-glam"],
  },
  {
    id: "p5",
    slug: "barely-there-tint",
    name: "Barely-There Tint",
    category: "skincare",
    price: 22,
    cost: 7,
    art: "moss",
    stockQuantity: 30,
    lowStockThreshold: 10,
    rating: 4.5,
    reviewCount: 89,
    concerns: ["glowy-skin", "office-ready"],
  },
  {
    id: "p6",
    slug: "structured-tote",
    name: "Structured Tote",
    category: "handbags",
    brand: "Michael Kors",
    price: 168,
    cost: 74,
    art: "clay",
    imageUrl: "/images/products/structured-tote.avif",
    stockQuantity: 12,
    lowStockThreshold: 6,
    rating: 4.8,
    reviewCount: 41,
    variants: ["Oat", "Moss", "Black"],
    concerns: ["office-ready"],
  },
];

export const preorderBrands: PreorderBrand[] = [
  { name: "Louis Vuitton", art: "clay" },
  { name: "Chanel", art: "rose" },
  { name: "Dior", art: "sand" },
];

export const shopByLook = [
  { slug: "glowy-skin", label: "Glowy Skin" },
  { slug: "everyday-glam", label: "Everyday Glam" },
  { slug: "date-night", label: "Date Night" },
  { slug: "office-ready", label: "Office Ready" },
  { slug: "bridal", label: "Bridal" },
];

export const orders: Order[] = [
  {
    id: "ord_1042",
    customerName: "Layla Haddad",
    customerEmail: "layla.h@example.com",
    items: "Silk Veil Blush (Rosewood), Dew Drop Serum",
    total: 74,
    placedAt: "2026-07-26T09:14:00Z",
    status: "new",
  },
  {
    id: "ord_1041",
    customerName: "Ranya Kassem",
    customerEmail: "ranya.k@example.com",
    items: "Petite Top-Handle (Blush)",
    total: 118,
    placedAt: "2026-07-25T21:02:00Z",
    status: "new",
  },
  {
    id: "ord_1040",
    customerName: "Dina Farouk",
    customerEmail: "dina.f@example.com",
    items: "Velvet Matte Rouge (Cherry) x2",
    total: 48,
    placedAt: "2026-07-25T16:47:00Z",
    status: "fulfilled",
  },
];

export const preorders: Preorder[] = [
  {
    id: "pre_1",
    customerName: "Yasmin Odeh",
    customerEmail: "yasmin.o@example.com",
    brand: "Chanel",
    styleReference: "Classic Flap, medium, caviar black/gold",
    itemPrice: 8800,
    depositAmount: 4400,
    status: "deposit_paid",
    createdAt: "2026-07-20T10:00:00Z",
  },
  {
    id: "pre_2",
    customerName: "Farah Nasser",
    customerEmail: "farah.n@example.com",
    brand: "Louis Vuitton",
    styleReference: "Neverfull MM, Damier Ebene",
    itemPrice: 1740,
    depositAmount: 870,
    status: "arrived",
    createdAt: "2026-07-12T14:30:00Z",
  },
];

// Computed helpers (bestsellers, lowStock, profitByCategory) live in
// `src/lib/product-utils.ts` — they're pure functions over `Product[]` so
// the same logic works whether the array came from here or from Supabase.
