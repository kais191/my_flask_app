"use client";

import Link from "next/link";
import { BagIcon, SearchIcon } from "./icons";
import { useCart } from "@/lib/cart/context";

const NAV_LINKS = [
  { href: "/category/makeup", label: "Makeup" },
  { href: "/category/skincare", label: "Skincare" },
  { href: "/category/handbags", label: "Handbags" },
  { href: "/reserve", label: "The Reserve" },
];

export function SiteHeader() {
  const { count } = useCart();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-cream/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 lg:px-8">
        <Link href="/" className="font-display text-xl italic tracking-wide text-ink">
          Beauty House
        </Link>

        <nav className="hidden items-center gap-8 lg:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-ink-soft transition-colors hover:text-ink"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            href="/search"
            aria-label="Search"
            className="flex h-9 w-9 items-center justify-center rounded-full text-ink transition-colors hover:bg-cream-deep"
          >
            <SearchIcon className="h-[19px] w-[19px]" />
          </Link>
          <Link
            href="/cart"
            aria-label={`Cart${count ? `, ${count} items` : ""}`}
            className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink transition-colors hover:bg-cream-deep"
          >
            <BagIcon className="h-[19px] w-[19px]" />
            {count > 0 && (
              <span className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose px-1 text-[9px] font-bold text-white">
                {count}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
