import Link from "next/link";
import { BagIcon } from "./icons";
import { ProductArt } from "./product-art";
import type { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  const lowStock = product.stockQuantity <= product.lowStockThreshold;

  return (
    <div className="w-[142px] flex-none sm:w-[180px]">
      <Link href={`/product/${product.slug}`} className="group block">
        <div className="relative mb-2 h-[150px] overflow-hidden rounded-[14px] sm:h-[190px]">
          <ProductArt tone={product.art} className="absolute inset-0" />
          {product.bestseller && (
            <span className="absolute left-2 top-2 z-10 rounded-full bg-white/95 px-2 py-1 text-[9.5px] font-bold uppercase tracking-wide text-ink">
              Bestseller
            </span>
          )}
          {lowStock && !product.bestseller && (
            <span className="absolute left-2 top-2 z-10 rounded-full bg-white/95 px-2 py-1 text-[9.5px] font-bold uppercase tracking-wide text-rose-dark">
              Low stock
            </span>
          )}
          <button
            aria-label={`Add ${product.name} to bag`}
            className="absolute bottom-2 right-2 z-10 flex h-[30px] w-[30px] items-center justify-center rounded-full bg-rose transition-transform hover:scale-110"
          >
            <BagIcon className="h-3.5 w-3.5 text-white" strokeWidth={2} />
          </button>
        </div>
        <p className="mb-0.5 text-[13px] font-semibold text-ink">{product.name}</p>
        <p className="mb-1 text-[11.5px] text-ink-soft">
          {product.variants ? `${product.variants.length} options` : product.brand ?? " "}
        </p>
        <p className="text-[13px] font-bold text-ink">${product.price}</p>
      </Link>
    </div>
  );
}
