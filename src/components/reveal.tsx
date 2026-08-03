"use client";

import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Animates its direct children into place as the section scrolls into view.
 * Wrap a row of cards/tiles in this to get a staggered reveal for free —
 * each child animates ~80ms after the last.
 *
 * variant "fade" — gentle fade + slide up, for banners/text blocks.
 * variant "pop"  — scale up from small with a bouncy overshoot, for grids
 *                  of product tiles/images (same card shape, punchier arrival).
 */
export function Reveal({
  children,
  className,
  stagger = 0.08,
  as: Tag = "div",
  variant = "fade",
}: {
  children: React.ReactNode;
  className?: string;
  stagger?: number;
  as?: "div" | "section";
  variant?: "fade" | "pop";
}) {
  const containerRef = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;
      if (prefersReducedMotion || !containerRef.current) return;

      const props =
        variant === "pop"
          ? { opacity: 0, scale: 0.75, duration: 0.55, ease: "back.out(1.7)" }
          : { opacity: 0, y: 24, duration: 0.5, ease: "power2.out" };

      gsap.from(containerRef.current.children, {
        ...props,
        stagger,
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top 85%",
          toggleActions: "play none none reverse",
        },
      });
    },
    { scope: containerRef, dependencies: [variant] }
  );

  return (
    <Tag ref={containerRef as React.Ref<HTMLDivElement>} className={className}>
      {children}
    </Tag>
  );
}
