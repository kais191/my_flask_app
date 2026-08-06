# Nested Blooms

A complete, working flower-delivery shop built with Flask — modelled on the
structure of an Irish online florist. It covers the whole commercial path:
browsing, a configurable product page, a basket, discount codes, a scheduled
delivery checkout, order tracking, customer accounts and a back-office for
running the shop.

Everything is self-contained. There are no CDNs, no webfonts and no external
image hosts — all 53 illustrations are generated as SVG by a script in this
repository, so the site works offline and deploys anywhere.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:8000>. The database is created and seeded with the
full catalogue on first run.

The seeded administrator is `admin@nestedblooms.ie` / `bloom-admin-2024`
(override with the `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables).
Sign in with it and the studio dashboard appears at `/admin`.

## What's in the shop

- **33 arrangements** across 7 collections (hatboxes, hand-tied bouquets, vase
  arrangements, baskets, luxury, plants, gift sets) and 10 gifting occasions.
- **Three sizes** per bouquet and six paid add-ons, priced live on the page.
- **Discount codes** — `WELCOME10`, `BLOOM20`, `FREEPOST`, `NEST15`.
- **Delivery scheduling** with real cut-off logic: same-day for Dublin, Kildare
  and Wicklow before 2pm; next-day nationwide before 4pm; any date up to ninety
  days ahead.
- **Guest checkout** plus optional accounts with saved addresses and order
  history, and order tracking by reference for everyone.

## Project layout

```
app.py                     Entry point — creates the app, seeds on first run
nestedblooms/
  __init__.py              Application factory, template globals, CLI commands
  config.py                Configuration (SQLite by default, DATABASE_URL aware)
  catalog.py               Single source of truth for all merchandising data
  models.py                SQLAlchemy models — money stored in integer cents
  utils.py                 Pricing, basket and delivery-date logic
  seed.py                  Idempotent database seeding
  blueprints/
    main.py                Homepage, editorial pages, city landing pages, SEO
    shop.py                Listings, filtering, product detail, search, reviews
    cart.py                Basket and discount codes
    checkout.py            Delivery details, payment, confirmation, tracking
    auth.py                Registration, sign-in, customer account
    admin.py               Studio dashboard
templates/                 Jinja templates
static/css/style.css       The whole design system, one file
static/js/main.js          Progressive enhancement only — nothing required
static/img/                Generated SVG artwork
tools/
  generate_art.py          Procedural SVG bouquet generator
  smoke_test.py            End-to-end test suite
```

## The artwork

`tools/generate_art.py` draws every bouquet on the site. Flowers are built from
parameterised petal geometry — thirteen species including roses, peonies,
tulips, lilies, hydrangea, orchids and gypsophila — then composed into a domed
arrangement inside one of five vessels (hatbox, wrapped cone, vase, basket,
pot). The recipe for each product lives beside its price and copy in
`catalog.py`.

Two details keep the output looking deliberate rather than generated: bloom
counts are solved for a target coverage of the dome, so an arrangement is
always full regardless of how the recipe was written, and each species has a
fill factor describing how much of its bounding circle it actually inks, so
airy flowers such as daisies get more stems than dense ones like hydrangea.

Regenerate everything with:

```bash
python3 tools/generate_art.py
```

It needs only the standard library.

## Tests

```bash
python3 tools/smoke_test.py
```

Runs 90-plus checks against a throwaway database: every public route, all 33
product pages, artwork integrity, filtering and pagination, basket pricing,
discount codes, checkout validation (including Luhn and expiry checks on the
card form and rejection of past delivery dates), a complete purchase, order
tracking, account handling and admin authorisation.

## Payments

The checkout deliberately stops short of a real payment provider. Card details
are validated client- and server-side and then discarded — nothing is stored
and no charge is made. To go live, replace `_validate_payment` in
`nestedblooms/blueprints/checkout.py` with a call to a provider's hosted
fields (Stripe Elements or similar) and create the order on their webhook.

## Deploying

The app reads `DATABASE_URL` (PostgreSQL included; the legacy `postgres://`
scheme is rewritten automatically) and falls back to SQLite. Set these in
production:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Signs the session cookie. **Required in production.** |
| `DATABASE_URL` | Database connection string. Defaults to local SQLite. |
| `SESSION_COOKIE_SECURE` | Set to `1` when serving over HTTPS. |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Credentials for the seeded admin account. |

The `Procfile` runs the seeder on release and serves the app with gunicorn.
