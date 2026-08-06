"""Populate the database from the static catalogue.

Seeding is idempotent: running it against an existing database updates the
merchandising copy and prices in place rather than creating duplicates, so it
is safe to run on every deploy.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from flask import current_app

from . import catalog
from .extensions import db
from .models import (
    Collection, ContactMessage, Coupon, Occasion, Order, OrderItem, Product,
    Review, User,
)

# A pool of plausible review copy, distributed across products deterministically
# so the demo shop does not launch with empty review sections.
REVIEW_POOL = [
    (5, "Exactly as pictured", "Arrived beautifully packaged and looked even better than the photo. Lasted a full two weeks."),
    (5, "Delighted", "Ordered in the morning and they were delivered the same afternoon. My sister was thrilled."),
    (5, "Beautiful arrangement", "The florist rang to confirm the delivery time, which I really appreciated."),
    (4, "Lovely, slightly smaller than expected", "Genuinely gorgeous flowers, though I'd size up next time. Still very happy."),
    (5, "Will order again", "Second time using Nested Blooms and the quality has been spot on both times."),
    (5, "Great for a hospital gift", "Low scent and already in a vase, which was perfect for the ward."),
    (5, "Stunning", "The colours are so much richer in person. Handwritten card was a lovely touch."),
    (4, "Good value", "Plenty of stems for the price and they opened up nicely over a few days."),
]

REVIEWER_NAMES = [
    ("Aoife M.", "Dublin"), ("Cian D.", "Cork"), ("Niamh B.", "Galway"),
    ("Ruairí O.", "Limerick"), ("Saoirse L.", "Wicklow"), ("Eoin F.", "Kildare"),
    ("Méabh C.", "Meath"), ("Fionn T.", "Waterford"), ("Órla K.", "Sligo"),
    ("Darragh N.", "Belfast"), ("Clodagh R.", "Kilkenny"), ("Peter H.", "Dublin"),
]


def seed_all(verbose=True):
    """Create or refresh every catalogue row. Safe to re-run."""
    counts = {
        "collections": _seed_collections(),
        "occasions": _seed_occasions(),
        "products": _seed_products(),
        "coupons": _seed_coupons(),
        "reviews": _seed_reviews(),
        "admin": _seed_admin(),
    }
    db.session.commit()
    if verbose:
        summary = ", ".join(f"{k}: {v}" for k, v in counts.items())
        print(f"Seeded — {summary}")
    return counts


def _seed_collections():
    for entry in catalog.COLLECTIONS:
        row = Collection.query.filter_by(slug=entry["slug"]).first()
        if row is None:
            row = Collection(slug=entry["slug"])
            db.session.add(row)
        row.name = entry["name"]
        row.headline = entry["headline"]
        row.blurb = entry["blurb"]
        row.position = entry["position"]
    db.session.flush()
    return Collection.query.count()


def _seed_occasions():
    for entry in catalog.OCCASIONS:
        row = Occasion.query.filter_by(slug=entry["slug"]).first()
        if row is None:
            row = Occasion(slug=entry["slug"])
            db.session.add(row)
        row.name = entry["name"]
        row.blurb = entry["blurb"]
        row.position = entry["position"]
    db.session.flush()
    return Occasion.query.count()


def _seed_products():
    collections = {c.slug: c for c in Collection.query.all()}
    occasions = {o.slug: o for o in Occasion.query.all()}

    for position, entry in enumerate(catalog.PRODUCTS):
        row = Product.query.filter_by(slug=entry["slug"]).first()
        if row is None:
            row = Product(slug=entry["slug"])
            db.session.add(row)
        row.name = entry["name"]
        row.collection = collections[entry["collection"]]
        row.price = entry["price"]
        row.blurb = entry["blurb"]
        row.description = entry["description"]
        row.contains = entry["contains"]
        row.badges = ",".join(entry.get("badges", []))
        row.position = position
        row.is_active = True
        row.occasions = [
            occasions[slug] for slug in entry["occasions"] if slug in occasions
        ]
    db.session.flush()
    return Product.query.count()


def _seed_coupons():
    for entry in catalog.COUPONS:
        row = Coupon.query.filter_by(code=entry["code"]).first()
        if row is None:
            row = Coupon(code=entry["code"])
            db.session.add(row)
        row.description = entry["description"]
        row.kind = entry["kind"]
        row.value = entry["value"]
        row.min_spend = entry["min_spend"]
        row.is_active = True
    db.session.flush()
    return Coupon.query.count()


def _seed_reviews():
    """Give each product a small, stable set of reviews."""
    if Review.query.count():
        return Review.query.count()

    now = datetime.utcnow()
    for product in Product.query.all():
        rng = random.Random(product.slug)
        for i in range(rng.randint(2, 5)):
            rating, title, body = rng.choice(REVIEW_POOL)
            author, location = rng.choice(REVIEWER_NAMES)
            db.session.add(Review(
                product=product,
                author=author,
                location=location,
                rating=rating,
                title=title,
                body=body,
                created_at=now - timedelta(days=rng.randint(3, 400)),
            ))
    db.session.flush()
    return Review.query.count()


def _seed_admin():
    """Ensure an administrator exists so the dashboard is reachable."""
    email = current_app.config["ADMIN_EMAIL"]
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            first_name="Studio",
            last_name="Manager",
            email=email,
            is_admin=True,
        )
        user.set_password(current_app.config["ADMIN_PASSWORD"])
        db.session.add(user)
    else:
        user.is_admin = True
    db.session.flush()
    return email


def reset_all():
    """Drop and rebuild every table. Destructive — development only."""
    db.drop_all()
    db.create_all()
    return seed_all()
