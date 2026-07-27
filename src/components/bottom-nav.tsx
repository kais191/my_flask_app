"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BagIcon, HeartIcon, HomeIcon, SearchIcon, UserIcon } from "./icons";
import { useCart } from "@/lib/cart/context";

const ITEMS = [
  { href: "/", label: "Home", icon: HomeIcon },
  { href: "/search", label: "Search", icon: SearchIcon },
  { href: "/cart", label: "Cart", icon: BagIcon },
  { href: "/wishlist", label: "Wishlist", icon: HeartIcon },
  { href: "/profile", label: "Profile", icon: UserIcon },
];

export function BottomNav() {
  const pathname = usePathname();
  const { count } = useCart();

  if (pathname.startsWith("/admin")) return null;

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-40 flex items-center justify-around border-t border-line bg-surface px-2 pb-[calc(10px+env(safe-area-inset-bottom))] pt-2.5 lg:hidden"
      aria-label="Primary"
    >
      {ITEMS.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className="relative flex min-w-11 flex-col items-center gap-1 py-1"
          >
            <span className="relative">
              <Icon
                className="h-[21px] w-[21px]"
                style={{
                  stroke: active ? "var(--color-rose)" : "var(--color-ink-soft)",
                  fill: active ? "var(--color-rose)" : "none",
                  fillOpacity: active ? 0.12 : 1,
                }}
              />
              {href === "/cart" && count > 0 && (
                <span className="absolute -right-1.5 -top-1 flex h-3.5 min-w-3.5 items-center justify-center rounded-full bg-rose px-1 text-[8px] font-bold text-white">
                  {count}
                </span>
              )}
            </span>
            <span
              className="text-[10px] font-semibold"
              style={{ color: active ? "var(--color-rose)" : "var(--color-ink-soft)" }}
            >
              {label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
