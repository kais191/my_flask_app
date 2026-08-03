import Image from "next/image";
import { ProductArt } from "./product-art";
import type { ArtTone } from "@/lib/types";

/**
 * Real product photo when one exists, falling back to the ProductArt
 * gradient placeholder otherwise — same className/positioning API either
 * way, so call sites don't need to branch.
 *
 * Real photos use object-contain (on a neutral backdrop) rather than
 * object-cover: catalog-style product shots aren't reliably croppable —
 * cover can chop off most of the product depending on the container's
 * aspect ratio. The gradient placeholder has no such content to lose, so
 * it stays object-cover-equivalent (it just fills the box).
 */
export function ProductPhoto({
  imageUrl,
  tone,
  alt,
  className = "",
}: {
  imageUrl?: string;
  tone: ArtTone;
  alt: string;
  className?: string;
}) {
  if (imageUrl) {
    return (
      <div className={`bg-[#F3EEEA] ${className}`}>
        <Image
          src={imageUrl}
          alt={alt}
          fill
          sizes="(min-width: 1024px) 25vw, 50vw"
          className="object-contain p-4"
        />
      </div>
    );
  }

  return <ProductArt tone={tone} className={className} />;
}
