"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProductArt } from "./product-art";
import type { ArtTone } from "@/lib/types";

interface Slide {
  eyebrow: string;
  title: string;
  cta: string;
  href: string;
  art: ArtTone;
}

const SLIDES: Slide[] = [
  {
    eyebrow: "New in this week",
    title: "The Glow Edit",
    cta: "Shop bestsellers",
    href: "/search?sort=bestseller",
    art: "peach",
  },
  {
    eyebrow: "Skincare, simplified",
    title: "Routines that earn their shelf space",
    cta: "Shop skincare",
    href: "/category/skincare",
    art: "moss",
  },
  {
    eyebrow: "By reservation",
    title: "Louis Vuitton, Chanel & Dior",
    cta: "See The Reserve",
    href: "/reserve",
    art: "clay",
  },
];

export function HeroBanner() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;
    const id = setInterval(() => setActive((i) => (i + 1) % SLIDES.length), 5000);
    return () => clearInterval(id);
  }, []);

  const slide = SLIDES[active];

  return (
    <div className="relative mx-4 mt-4 mb-6 h-[300px] overflow-hidden rounded-[22px] sm:mx-6 sm:mb-8 sm:h-[380px] lg:mx-8 lg:h-[440px]">
      <ProductArt tone={slide.art} className="absolute inset-0" />
      <div className="relative z-10 flex h-full flex-col justify-end p-6 sm:p-10">
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-white/85">
          {slide.eyebrow}
        </p>
        <h1 className="mb-4 max-w-sm text-[29px] leading-[1.1] text-white sm:text-4xl">
          {slide.title}
        </h1>
        <Link
          href={slide.href}
          className="w-fit rounded-full bg-white px-6 py-2.5 text-[13px] font-bold tracking-wide text-ink transition-transform hover:scale-[1.03]"
        >
          {slide.cta}
        </Link>
      </div>
      <div className="absolute bottom-4 right-5 z-10 flex gap-1.5">
        {SLIDES.map((s, i) => (
          <button
            key={s.title}
            aria-label={`Show slide ${i + 1}`}
            onClick={() => setActive(i)}
            className="h-[5px] rounded-full bg-white transition-all"
            style={{ width: i === active ? 14 : 5, opacity: i === active ? 1 : 0.55 }}
          />
        ))}
      </div>
    </div>
  );
}
