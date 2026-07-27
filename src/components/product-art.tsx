import type { ArtTone } from "@/lib/types";

/**
 * Placeholder for real product photography. Renders a soft gradient in the
 * Blush Bloom palette so layouts read correctly before Cloudinary is wired
 * up — swap for a Next/Image once real photos exist, same className API.
 */
const GRADIENTS: Record<ArtTone, string> = {
  rose: "radial-gradient(120% 100% at 80% 10%, #E9C6B8 0%, #C17A8B 55%, #6E3D45 100%)",
  peach: "radial-gradient(120% 100% at 20% 15%, #F3D3C4 0%, #E3A99A 45%, #B0503F 100%)",
  sand: "linear-gradient(160deg, #EADFCF 0%, #C9B79A 60%, #8A6F52 100%)",
  moss: "radial-gradient(120% 100% at 25% 20%, #E7E5D5 0%, #B7C2A4 50%, #66765A 100%)",
  clay: "linear-gradient(160deg, #E7CBB8 0%, #C79A80 60%, #8A5C46 100%)",
};

export function ProductArt({
  tone,
  className = "",
}: {
  tone: ArtTone;
  className?: string;
}) {
  return (
    <div
      aria-hidden
      className={`${className}`}
      style={{ background: GRADIENTS[tone] }}
    />
  );
}
