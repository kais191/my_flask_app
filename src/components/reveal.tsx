"use client";

import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Fades + slides its direct children up into place as the section scrolls
 * into view. Wrap a row of cards/tiles in this to get a staggered reveal
 * for free — each child animates ~80ms after the last.
 */
export function Reveal({
  children,
  className,
  stagger = 0.08,
  as: Tag = "div",
}: {
  children: React.ReactNode;
  className?: string;
  stagger?: number;
  as?: "div" | "section";
}) {
  const containerRef = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;
      if (prefersReducedMotion || !containerRef.current) return;

      gsap.from(containerRef.current.children, {
        opacity: 0,
        y: 24,
        duration: 0.5,
        stagger,
        ease: "power2.out",
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top 85%",
          toggleActions: "play none none reverse",
        },
      });
    },
    { scope: containerRef }
  );

  return (
    <Tag ref={containerRef as React.Ref<HTMLDivElement>} className={className}>
      {children}
    </Tag>
  );
}
