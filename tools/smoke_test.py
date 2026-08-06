#!/usr/bin/env python3
"""End-to-end smoke test.

Walks every public route and then drives a complete purchase — basket,
discount code, delivery details, payment, confirmation and tracking — before
checking the admin dashboard. Run from the project root:

    python3 tools/smoke_test.py
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a throwaway database so a test run never touches real orders.
_TMP_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP_DB.close()
os.environ["DATABASE_URL"] = "sqlite:///" + _TMP_DB.name
os.environ["SECRET_KEY"] = "smoke-test"

from nestedblooms import create_app  # noqa: E402
from nestedblooms.extensions import db  # noqa: E402
from nestedblooms.models import Collection, Occasion, Order, Product  # noqa: E402
from nestedblooms.seed import seed_all  # noqa: E402

PASSED = 0
FAILED = []


def check(label, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED.append(label)
        print(f"  \033[31m✗\033[0m {label} {detail}")


def text(response):
    """Response body with HTML entities resolved.

    Jinja escapes apostrophes to &#39;, so asserting on copy like "isn't
    valid" fails against the raw bytes.
    """
    import html

    return html.unescape(response.get_data(as_text=True))


def get(client, path, expect=200, label=None):
    response = client.get(path, follow_redirects=False)
    check(
        label or f"GET {path}",
        response.status_code == expect,
        f"(got {response.status_code}, expected {expect})",
    )
    return response


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_all(verbose=False)
        products = Product.query.order_by(Product.position).all()
        collections = Collection.query.all()
        occasions = Occasion.query.all()
        first = products[0]
        second = products[5]
        first_id, second_id = first.id, second.id
        first_slug, first_price = first.slug, first.price

    client = app.test_client()

    print("\n\033[1mPublic pages\033[0m")
    for path in [
        "/", "/flowers", "/occasions", "/about", "/delivery", "/faq",
        "/reviews", "/contact", "/corporate", "/weddings", "/terms",
        "/privacy", "/returns", "/basket", "/login", "/register",
        "/checkout/track", "/search?q=rose", "/robots.txt", "/sitemap.xml",
    ]:
        get(client, path)

    get(client, "/this-page-does-not-exist", expect=404)

    print("\n\033[1mCatalogue\033[0m")
    for collection in collections:
        get(client, f"/flowers/{collection.slug}")
    for occasion in occasions:
        get(client, f"/occasions/{occasion.slug}")
    print(f"  … {len(products)} product pages")
    broken = []
    for product in products:
        if client.get(f"/product/{product.slug}").status_code != 200:
            broken.append(product.slug)
    check("every product page renders", not broken, f"broken: {broken}")

    print("\n\033[1mArtwork files exist\033[0m")
    static_dir = os.path.join(app.root_path, "..", "static")
    missing = [
        p.slug for p in products
        if not os.path.exists(os.path.join(static_dir, "img", "products", f"{p.slug}.svg"))
    ]
    check("all product illustrations present", not missing, f"missing: {missing}")

    # SVG is XML — an unescaped "&" renders as a blank image in the browser
    # while still passing an existence check.
    import glob
    import xml.etree.ElementTree as ElementTree

    malformed = []
    for path in glob.glob(os.path.join(static_dir, "img", "**", "*.svg"), recursive=True):
        try:
            ElementTree.parse(path)
        except ElementTree.ParseError:
            malformed.append(os.path.basename(path))
    check("all artwork is well-formed XML", not malformed, f"malformed: {malformed}")

    print("\n\033[1mFiltering, sorting and pagination\033[0m")
    get(client, "/flowers?sort=price-asc")
    get(client, "/flowers?sort=price-desc&price=under-50")
    get(client, "/flowers?page=2")
    get(client, "/flowers?page=999", label="GET /flowers?page=999 (empty page)")
    get(client, "/flowers?sort=nonsense", label="GET /flowers with bad sort")

    response = client.get("/flowers?price=under-50")
    # Only the product-card prices — the page also shows delivery and
    # free-delivery-threshold figures.
    prices = [
        float(p) for p in
        re.findall(r'class="card__price">€([\d.,]+)<', text(response))
    ]
    check(
        "price filter excludes expensive items",
        prices and all(p < 50 for p in prices),
        f"(found {prices})",
    )

    print("\n\033[1mBasket\033[0m")
    client.post("/basket/add", data={
        "product_id": first_id, "size": "deluxe",
        "addons": ["chocolates", "prosecco"], "quantity": 2,
    })
    response = client.get("/basket")
    body = text(response)
    check("basket shows the added product", first.name in body)
    check("basket shows the chosen size", "Deluxe" in body)
    check("basket shows add-ons", "Belgian Chocolates" in body)

    # 2 × (base + deluxe 1500 + chocolates 1295 + prosecco 1495)
    expected_line = 2 * (first_price + 1500 + 1295 + 1495)
    check(
        "line total is priced correctly",
        f"€{expected_line / 100:,.2f}" in body,
        f"expected €{expected_line / 100:,.2f}",
    )

    client.post("/basket/add", data={"product_id": second_id, "quantity": 1})
    client.post("/basket/add", data={"product_id": second_id, "quantity": 1})
    body = text(client.get("/basket"))
    check("re-adding the same line stacks quantity", "€" in body)

    print("\n\033[1mDiscount codes\033[0m")
    client.post("/basket/coupon", data={"code": "NOPE"})
    check("invalid code is rejected", "isn't a valid" in text(client.get("/basket")))

    client.post("/basket/coupon", data={"code": "WELCOME10"})
    body = text(client.get("/basket"))
    check("valid code is applied", "WELCOME10" in body and "Discount" in body)

    print("\n\033[1mCheckout\033[0m")
    get(client, "/checkout/")

    # Missing fields should come back with errors rather than an order.
    response = client.post("/checkout/", data={"customer_name": ""})
    check("empty checkout form is rejected", "Please check the highlighted" in text(response))

    delivery_day = (date.today() + timedelta(days=3)).isoformat()
    details = {
        "customer_name": "Cara Nolan",
        "customer_email": "cara@example.ie",
        "customer_phone": "0851234567",
        "recipient_name": "Bridget Nolan",
        "recipient_phone": "0879876543",
        "address_line1": "14 Marlborough Road",
        "address_line2": "",
        "city": "Rathmines",
        "county": "Dublin",
        "eircode": "D06 X284",
        "delivery_notes": "Leave with next door if out",
        "card_message": "Happy birthday Mam, wish I could be there. — Cara",
        "delivery_option": "standard",
        "delivery_date": delivery_day,
    }
    response = client.post("/checkout/", data=details)
    check("valid details advance to payment", response.headers.get("Location", "").endswith("/payment"))

    # A past date must not be accepted.
    past = dict(details, delivery_date=(date.today() - timedelta(days=1)).isoformat())
    response = client.post("/checkout/", data=past)
    check("past delivery date is rejected", "earliest we can deliver" in text(response))
    client.post("/checkout/", data=details)  # restore good details

    get(client, "/checkout/payment")

    response = client.post("/checkout/payment", data={
        "card_name": "Cara Nolan", "card_number": "4242 4242 4242 4241",
        "card_expiry": "12/30", "card_cvc": "123", "terms": "on",
    })
    check("card failing the Luhn check is rejected", "doesn't check out" in text(response))

    response = client.post("/checkout/payment", data={
        "card_name": "Cara Nolan", "card_number": "4242 4242 4242 4242",
        "card_expiry": "01/20", "card_cvc": "123", "terms": "on",
    })
    check("expired card is rejected", "has expired" in text(response))

    response = client.post("/checkout/payment", data={
        "card_name": "Cara Nolan", "card_number": "4242 4242 4242 4242",
        "card_expiry": "12/30", "card_cvc": "123", "terms": "on",
    })
    location = response.headers.get("Location", "")
    check("valid payment places the order", "/confirmation/" in location, f"(got {location})")

    reference = location.rsplit("/", 1)[-1] if "/confirmation/" in location else None
    if reference:
        response = client.get(f"/checkout/confirmation/{reference}")
        body = text(response)
        check("confirmation page renders", response.status_code == 200)
        check("confirmation shows the reference", reference in body)
        check("confirmation shows the card message", "wish I could be there" in body)

        body = text(client.get("/basket"))
        check("basket is emptied after ordering", "Your basket is empty" in body)

        with app.app_context():
            order = Order.query.filter_by(reference=reference).first()
            check("order was persisted", order is not None)
            check("order has line items", order and len(order.items) >= 2)
            check("discount was recorded", order and order.discount > 0)
            check(
                "total equals subtotal + delivery − discount",
                order and order.total == order.subtotal + order.delivery_fee - order.discount,
                f"({order.subtotal} + {order.delivery_fee} - {order.discount} != {order.total})",
            )
            check("card message stored", order and "Cara" in (order.card_message or ""))

        print("\n\033[1mOrder tracking\033[0m")
        response = client.post("/checkout/track", data={
            "reference": reference, "email": "cara@example.ie",
        })
        check("tracking finds the order", reference in text(response))

        response = client.post("/checkout/track", data={
            "reference": reference, "email": "wrong@example.ie",
        })
        check("tracking rejects a mismatched email", "couldn't find an order" in text(response))

    print("\n\033[1mAccounts\033[0m")
    fresh = app.test_client()
    response = fresh.post("/register", data={
        "first_name": "Sean", "last_name": "Byrne", "email": "sean@example.ie",
        "phone": "0861112222", "password": "longenough1", "confirm": "longenough1",
    })
    check("registration succeeds", response.status_code == 302)
    check("account page loads when signed in", fresh.get("/account").status_code == 200)

    response = fresh.post("/register", data={
        "first_name": "A", "last_name": "B", "email": "sean@example.ie",
        "password": "longenough1", "confirm": "longenough1",
    })
    check("duplicate email is refused", response.status_code in (200, 302))

    short = app.test_client()
    response = short.post("/register", data={
        "first_name": "A", "last_name": "B", "email": "new@example.ie",
        "password": "short", "confirm": "short",
    })
    check("short password is refused", "at least 8 characters" in text(response))

    fresh.get("/logout")
    check("account redirects when signed out", fresh.get("/account").status_code == 302)

    response = fresh.post("/login", data={"email": "sean@example.ie", "password": "wrong"})
    check("wrong password is refused", "don't match an account" in text(response))

    response = fresh.post("/login", data={"email": "sean@example.ie", "password": "longenough1"})
    check("correct password signs in", response.status_code == 302)

    print("\n\033[1mAdmin\033[0m")
    anon = app.test_client()
    check("admin is hidden from guests", anon.get("/admin/").status_code == 302)
    check("admin is hidden from ordinary users", fresh.get("/admin/").status_code == 404)

    admin = app.test_client()
    admin.post("/login", data={
        "email": app.config["ADMIN_EMAIL"], "password": app.config["ADMIN_PASSWORD"],
    })
    for path in ["/admin/", "/admin/orders", "/admin/products", "/admin/messages", "/admin/reviews"]:
        get(admin, path)

    if reference:
        get(admin, f"/admin/orders/{reference}")
        admin.post(f"/admin/orders/{reference}/status", data={"status": "out_for_delivery"})
        with app.app_context():
            order = Order.query.filter_by(reference=reference).first()
            check("admin can change order status", order.status == "out_for_delivery")

    print("\n\033[1mForms\033[0m")
    response = client.post("/contact", data={
        "name": "Test Person", "email": "test@example.ie",
        "subject": "General enquiry", "message": "Do you deliver to Leitrim?",
    })
    check("contact form accepts a valid message", response.status_code == 302)

    response = client.post("/contact", data={"name": "", "email": "bad", "message": ""})
    check("contact form rejects bad input", response.status_code == 200)

    response = client.post("/newsletter", data={"email": "sub@example.ie"})
    check("newsletter signup works", response.status_code == 302)

    response = client.post(f"/product/{first_slug}/review", data={
        "author": "Reviewer", "rating": "5", "body": "Lovely flowers.",
    })
    check("review submission works", response.status_code == 302)

    print("\n" + "=" * 58)
    if FAILED:
        print(f"\033[31m{len(FAILED)} failed\033[0m, {PASSED} passed")
        for label in FAILED:
            print(f"  · {label}")
    else:
        print(f"\033[32mAll {PASSED} checks passed\033[0m")
    print("=" * 58)

    os.unlink(_TMP_DB.name)
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
