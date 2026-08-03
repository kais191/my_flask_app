-- Beauty House — seed data
-- Mirrors src/lib/mock-data.ts so the site looks the same the moment you
-- switch it over to Supabase. Run after schema.sql. Safe to re-run.

insert into categories (slug, name, sort_order) values
  ('makeup', 'Makeup', 1),
  ('skincare', 'Skincare', 2),
  ('handbags', 'Handbags', 3)
on conflict (slug) do nothing;

insert into products (
  slug, name, category_id, brand, price, cost, stock_quantity, low_stock_threshold,
  bestseller, rating, review_count, variants, concerns
)
select
  v.slug, v.name, c.id, v.brand, v.price, v.cost, v.stock_quantity, v.low_stock_threshold,
  v.bestseller, v.rating, v.review_count, v.variants, v.concerns
from (values
  ('silk-veil-blush', 'Silk Veil Blush', 'makeup', null::text, 28.00, 9.00, 42, 10, true, 4.8, 214,
    array['Petal', 'Rosewood', 'Terracotta', 'Berry'], array['everyday-glam', 'date-night']),
  ('dew-drop-serum', 'Dew Drop Serum', 'skincare', null, 46.00, 17.00, 8, 10, false, 4.7, 132,
    null, array['glowy-skin']),
  ('petite-top-handle', 'Petite Top-Handle', 'handbags', 'Coach', 118.00, 52.00, 5, 6, false, 4.9, 58,
    array['Cream', 'Blush', 'Espresso'], array['everyday-glam', 'office-ready']),
  ('velvet-matte-rouge', 'Velvet Matte Rouge', 'makeup', null, 24.00, 8.00, 3, 10, false, 4.6, 301,
    array['Blush Nude', 'Cherry', 'Mauve', 'Brick'], array['date-night', 'everyday-glam']),
  ('barely-there-tint', 'Barely-There Tint', 'skincare', null, 22.00, 7.00, 30, 10, false, 4.5, 89,
    null, array['glowy-skin', 'office-ready']),
  ('structured-tote', 'Structured Tote', 'handbags', 'Michael Kors', 168.00, 74.00, 12, 6, false, 4.8, 41,
    array['Oat', 'Moss', 'Black'], array['office-ready'])
) as v(slug, name, category_slug, brand, price, cost, stock_quantity, low_stock_threshold,
       bestseller, rating, review_count, variants, concerns)
join categories c on c.slug = v.category_slug
on conflict (slug) do nothing;
