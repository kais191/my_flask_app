import Link from "next/link";
import { ProductCard } from "./product-card";
import type { Product } from "@/lib/types";

export function ProductRail({
  title,
  seeAllHref,
  products,
}: {
  title: string;
  seeAllHref: string;
  products: Product[];
}) {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-3.5 flex items-baseline justify-between">
        <h2 className="text-[17px] font-semibold">{title}</h2>
        <Link href={seeAllHref} className="text-xs text-ink-soft hover:text-rose">
          See all
        </Link>
      </div>
      <div className="no-scrollbar flex gap-3 overflow-x-auto pb-1">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </section>
  );
}
