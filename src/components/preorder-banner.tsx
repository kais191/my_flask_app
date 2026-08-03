import Link from "next/link";
import { Reveal } from "./reveal";

export function PreorderBanner() {
  return (
    <Reveal as="section" className="px-4 py-2 sm:px-6 lg:px-8">
      <div
        className="relative overflow-hidden rounded-[20px] border border-[#e9c9bc] p-6 sm:p-9"
        style={{ background: "linear-gradient(150deg, #F6E4DC, #EABEB0)" }}
      >
        <div className="max-w-sm">
          <p className="mb-2 text-[10.5px] font-semibold uppercase tracking-[0.18em] text-rose-dark">
            By reservation
          </p>
          <h2 className="mb-2 text-2xl text-ink sm:text-3xl">Reserve the Icons</h2>
          <p className="mb-4 max-w-[280px] text-sm leading-relaxed text-ink/80">
            Louis Vuitton, Chanel &amp; Dior pieces, secured before they land —
            half now, half on arrival.
          </p>
          <p className="mb-4 text-[11.5px] font-semibold uppercase tracking-[0.08em] text-ink/60">
            LV · Chanel · Dior
          </p>
          <Link
            href="/reserve"
            className="inline-block rounded-full bg-rose px-6 py-2.5 text-[12.5px] font-bold tracking-wide text-white transition-transform hover:scale-[1.03]"
          >
            Reserve yours
          </Link>
        </div>
        <div className="absolute right-6 top-6 text-right text-[11px] text-rose-dark sm:right-9 sm:top-9">
          Deposit today
          <b className="block text-base text-ink sm:text-xl">50%</b>
        </div>
      </div>
    </Reveal>
  );
}
