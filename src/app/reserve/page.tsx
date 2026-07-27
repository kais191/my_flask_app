import { ProductArt } from "@/components/product-art";
import { preorderBrands } from "@/lib/mock-data";

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

export default function ReservePage() {
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

      {/* Stripe deposit checkout (50% now, remainder invoiced on arrival) wires
          up in Phase 3 — this captures the request so nothing is lost until then. */}
      <div className="max-w-md rounded-2xl border border-line p-6">
        <h2 className="mb-4 text-lg font-semibold">Start a reservation</h2>
        <div className="mb-3 grid gap-3 sm:grid-cols-2">
          <select className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink">
            <option>Louis Vuitton</option>
            <option>Chanel</option>
            <option>Dior</option>
          </select>
          <input
            className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
            placeholder="Style / reference"
          />
        </div>
        <input
          type="email"
          className="mb-4 w-full rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
          placeholder="Email"
        />
        <button className="w-full rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01]">
          Continue to deposit
        </button>
      </div>
    </div>
  );
}
