export type CategorySlug = "makeup" | "skincare" | "handbags";

export type ArtTone = "rose" | "peach" | "sand" | "moss" | "clay";

export interface Product {
  id: string;
  slug: string;
  name: string;
  category: CategorySlug;
  brand?: string;
  price: number;
  compareAtPrice?: number;
  cost: number;
  art: ArtTone;
  stockQuantity: number;
  lowStockThreshold: number;
  bestseller?: boolean;
  rating: number;
  reviewCount: number;
  variants?: string[]; // shade names or bag sizes
  concerns?: string[]; // "shop by look" tags
  isPreorder?: boolean;
  depositPercent?: number;
}

export interface PreorderBrand {
  name: string;
  art: ArtTone;
}

export interface Order {
  id: string;
  customerName: string;
  customerEmail: string;
  items: string;
  total: number;
  placedAt: string;
  status: "new" | "fulfilled";
}

export type PreorderStatus =
  | "pending_deposit"
  | "deposit_paid"
  | "arrived"
  | "balance_paid"
  | "cancelled";

export interface Preorder {
  id: string;
  customerName: string;
  customerEmail: string;
  brand: string;
  styleReference?: string;
  itemPrice: number;
  depositAmount: number;
  status: PreorderStatus;
  createdAt: string;
}
