import { notFound } from "next/navigation";
import { ProductArt } from "@/components/product-art";
import { ProductRail } from "@/components/product-rail";
import { StarIcon, BagIcon, HeartIcon } from "@/components/icons";
import { getAllProducts, getProductBySlug } from "@/lib/data/products";

export async function generateStaticParams() {
  const products = await getAllProducts();
  return products.map((p) => ({ slug: p.slug }));
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = await getProductBySlug(slug);
  if (!product) notFound();

  const allProducts = await getAllProducts();
  const crossSell = allProducts.filter((p) => p.id !== product.id).slice(0, 4);
  const isHandbag = product.category === "handbags";

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-8 lg:grid-cols-2">
        <div className="relative h-[380px] overflow-hidden rounded-2xl lg:h-[520px]">
          <ProductArt tone={product.art} className="absolute inset-0" />
        </div>

        <div>
          {product.brand && (
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink-soft">
              {product.brand}
            </p>
          )}
          <h1 className="mb-2 text-2xl">{product.name}</h1>
          <div className="mb-4 flex items-center gap-1.5">
            {Array.from({ length: 5 }).map((_, i) => (
              <StarIcon
                key={i}
                className="h-3.5 w-3.5"
                style={{ color: i < Math.round(product.rating) ? "var(--color-rose)" : "var(--color-line)" }}
              />
            ))}
            <span className="ml-1 text-xs text-ink-soft">
              {product.rating} ({product.reviewCount} reviews)
            </span>
          </div>
          <p className="mb-6 text-xl font-bold">${product.price}</p>

          {product.variants && (
            <div className="mb-6">
              <p className="mb-2 text-sm font-semibold">
                {isHandbag ? "Colour" : "Shade"}
              </p>
              <div className="flex flex-wrap gap-2">
                {product.variants.map((v, i) => (
                  <button
                    key={v}
                    className={`rounded-full border px-4 py-2 text-xs font-semibold ${
                      i === 0 ? "border-ink bg-ink text-cream" : "border-line text-ink hover:border-rose"
                    }`}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>
          )}

          <p
            className={`mb-6 text-xs font-semibold ${
              product.stockQuantity <= product.lowStockThreshold ? "text-rose-dark" : "text-ink-soft"
            }`}
          >
            {product.stockQuantity <= product.lowStockThreshold
              ? `Only ${product.stockQuantity} left in stock`
              : "In stock, ready to ship"}
          </p>

          <div className="flex gap-3">
            <button className="flex flex-1 items-center justify-center gap-2 rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.02]">
              <BagIcon className="h-4 w-4" strokeWidth={2} />
              Add to bag
            </button>
            <button
              aria-label="Add to wishlist"
              className="flex h-[52px] w-[52px] items-center justify-center rounded-full border border-line hover:border-rose"
            >
              <HeartIcon className="h-4.5 w-4.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Reviews with photos front and center — real review data + photo uploads land in Phase 2 with Supabase. */}
      <section className="mt-14">
        <h2 className="mb-4 text-lg font-semibold">Reviews</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            { name: "Amira K.", art: "peach" as const, quote: "Melts in instantly, wears all day." },
            { name: "Sofia R.", art: "rose" as const, quote: "The shade range is unreal. Buying every color." },
            { name: "Nour T.", art: "sand" as const, quote: "Better than the department store version, honestly." },
          ].map((r) => (
            <div key={r.name} className="rounded-2xl border border-line p-4">
              <div className="relative mb-3 h-32 overflow-hidden rounded-xl">
                <ProductArt tone={r.art} className="absolute inset-0" />
              </div>
              <p className="mb-2 text-sm text-ink">&ldquo;{r.quote}&rdquo;</p>
              <p className="text-xs font-semibold text-ink-soft">{r.name}</p>
            </div>
          ))}
        </div>
      </section>

      <ProductRail title="Complete the look" seeAllHref="/search" products={crossSell} />
    </div>
  );
}
