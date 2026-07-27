import Link from "next/link";
import { BagIcon } from "@/components/icons";

export default function CartPage() {
  // Cart is empty by default until client-side cart state (Phase 2, likely
  // Zustand or React context + Supabase-synced for logged-in users) lands.
  return (
    <div className="mx-auto flex max-w-6xl flex-col items-center px-4 py-24 text-center sm:px-6 lg:px-8">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-cream-deep">
        <BagIcon className="h-7 w-7 text-rose" />
      </div>
      <h1 className="mb-2 text-xl">Your bag is empty</h1>
      <p className="mb-6 max-w-xs text-sm text-ink-soft">
        Add something from Makeup, Skincare or Handbags to see it here.
      </p>
      <Link
        href="/"
        className="rounded-full bg-rose px-6 py-3 text-sm font-bold text-white transition-transform hover:scale-[1.03]"
      >
        Start shopping
      </Link>
    </div>
  );
}
