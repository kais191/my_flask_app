"""Pricing, basket and delivery-scheduling helpers.

Everything money-related happens here in integer cents. The basket itself
lives in the session so that guests can shop without an account.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from flask import session

from . import catalog
from .models import Product

try:  # Python 3.9+
    from zoneinfo import ZoneInfo

    DUBLIN = ZoneInfo("Europe/Dublin")
except Exception:  # pragma: no cover - fallback if tzdata is unavailable
    DUBLIN = None

CART_KEY = "cart"
COUPON_KEY = "coupon"

# Counties our own drivers cover, and which therefore qualify for same-day.
SAME_DAY_COUNTIES = {"dublin", "kildare", "wicklow"}
SAME_DAY_CUTOFF_HOUR = 14  # 2pm
NEXT_DAY_CUTOFF_HOUR = 16  # 4pm


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def money(cents):
    """Format integer cents as a euro string."""
    if cents is None:
        return "€0.00"
    return f"€{cents / 100:,.2f}"


def now_local():
    return datetime.now(DUBLIN) if DUBLIN else datetime.now()


# ---------------------------------------------------------------------------
# Catalogue option lookups
# ---------------------------------------------------------------------------

def size_options():
    return catalog.SIZE_OPTIONS


def size_for(code):
    for option in catalog.SIZE_OPTIONS:
        if option["code"] == code:
            return option
    return catalog.SIZE_OPTIONS[0]


def addon_options():
    return catalog.ADDONS


def addon_for(code):
    for option in catalog.ADDONS:
        if option["code"] == code:
            return option
    return None


def delivery_options():
    return catalog.DELIVERY_OPTIONS


def delivery_option_for(code):
    for option in catalog.DELIVERY_OPTIONS:
        if option["code"] == code:
            return option
    return catalog.DELIVERY_OPTIONS[0]


# ---------------------------------------------------------------------------
# Delivery scheduling
# ---------------------------------------------------------------------------

def same_day_available(county=None):
    """Same-day runs on our own vans, so it is both time- and area-limited."""
    if now_local().hour >= SAME_DAY_CUTOFF_HOUR:
        return False
    if county is None:
        return True
    return county.strip().lower().replace("co. ", "").replace("county ", "") in (
        SAME_DAY_COUNTIES
    )


def earliest_delivery_date(option_code="standard", county=None):
    today = now_local().date()
    if option_code == "sameday" and same_day_available(county):
        return today
    # Anything else is next-day, and next-day itself has a 4pm cut-off.
    offset = 1 if now_local().hour < NEXT_DAY_CUTOFF_HOUR else 2
    return today + timedelta(days=offset)


def delivery_calendar(option_code="standard", county=None, days=60):
    """Dates offered in the checkout date picker."""
    start = earliest_delivery_date(option_code, county)
    return [start + timedelta(days=i) for i in range(days)]


def parse_delivery_date(value):
    """Parse an ISO date from a form, returning ``None`` when unusable."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# Basket
# ---------------------------------------------------------------------------

def line_key(product_id, size_code, addon_codes):
    """Identity for a basket line: same product+size+extras stacks together."""
    return f"{product_id}:{size_code}:{','.join(sorted(addon_codes))}"


def unit_price_for(product, size_code, addon_codes):
    price = product.price + size_for(size_code)["delta"]
    for code in addon_codes:
        addon = addon_for(code)
        if addon:
            price += addon["price"]
    return price


def raw_cart():
    return session.get(CART_KEY, [])


def save_cart(lines):
    session[CART_KEY] = lines
    session.modified = True


def add_to_cart(product_id, size_code="classic", addon_codes=(), quantity=1):
    addon_codes = [c for c in addon_codes if addon_for(c)]
    key = line_key(product_id, size_code, addon_codes)
    lines = raw_cart()
    for line in lines:
        if line["key"] == key:
            line["qty"] = min(99, line["qty"] + quantity)
            break
    else:
        lines.append({
            "key": key,
            "product_id": product_id,
            "size": size_code,
            "addons": list(addon_codes),
            "qty": max(1, min(99, quantity)),
        })
    save_cart(lines)


def update_cart_line(key, quantity):
    lines = [line for line in raw_cart() if line["key"] != key or quantity > 0]
    for line in lines:
        if line["key"] == key:
            line["qty"] = max(1, min(99, quantity))
    save_cart(lines)


def remove_cart_line(key):
    save_cart([line for line in raw_cart() if line["key"] != key])


def clear_cart():
    session.pop(CART_KEY, None)
    session.pop(COUPON_KEY, None)
    session.modified = True


def cart_items():
    """Resolve the session basket into rich rows, dropping stale products."""
    lines = raw_cart()
    if not lines:
        return []

    products = {
        p.id: p
        for p in Product.query.filter(
            Product.id.in_([line["product_id"] for line in lines])
        ).all()
    }

    items = []
    changed = False
    for line in list(lines):
        product = products.get(line["product_id"])
        if product is None or not product.is_active:
            lines.remove(line)
            changed = True
            continue
        size = size_for(line["size"])
        addons = [addon_for(c) for c in line["addons"] if addon_for(c)]
        unit = unit_price_for(product, line["size"], line["addons"])
        items.append({
            "key": line["key"],
            "product": product,
            "size": size,
            "addons": addons,
            "quantity": line["qty"],
            "unit_price": unit,
            "line_total": unit * line["qty"],
        })
    if changed:
        save_cart(lines)
    return items


def cart_count():
    return sum(line["qty"] for line in raw_cart())


def active_coupon():
    """Return the Coupon currently applied to the session, if still valid."""
    from .models import Coupon

    code = session.get(COUPON_KEY)
    if not code:
        return None
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if coupon is None:
        session.pop(COUPON_KEY, None)
    return coupon


def cart_totals(items=None, delivery_code="standard", coupon=None):
    """Compute the full price breakdown for a basket."""
    items = cart_items() if items is None else items
    coupon = active_coupon() if coupon is None else coupon

    subtotal = sum(item["line_total"] for item in items)
    option = delivery_option_for(delivery_code)
    delivery_fee = option["price"] if items else 0

    # Free standard delivery over the threshold; upgrades still cost the
    # difference rather than becoming free outright.
    free_delivery_earned = subtotal >= catalog.FREE_DELIVERY_THRESHOLD
    if free_delivery_earned:
        delivery_fee = max(0, delivery_fee - catalog.DELIVERY_OPTIONS[0]["price"])

    item_discount = delivery_discount = 0
    coupon_applied = False
    if coupon is not None:
        item_discount, delivery_discount = coupon.discount_for(subtotal, delivery_fee)
        coupon_applied = bool(item_discount or delivery_discount)

    discount = item_discount + delivery_discount
    total = max(0, subtotal + delivery_fee - discount)

    return {
        "items": items,
        "count": sum(item["quantity"] for item in items),
        "subtotal": subtotal,
        "delivery_option": option,
        "delivery_fee": delivery_fee,
        "free_delivery_earned": free_delivery_earned,
        "free_delivery_threshold": catalog.FREE_DELIVERY_THRESHOLD,
        "remaining_for_free": max(
            0, catalog.FREE_DELIVERY_THRESHOLD - subtotal
        ),
        "coupon": coupon,
        "coupon_applied": coupon_applied,
        "discount": discount,
        "total": total,
    }
