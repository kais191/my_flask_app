import { HeartIcon } from "./icons";
import { ProductArt } from "./product-art";
import type { ArtTone } from "@/lib/types";

const POSTS: { art: ArtTone; likes: number }[] = [
  { art: "peach", likes: 241 },
  { art: "rose", likes: 98 },
  { art: "sand", likes: 412 },
  { art: "moss", likes: 76 },
  { art: "clay", likes: 329 },
  { art: "peach", likes: 154 },
];

export function SocialProof() {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <h2 className="mb-3.5 text-[17px] font-semibold">Real results, #BeautyHouseGlow</h2>
      <div className="grid grid-cols-3 gap-1.5 sm:grid-cols-6">
        {POSTS.map((post, i) => (
          <div key={i} className="relative aspect-square overflow-hidden rounded-[10px]">
            <ProductArt tone={post.art} className="absolute inset-0" />
            <span className="absolute bottom-1.5 left-1.5 z-10 flex items-center gap-1 text-[10px] font-bold text-white">
              <HeartIcon className="h-[11px] w-[11px]" fill="currentColor" stroke="none" />
              {post.likes}
            </span>
          </div>
        ))}
      </div>
      <p className="mt-2.5 text-center text-[11.5px] text-ink-soft">
        Tag #BeautyHouseGlow to be featured
      </p>
    </section>
  );
}
