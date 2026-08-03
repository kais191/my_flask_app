import Link from "next/link";
import { isStripeConfigured } from "@/lib/stripe/env";
import { getStripe } from "@/lib/stripe/server";

export default async function ReserveSuccessPage({
  searchParams,
}: {
  searchParams: Promise<{ session_id?: string }>;
}) {
  const { session_id } = await searchParams;

  let email: string | null = null;
  let amount: number | null = null;

  if (session_id && isStripeConfigured()) {
    try {
      const session = await getStripe().checkout.sessions.retrieve(session_id);
      email = session.customer_details?.email ?? null;
      amount = session.amount_total ? session.amount_total / 100 : null;
    } catch (err) {
      console.error("reserve/success: could not retrieve session —", err);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col items-center justify-center px-4 text-center">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-rose-dark">
        Reservation confirmed
      </p>
      <h1 className="mb-3 text-2xl">Your deposit is in</h1>
      <p className="mb-6 text-sm leading-relaxed text-ink-soft">
        {amount
          ? `We've charged your $${amount.toFixed(2)} deposit`
          : "We've received your deposit"}
        {email ? ` and will email ${email}` : ""} with sourcing updates. The
        remaining balance is only due once your piece has arrived and been
        authenticated.
      </p>
      <Link
        href="/"
        className="rounded-full bg-rose px-6 py-3 text-sm font-bold text-white transition-transform hover:scale-[1.03]"
      >
        Back to shopping
      </Link>
    </div>
  );
}
