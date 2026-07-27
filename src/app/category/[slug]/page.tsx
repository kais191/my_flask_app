import { notFound } from "next/navigation";
import { ProductCard } from "@/components/product-card";
import { Reveal } from "@/components/reveal";
import { getProductsByCategory } from "@/lib/data/products";
import type { CategorySlug } from "@/lib/types";

const LABELS: Record<CategorySlug, string> = {
  makeup: "Makeup",
  skincare: "Skincare",
  handbags: "Handbags",
};

export function generateStaticParams() {
  return Object.keys(LABELS).map((slug) => ({ slug }));
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  if (!(slug in LABELS)) notFound();
  const category = slug as CategorySlug;
  const items = await getProductsByCategory(category);

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-2xl">{LABELS[category]}</h1>
        {/* Filters open as a bottom sheet on mobile, not a sidebar — wired up in Phase 2 once real filter facets (shade, price, brand) exist. */}
        <button className="rounded-full border border-line px-4 py-2 text-xs font-semibold text-ink hover:border-rose">
          Filter
        </button>
      </div>
      <Reveal variant="pop" className="grid grid-cols-2 gap-x-3 gap-y-6 sm:grid-cols-3 lg:grid-cols-4">
        {items.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </Reveal>
      {items.length === 0 && (
        <p className="py-16 text-center text-sm text-ink-soft">
          Nothing here yet — check back soon.
        </p>
      )}
    </div>
  );
}
