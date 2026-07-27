import { ProductCard } from "@/components/product-card";
import { SearchIcon } from "@/components/icons";
import { products } from "@/lib/mock-data";

export default function SearchPage() {
  // Client-side filtering over mock data for now; swaps for a real search
  // index (Postgres full-text to start, see the pre-brief on Algolia/Meilisearch
  // if the catalog grows past a few hundred SKUs) once Supabase is wired up.
  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center gap-3 rounded-full border border-line bg-surface px-4 py-3">
        <SearchIcon className="h-4 w-4 text-ink-soft" />
        <input
          type="search"
          placeholder="Search Beauty House"
          className="w-full bg-transparent text-sm outline-none placeholder:text-ink-soft"
        />
      </div>
      <div className="grid grid-cols-2 gap-x-3 gap-y-6 sm:grid-cols-3 lg:grid-cols-4">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
