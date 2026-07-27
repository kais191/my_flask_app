# Beauty House

A mobile-first storefront for a beauty + accessories store (makeup, skincare,
handbags), plus a by-reservation flow for luxury handbags (Louis Vuitton,
Chanel, Dior — 50% deposit, balance on arrival) and an admin panel for
inventory, profit, and order tracking.

## Where this is right now

This is **Phase 1**: the storefront's real code, built to the confirmed
"Blush Bloom" design, running on mock in-memory data (`src/lib/mock-data.ts`)
instead of a real database. Every page you can click through today —
homepage, category pages, product pages, cart/wishlist/profile shells,
the Reserve page, and the admin dashboard/inventory/orders views — is real
Next.js code, not a mockup. What's still ahead:

- **Phase 2** — Supabase (Postgres + Auth): real product/order/customer data,
  sign-in, and the admin panel reading live numbers instead of mock data.
- **Phase 3** — Stripe checkout, including the 50% deposit / 50% on-arrival
  flow for luxury pre-orders, plus low-stock and new-order notifications.
- **Phase 4** — real product photography via Cloudinary, replacing the
  gradient placeholders (`src/components/product-art.tsx`) used throughout.

## Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS v4** — theme tokens (colors, fonts) live in
  `src/app/globals.css` under `@theme`
- Fonts: **Fraunces** (display/serif) + **Work Sans** (body), loaded via
  `next/font/google`

## Running it locally, step by step

1. **Install Node.js 20 or later.** Check with `node -v`. If you don't have
   it, get it from [nodejs.org](https://nodejs.org) (the LTS version).
2. **Clone the repo and switch to this branch:**
   ```bash
   git clone https://github.com/kais191/my_flask_app.git
   cd my_flask_app
   git checkout claude/install-ui-ux-pro-max-skill-oxncla
   ```
3. **Install dependencies:**
   ```bash
   npm install
   ```
4. **Start the dev server:**
   ```bash
   npm run dev
   ```
5. **Open the site:** [http://localhost:3000](http://localhost:3000) for the
   storefront, [http://localhost:3000/admin](http://localhost:3000/admin) for
   the admin panel. Edits to files under `src/` hot-reload automatically.

To produce a production build locally (this also type-checks everything):

```bash
npm run build
npm run start
```

## Project structure

```
src/
  app/                  routes (App Router — one folder per URL)
    page.tsx             homepage
    category/[slug]/     category listing (makeup / skincare / handbags)
    product/[slug]/      product detail
    cart/ wishlist/ profile/ search/    storefront account pages
    reserve/             luxury pre-order (deposit) flow
    admin/               dashboard, inventory, orders
    globals.css          design tokens (colors, fonts) + Tailwind import
    layout.tsx           root layout: fonts, header, bottom nav
  components/            shared UI (header, bottom nav, product card, icons…)
  lib/
    types.ts              shape of Product / Order / etc.
    mock-data.ts           stand-in catalog + orders (swapped for Supabase in Phase 2)
```

## Design system

- **Palette** — warm cream/blush background, muted dusty-rose accent, deep
  cocoa-plum text. No pure black anywhere by design.
- **Type** — Fraunces (italic serif) for the wordmark and headings, Work Sans
  for everything else.
- **Layout** — sticky bottom nav (Home / Search / Cart / Wishlist / Profile)
  on mobile, top nav on desktop (`lg:` breakpoint and up).

## Deploying (once you're ready)

The easiest path is **Vercel** (built by the Next.js team, zero-config for
this kind of project):

1. Push this branch, then import the repo at [vercel.com/new](https://vercel.com/new).
2. Leave the build settings as detected (Next.js is auto-detected).
3. Deploy. You'll get a live URL immediately — no environment variables are
   required yet since Phase 1 has no external services wired up.

Phases 2–3 will add required environment variables (Supabase URL/key, Stripe
keys, Cloudinary credentials) — this README will be updated with exactly what
to set and where, when that lands.
