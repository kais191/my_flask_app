import Link from "next/link";
import { ProductArt } from "./product-art";
import { Reveal } from "./reveal";
import type { ArtTone, CategorySlug } from "@/lib/types";

const CATEGORIES: { slug: CategorySlug; label: string; art: ArtTone }[] = [
  { slug: "makeup", label: "Makeup", art: "peach" },
  { slug: "skincare", label: "Skincare", art: "rose" },
  { slug: "handbags", label: "Handbags", art: "sand" },
];

export function CategoryTiles() {
  return (
    <Reveal className="grid grid-cols-3 gap-2.5 px-4 sm:gap-4 sm:px-6 lg:px-8">
      {CATEGORIES.map((cat) => (
        <Link
          key={cat.slug}
          href={`/category/${cat.slug}`}
          className="group relative flex h-28 items-end overflow-hidden rounded-2xl p-2.5 sm:h-40 sm:p-4"
        >
          <ProductArt
            tone={cat.art}
            className="absolute inset-0 transition-transform duration-300 group-hover:scale-105"
          />
          <span className="relative z-10 text-xs font-bold tracking-wide text-white [text-shadow:0_1px_6px_rgba(0,0,0,0.35)] sm:text-base">
            {cat.label}
          </span>
        </Link>
      ))}
    </Reveal>
  );
}
