"use client";

import Link from "next/link";
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ProductPhoto } from "./product-photo";
import type { Product } from "@/lib/types";

gsap.registerPlugin(ScrollTrigger);

export function Spotlight({ product }: { product: Product }) {
  const rootRef = useRef<HTMLDivElement>(null);
  const blobRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<HTMLDivElement>(null);
  const copyRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLAnchorElement>(null);

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

      // decorative blob drifts slower than scroll — background layer only, never the product or copy
      if (blobRef.current) {
        gsap.to(blobRef.current, {
          yPercent: 14,
          ease: "none",
          scrollTrigger: { trigger: rootRef.current, scrub: 0.5 },
        });
      }

      // product frame scales in as it enters view
      if (frameRef.current) {
        gsap.from(frameRef.current, {
          opacity: 0,
          scale: 0.94,
          duration: 0.7,
          ease: "power2.out",
          scrollTrigger: { trigger: rootRef.current, start: "top 75%", toggleActions: "play none none reverse" },
        });
      }

      // copy block staggers in line by line
      if (copyRef.current) {
        gsap.from(copyRef.current.children, {
          opacity: 0,
          y: 24,
          duration: 0.5,
          stagger: 0.08,
          ease: "power2.out",
          scrollTrigger: { trigger: rootRef.current, start: "top 75%", toggleActions: "play none none reverse" },
        });
      }

      // magnetic CTA — desktop pointer only
      const cta = ctaRef.current;
      if (cta && window.matchMedia("(pointer: fine)").matches) {
        const xTo = gsap.quickTo(cta, "x", { duration: 0.4, ease: "elastic.out(1,0.4)" });
        const yTo = gsap.quickTo(cta, "y", { duration: 0.4, ease: "elastic.out(1,0.4)" });
        const onMove = (e: MouseEvent) => {
          const r = cta.getBoundingClientRect();
          xTo((e.clientX - r.left - r.width / 2) * 0.3);
          yTo((e.clientY - r.top - r.height / 2) * 0.3);
        };
        const onLeave = () => {
          xTo(0);
          yTo(0);
        };
        cta.addEventListener("mousemove", onMove);
        cta.addEventListener("mouseleave", onLeave);
        return () => {
          cta.removeEventListener("mousemove", onMove);
          cta.removeEventListener("mouseleave", onLeave);
        };
      }
    },
    { scope: rootRef }
  );

  return (
    <section ref={rootRef} className="relative mx-4 my-10 overflow-hidden rounded-[28px] bg-cream-deep sm:mx-6 lg:mx-8">
      <div
        ref={blobRef}
        aria-hidden
        className="pointer-events-none absolute -right-24 -top-24 h-[420px] w-[420px] rounded-full bg-rose/20 blur-3xl"
      />
      <div className="relative grid gap-8 p-6 sm:p-10 lg:grid-cols-2 lg:items-center lg:gap-12 lg:p-14">
        <div ref={frameRef} className="relative aspect-[4/5] w-full overflow-hidden rounded-3xl bg-surface shadow-[0_20px_50px_-20px_rgba(62,39,35,0.25)]">
          <ProductPhoto
            imageUrl={product.imageUrl}
            tone={product.art}
            alt={product.name}
            className="absolute inset-0"
          />
        </div>

        <div ref={copyRef} className="flex flex-col items-start">
          <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-rose-dark">
            Editor&rsquo;s pick
          </p>
          <h2 className="mb-4 max-w-md text-[32px] leading-[1.1] sm:text-[40px]">
            {product.name}
          </h2>
          <p className="mb-6 max-w-sm text-sm leading-relaxed text-ink-soft">
            {product.brand ? `${product.brand} — ` : ""}
            our most-loved piece this season, carried for its everyday shape and quiet
            polish. Rated {product.rating.toFixed(1)} by {product.reviewCount} shoppers.
          </p>
          <p className="mb-6 text-2xl font-semibold tabular-nums">${product.price}</p>
          <Link
            ref={ctaRef}
            href={`/product/${product.slug}`}
            className="inline-block w-fit rounded-full bg-ink px-7 py-3 text-[13px] font-bold tracking-wide text-cream transition-transform will-change-transform hover:scale-[1.03]"
          >
            Shop the piece
          </Link>
        </div>
      </div>
    </section>
  );
}
