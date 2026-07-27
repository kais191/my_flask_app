import { notFound } from "next/navigation";
import { ProductArt } from "@/components/product-art";
import { ProductPhoto } from "@/components/product-photo";
import { ProductRail } from "@/components/product-rail";
import { ProductBuyBox } from "@/components/product-buy-box";
import { StarIcon } from "@/components/icons";
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
          <ProductPhoto
            imageUrl={product.imageUrl}
            tone={product.art}
            alt={product.name}
            className="absolute inset-0"
          />
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

          <ProductBuyBox product={product} isHandbag={isHandbag} />
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
