import { HeroBanner } from "@/components/hero-banner";
import { CategoryTiles } from "@/components/category-tiles";
import { ShopByLook } from "@/components/shop-by-look";
import { ProductRail } from "@/components/product-rail";
import { Spotlight } from "@/components/spotlight";
import { PreorderBanner } from "@/components/preorder-banner";
import { SocialProof } from "@/components/social-proof";
import { getBestsellers, getProductBySlug } from "@/lib/data/products";

export default async function Home() {
  const [bestsellers, spotlightProduct] = await Promise.all([
    getBestsellers(),
    getProductBySlug("structured-tote"),
  ]);

  return (
    <div className="mx-auto max-w-6xl">
      <HeroBanner />
      <CategoryTiles />
      <ShopByLook />
      <ProductRail
        title="Everyday Glam edit"
        seeAllHref="/search?look=everyday-glam"
        products={bestsellers}
      />
      {spotlightProduct && <Spotlight product={spotlightProduct} />}
      <PreorderBanner />
      <SocialProof />
    </div>
  );
}
