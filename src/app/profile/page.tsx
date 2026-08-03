import { UserIcon } from "@/components/icons";

const MENU = [
  "Order history",
  "Reservations & deposits",
  "Saved addresses",
  "Payment methods",
  "Notification preferences",
];

export default function ProfilePage() {
  // Sign-in / account creation wires up in Phase 2 with Supabase Auth.
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-cream-deep">
          <UserIcon className="h-6 w-6 text-rose" />
        </div>
        <div>
          <h1 className="text-lg font-semibold">Welcome to Beauty House</h1>
          <p className="text-sm text-ink-soft">Sign in to track orders and reservations.</p>
        </div>
      </div>

      <button className="mb-8 w-full rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01] sm:w-auto sm:px-8">
        Sign in
      </button>

      <div className="divide-y divide-line rounded-2xl border border-line">
        {MENU.map((item) => (
          <div key={item} className="flex items-center justify-between px-5 py-4 text-sm text-ink">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}
