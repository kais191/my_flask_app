-- Beauty House — Phase 2 schema
-- Run this once against a fresh Supabase project (SQL Editor, or `supabase db push`).
-- Safe to re-run: every statement is guarded with IF NOT EXISTS / OR REPLACE.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------------------

create table if not exists categories (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  sort_order int not null default 0
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  category_id uuid not null references categories(id),
  brand text,
  price numeric(10, 2) not null,
  compare_at_price numeric(10, 2),
  cost numeric(10, 2) not null default 0,
  stock_quantity int not null default 0,
  low_stock_threshold int not null default 10,
  bestseller boolean not null default false,
  rating numeric(2, 1) not null default 0,
  review_count int not null default 0,
  variants text[],
  concerns text[],
  is_preorder boolean not null default false,
  deposit_percent int,
  image_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid references auth.users(id) on delete set null,
  full_name text not null,
  email text not null,
  created_at timestamptz not null default now()
);

create table if not exists orders (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references customers(id),
  customer_name text not null,
  customer_email text not null,
  total numeric(10, 2) not null,
  status text not null default 'new' check (status in ('new', 'fulfilled', 'cancelled')),
  stripe_payment_intent_id text,
  placed_at timestamptz not null default now()
);

create table if not exists order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders(id) on delete cascade,
  product_id uuid references products(id) on delete set null,
  product_name text not null,
  variant text,
  quantity int not null default 1,
  unit_price numeric(10, 2) not null
);

-- Luxury bag reservations: 50% deposit now, balance charged once the piece
-- has arrived and been authenticated (see AGENTS request re: LV/Chanel/Dior).
create table if not exists preorders (
  id uuid primary key default gen_random_uuid(),
  customer_name text not null,
  customer_email text not null,
  brand text not null check (brand in ('Louis Vuitton', 'Chanel', 'Dior')),
  style_reference text,
  item_price numeric(10, 2),
  deposit_amount numeric(10, 2),
  stripe_deposit_payment_intent_id text,
  stripe_balance_payment_intent_id text,
  status text not null default 'pending_deposit'
    check (status in ('pending_deposit', 'deposit_paid', 'arrived', 'balance_paid', 'cancelled')),
  created_at timestamptz not null default now()
);

create table if not exists reviews (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references products(id) on delete cascade,
  customer_name text not null,
  rating int not null check (rating between 1 and 5),
  body text not null,
  photo_url text,
  created_at timestamptz not null default now()
);

-- Marks which auth.users accounts can access /admin and manage the catalog.
-- Add the first admin manually after creating your account:
--   insert into admin_profiles (id) values ('<your-auth-user-uuid>');
create table if not exists admin_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------

create or replace function is_admin()
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (select 1 from admin_profiles where id = auth.uid());
$$;

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists products_set_updated_at on products;
create trigger products_set_updated_at
  before update on products
  for each row execute function set_updated_at();

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------

alter table categories enable row level security;
alter table products enable row level security;
alter table customers enable row level security;
alter table orders enable row level security;
alter table order_items enable row level security;
alter table preorders enable row level security;
alter table reviews enable row level security;
alter table admin_profiles enable row level security;

-- Public storefront: anyone can read the catalog.
drop policy if exists "categories are publicly readable" on categories;
create policy "categories are publicly readable" on categories for select using (true);

drop policy if exists "products are publicly readable" on products;
create policy "products are publicly readable" on products for select using (true);

drop policy if exists "reviews are publicly readable" on reviews;
create policy "reviews are publicly readable" on reviews for select using (true);

-- Checkout: anyone can place an order or start a reservation (writes only —
-- reading back other people's orders is restricted to admins below).
drop policy if exists "anyone can place an order" on orders;
create policy "anyone can place an order" on orders for insert with check (true);

drop policy if exists "anyone can add order items" on order_items;
create policy "anyone can add order items" on order_items for insert with check (true);

drop policy if exists "anyone can start a reservation" on preorders;
create policy "anyone can start a reservation" on preorders for insert with check (true);

drop policy if exists "anyone can register as a customer" on customers;
create policy "anyone can register as a customer" on customers for insert with check (true);

-- Admin: full read/write across everything, gated by admin_profiles membership.
drop policy if exists "admins manage categories" on categories;
create policy "admins manage categories" on categories for all using (is_admin()) with check (is_admin());

drop policy if exists "admins manage products" on products;
create policy "admins manage products" on products for all using (is_admin()) with check (is_admin());

drop policy if exists "admins view customers" on customers;
create policy "admins view customers" on customers for select using (is_admin());

drop policy if exists "admins manage orders" on orders;
create policy "admins manage orders" on orders for all using (is_admin()) with check (is_admin());

drop policy if exists "admins manage order items" on order_items;
create policy "admins manage order items" on order_items for all using (is_admin()) with check (is_admin());

drop policy if exists "admins manage preorders" on preorders;
create policy "admins manage preorders" on preorders for all using (is_admin()) with check (is_admin());

drop policy if exists "admins moderate reviews" on reviews;
create policy "admins moderate reviews" on reviews for all using (is_admin()) with check (is_admin());

drop policy if exists "admins manage admin_profiles" on admin_profiles;
create policy "admins manage admin_profiles" on admin_profiles for all using (is_admin()) with check (is_admin());

-- ---------------------------------------------------------------------------
-- Realtime (powers live "new order" / low-stock notifications in the admin panel)
-- ---------------------------------------------------------------------------

do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and tablename = 'orders'
  ) then
    alter publication supabase_realtime add table orders;
  end if;

  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and tablename = 'products'
  ) then
    alter publication supabase_realtime add table products;
  end if;
end $$;

-- Ship the full previous row on UPDATE events (not just the primary key), so
-- the admin panel can tell "stock just crossed the low-stock threshold" from
-- "stock changed but was already low" instead of alerting on every edit.
alter table products replica identity full;
