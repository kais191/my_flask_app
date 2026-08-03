import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { ProductArt } from "@/components/product-art";
import { preorderBrands } from "@/lib/mock-data";
import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { getStripe } from "@/lib/stripe/server";
import { isStripeConfigured } from "@/lib/stripe/env";

const STEPS = [
  {
    title: "Tell us the piece",
    body: "Share the brand, style and any reference photos — a Chanel flap in caviar leather, a Neverfull in a specific print, whatever you have in mind.",
  },
  {
    title: "Pay 50% to reserve",
    body: "A deposit secures your place in that sourcing run. You'll get a confirmation with the expected arrival window.",
  },
  {
    title: "Pay the balance on arrival",
    body: "We authenticate and inspect before you're charged the remaining 50% — you only pay it once the piece is in hand.",
  },
];

async function startReservation(formData: FormData) {
  "use server";

  if (!isSupabaseConfigured() || !isStripeConfigured()) {
    redirect("/reserve?notice=setup");
  }

  const customerName = String(formData.get("name") ?? "").trim();
  const customerEmail = String(formData.get("email") ?? "").trim();
  const brand = String(formData.get("brand") ?? "");
  const styleReference = String(formData.get("style") ?? "").trim();
  const itemPrice = Number(formData.get("itemPrice"));

  if (!customerName || !customerEmail || !itemPrice || itemPrice <= 0) {
    redirect("/reserve?notice=invalid");
  }

  const depositAmount = Math.round(itemPrice * 0.5 * 100) / 100;

  const supabase = await createClient();
  const { data: preorder, error } = await supabase
    .from("preorders")
    .insert({
      customer_name: customerName,
      customer_email: customerEmail,
      brand,
      style_reference: styleReference || null,
      item_price: itemPrice,
      deposit_amount: depositAmount,
      status: "pending_deposit",
    })
    .select("id")
    .single();

  if (error || !preorder) {
    console.error("startReservation: could not create preorder —", error?.message);
    redirect("/reserve?notice=error");
  }

  const origin = (await headers()).get("origin") ?? "http://localhost:3000";
  const stripe = getStripe();
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    customer_email: customerEmail,
    line_items: [
      {
        price_data: {
          currency: "usd",
          product_data: {
            name: `${brand} reservation — 50% deposit`,
            description: styleReference || undefined,
          },
          unit_amount: Math.round(depositAmount * 100),
        },
        quantity: 1,
      },
    ],
    metadata: { preorder_id: preorder.id, kind: "deposit" },
    success_url: `${origin}/reserve/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/reserve`,
  });

  redirect(session.url!);
}

const NOTICES: Record<string, string> = {
  setup:
    "Reservations aren't live yet — Supabase and Stripe both need to be connected first. See README.md.",
  invalid: "Please fill in your name, email, and the piece's price before continuing.",
  error: "Something went wrong saving your reservation. Please try again.",
};

export default async function ReservePage({
  searchParams,
}: {
  searchParams: Promise<{ notice?: string }>;
}) {
  const { notice } = await searchParams;
  const isLive = isSupabaseConfigured() && isStripeConfigured();

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-10 max-w-xl">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-rose-dark">
          The Reserve
        </p>
        <h1 className="mb-3 text-3xl sm:text-4xl">Own the icons before anyone else</h1>
        <p className="text-[15px] leading-relaxed text-ink-soft">
          Louis Vuitton, Chanel and Dior pieces aren&rsquo;t held in everyday
          stock — they&rsquo;re sourced to order. Reserve yours with a 50%
          deposit; the rest is due only once your piece has arrived and been
          authenticated.
        </p>
      </div>

      <div className="mb-12 grid grid-cols-3 gap-2.5 sm:gap-4">
        {preorderBrands.map((brand) => (
          <div key={brand.name} className="relative h-32 overflow-hidden rounded-2xl sm:h-48">
            <ProductArt tone={brand.art} className="absolute inset-0" />
            <span className="absolute bottom-3 left-3 z-10 text-xs font-bold uppercase tracking-wide text-white [text-shadow:0_1px_6px_rgba(0,0,0,0.35)] sm:text-sm">
              {brand.name}
            </span>
          </div>
        ))}
      </div>

      <div className="mb-14 grid gap-6 sm:grid-cols-3">
        {STEPS.map((step, i) => (
          <div key={step.title}>
            <p className="mb-2 text-xs font-semibold text-rose">Step {i + 1}</p>
            <h3 className="mb-1.5 text-base font-semibold">{step.title}</h3>
            <p className="text-sm leading-relaxed text-ink-soft">{step.body}</p>
          </div>
        ))}
      </div>

      <div className="max-w-md rounded-2xl border border-line p-6">
        <h2 className="mb-4 text-lg font-semibold">Start a reservation</h2>

        {notice && (
          <p className="mb-4 rounded-xl border border-[#e3b98f] bg-[#fbf1e4] px-4 py-3 text-sm text-[#8a5a1f]">
            {NOTICES[notice] ?? NOTICES.error}
          </p>
        )}

        <form action={startReservation} className="flex flex-col gap-3">
          <input
            name="name"
            required
            placeholder="Full name"
            className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <select
              name="brand"
              className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink"
            >
              <option>Louis Vuitton</option>
              <option>Chanel</option>
              <option>Dior</option>
            </select>
            <input
              name="style"
              className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
              placeholder="Style / reference"
            />
          </div>
          <input
            type="email"
            name="email"
            required
            className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
            placeholder="Email"
          />
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-ink-soft">
              $
            </span>
            <input
              type="number"
              name="itemPrice"
              min="1"
              step="0.01"
              required
              className="w-full rounded-xl border border-line bg-surface py-3 pl-7 pr-4 text-sm text-ink placeholder:text-ink-soft"
              placeholder="Piece price (full retail)"
            />
          </div>
          <button className="mt-1 w-full rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01]">
            {isLive ? "Continue to deposit" : "Continue to deposit (setup required)"}
          </button>
        </form>
      </div>
    </div>
  );
}
