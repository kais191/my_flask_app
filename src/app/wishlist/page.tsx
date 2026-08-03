import Link from "next/link";
import { HeartIcon } from "@/components/icons";

export default function WishlistPage() {
  // Syncs across web + the future mobile app once accounts exist (Phase 2).
  return (
    <div className="mx-auto flex max-w-6xl flex-col items-center px-4 py-24 text-center sm:px-6 lg:px-8">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-cream-deep">
        <HeartIcon className="h-7 w-7 text-rose" />
      </div>
      <h1 className="mb-2 text-xl">No favorites yet</h1>
      <p className="mb-6 max-w-xs text-sm text-ink-soft">
        Tap the heart on any product to save it here — it&rsquo;ll sync to your
        account once you&rsquo;re signed in.
      </p>
      <Link
        href="/"
        className="rounded-full bg-rose px-6 py-3 text-sm font-bold text-white transition-transform hover:scale-[1.03]"
      >
        Browse the shop
      </Link>
    </div>
  );
}
