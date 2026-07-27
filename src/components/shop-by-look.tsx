import Link from "next/link";
import { shopByLook } from "@/lib/mock-data";

export function ShopByLook() {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-3.5 flex items-baseline justify-between">
        <h2 className="text-[17px] font-semibold">Shop by look</h2>
      </div>
      <div className="no-scrollbar flex gap-2 overflow-x-auto pb-1">
        {shopByLook.map((look, i) => (
          <Link
            key={look.slug}
            href={`/search?look=${look.slug}`}
            className={`flex-none rounded-full border px-4 py-2.5 text-[12.5px] font-semibold whitespace-nowrap transition-colors ${
              i === 0
                ? "border-ink bg-ink text-cream"
                : "border-line bg-surface text-ink hover:border-rose"
            }`}
          >
            {look.label}
          </Link>
        ))}
      </div>
    </section>
  );
}
