import { HeroBanner } from "@/components/hero-banner";
import { CategoryTiles } from "@/components/category-tiles";
import { ShopByLook } from "@/components/shop-by-look";
import { ProductRail } from "@/components/product-rail";
import { PreorderBanner } from "@/components/preorder-banner";
import { SocialProof } from "@/components/social-proof";
import { bestsellers } from "@/lib/mock-data";

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl">
      <HeroBanner />
      <CategoryTiles />
      <ShopByLook />
      <ProductRail
        title="Everyday Glam edit"
        seeAllHref="/search?look=everyday-glam"
        products={bestsellers()}
      />
      <PreorderBanner />
      <SocialProof />
    </div>
  );
}
