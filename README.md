# Beauty House

A mobile-first storefront for a beauty + accessories store (makeup, skincare,
handbags), plus a by-reservation flow for luxury handbags (Louis Vuitton,
Chanel, Dior — 50% deposit, balance on arrival) and an admin panel for
inventory, profit, and order tracking.

## Where this is right now

- **Phase 1 (done)** — the storefront's real code, built to the confirmed
  "Blush Bloom" design: homepage, category pages, product pages,
  cart/wishlist/profile shells, the Reserve page, and the admin
  dashboard/inventory/orders views.
- **Phase 2 (done)** — Supabase (Postgres + Auth) is wired up: schema, admin
  sign-in, and every page above reads real data *once you connect a Supabase
  project* (steps below). Until you do, the site keeps running on the
  built-in mock catalog, so it's never broken in the meantime.
- **Phase 3 (next)** — Stripe checkout, including the 50% deposit / 50%
  on-arrival flow for luxury pre-orders, plus live low-stock and new-order
  notifications.
- **Phase 4 (next)** — real product photography via Cloudinary, replacing the
  gradient placeholders (`src/components/product-art.tsx`) used throughout.

## Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS v4** — theme tokens (colors, fonts) live in
  `src/app/globals.css` under `@theme`
- **Supabase** (Postgres + Auth) — schema in `supabase/schema.sql`
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

That's it for a mock-data run — no account or API keys needed. To switch to
real data, continue to the Supabase section below.

To produce a production build locally (this also type-checks everything):

```bash
npm run build
npm run start
```

## Connecting Supabase (turns on real data + admin sign-in)

Skip this section if you're just browsing the mock-data version. Do this
when you're ready to store real products, orders, and customers.

1. **Create a Supabase project** at [supabase.com](https://supabase.com) —
   free tier is plenty to start. Pick a region close to you and save the
   database password it generates.
2. **Run the schema.** In the Supabase dashboard, open **SQL Editor → New
   query**, paste the contents of `supabase/schema.sql` from this repo, and
   run it. This creates every table (products, categories, orders,
   order_items, preorders, reviews, admin_profiles), the `is_admin()` helper,
   and the Row Level Security policies that let customers check out while
   keeping order data admin-only.
3. **(Optional) Load the starter catalog.** Run `supabase/seed.sql` the same
   way — it inserts the same six products you see in the mock-data version,
   so the site looks identical once you flip the switch.
4. **Get your API keys.** In the dashboard: **Project Settings → API**.
   You need the **Project URL** and the **anon public** key.
5. **Add them to `.env.local`:**
   ```bash
   cp .env.example .env.local
   ```
   then fill in:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
   ```
6. **Restart the dev server** (`npm run dev`). The homepage, category pages,
   product pages, and admin dashboard now all read from Supabase — you'll
   see this confirmed at the bottom of `/admin` ("Figures above are live
   from Supabase").
7. **Create your admin account.** In the Supabase dashboard: **Authentication
   → Users → Add user**, create yourself with an email + password. Then back
   in **SQL Editor**, run:
   ```sql
   insert into admin_profiles (id)
   values ('paste-the-user-uuid-from-the-users-table-here');
   ```
   Now `/admin` requires sign-in, and that account can get in at
   `/admin/login`. Every other admin account you want, repeat this step for.

## Project structure

```
src/
  app/                  routes (App Router — one folder per URL)
    page.tsx             homepage
    category/[slug]/     category listing (makeup / skincare / handbags)
    product/[slug]/      product detail
    cart/ wishlist/ profile/ search/    storefront account pages
    reserve/             luxury pre-order (deposit) flow
    admin/               dashboard, inventory, orders, login
    globals.css          design tokens (colors, fonts) + Tailwind import
    layout.tsx           root layout: fonts, header, bottom nav
  components/            shared UI (header, bottom nav, product card, icons…)
  lib/
    types.ts              shape of Product / Order / etc.
    mock-data.ts           stand-in catalog + orders (the Phase 1 fallback)
    product-utils.ts       pure helpers (bestsellers, low stock, profit-by-category)
    data/                  data layer pages actually call — reads Supabase when
                            configured, falls back to mock-data otherwise
    supabase/               browser/server Supabase clients + config check
  proxy.ts                admin route protection (Next.js 16's replacement
                           for middleware.ts — see the file's top comment)
supabase/
  schema.sql              tables, RLS policies, is_admin() helper
  seed.sql                 the same 6 products as mock-data.ts, for parity
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
3. Add the same environment variables from your `.env.local` in the Vercel
   project's **Settings → Environment Variables** (if you've connected
   Supabase — otherwise skip this and it deploys in mock-data mode).
4. Deploy. You'll get a live URL immediately.

Phase 3 will add Stripe environment variables — this README will be updated
with exactly what to set and where, when that lands.
