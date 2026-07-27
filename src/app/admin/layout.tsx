import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";

const NAV = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/inventory", label: "Inventory" },
  { href: "/admin/orders", label: "Orders" },
  { href: "/admin/preorders", label: "Preorders" },
];

async function signOut() {
  "use server";
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/admin/login");
}

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const showSignOut = isSupabaseConfigured();

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <p className="font-display text-lg italic text-ink">Beauty House</p>
          <p className="text-xs text-ink-soft">Admin</p>
        </div>
        <div className="flex items-center gap-3">
          <nav className="flex gap-1 rounded-full border border-line bg-surface p-1">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full px-4 py-1.5 text-xs font-semibold text-ink-soft transition-colors hover:bg-cream-deep hover:text-ink"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          {showSignOut && (
            <form action={signOut}>
              <button className="text-xs font-semibold text-ink-soft hover:text-ink">
                Sign out
              </button>
            </form>
          )}
        </div>
      </div>
      {children}
    </div>
  );
}
