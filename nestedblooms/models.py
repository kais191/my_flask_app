"""Database models for the Nested Blooms shop.

All monetary values are integers in euro cents. Storing money as a float is
the classic way to end up with an order totalling €64.94999999.
"""

from __future__ import annotations

import secrets
from datetime import datetime, date

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

# Many-to-many: a bouquet can suit several occasions.
product_occasions = db.Table(
    "product_occasions",
    db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),
    db.Column("occasion_id", db.Integer, db.ForeignKey("occasion.id"), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    orders = db.relationship(
        "Order", back_populates="user", lazy="select",
        order_by="Order.created_at.desc()",
    )
    addresses = db.relationship(
        "Address", back_populates="user", cascade="all, delete-orphan",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def __repr__(self):
        return f"<User {self.email}>"


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label = db.Column(db.String(60), default="Home")
    recipient_name = db.Column(db.String(140), nullable=False)
    line1 = db.Column(db.String(190), nullable=False)
    line2 = db.Column(db.String(190))
    city = db.Column(db.String(120), nullable=False)
    county = db.Column(db.String(120), nullable=False)
    eircode = db.Column(db.String(20))
    phone = db.Column(db.String(40))

    user = db.relationship("User", back_populates="addresses")

    @property
    def one_line(self):
        parts = [self.line1, self.line2, self.city, self.county, self.eircode]
        return ", ".join(p for p in parts if p)


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    headline = db.Column(db.String(200))
    blurb = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)

    products = db.relationship(
        "Product", back_populates="collection", order_by="Product.position",
    )

    @property
    def image(self):
        return f"img/collections/{self.slug}.svg"


class Occasion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    blurb = db.Column(db.String(255))
    position = db.Column(db.Integer, default=0)

    products = db.relationship(
        "Product", secondary=product_occasions, back_populates="occasions",
    )

    @property
    def image(self):
        return f"img/occasions/{self.slug}.svg"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(140), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # cents
    blurb = db.Column(db.String(255))
    description = db.Column(db.Text)
    contains = db.Column(db.Text)
    badges = db.Column(db.String(140), default="")  # comma separated
    position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    collection = db.relationship("Collection", back_populates="products")
    occasions = db.relationship(
        "Occasion", secondary=product_occasions, back_populates="products",
    )
    reviews = db.relationship(
        "Review", back_populates="product", cascade="all, delete-orphan",
        order_by="Review.created_at.desc()",
    )

    @property
    def image(self):
        return f"img/products/{self.slug}.svg"

    @property
    def badge_list(self):
        return [b for b in (self.badges or "").split(",") if b]

    @property
    def rating(self):
        approved = [r.rating for r in self.reviews if r.is_approved]
        return round(sum(approved) / len(approved), 1) if approved else None

    @property
    def review_count(self):
        return sum(1 for r in self.reviews if r.is_approved)

    def __repr__(self):
        return f"<Product {self.slug}>"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120))
    rating = db.Column(db.Integer, nullable=False, default=5)
    title = db.Column(db.String(160))
    body = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product", back_populates="reviews")


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    kind = db.Column(db.String(20), nullable=False)  # percent | fixed | free_delivery
    value = db.Column(db.Integer, default=0)
    min_spend = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    times_used = db.Column(db.Integer, default=0, nullable=False)

    def discount_for(self, subtotal, delivery_fee):
        """Return (item_discount, delivery_discount) in cents."""
        if not self.is_active or subtotal < (self.min_spend or 0):
            return 0, 0
        if self.kind == "percent":
            return int(round(subtotal * self.value / 100.0)), 0
        if self.kind == "fixed":
            return min(self.value, subtotal), 0
        if self.kind == "free_delivery":
            return 0, delivery_fee
        return 0, 0


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(30), default="confirmed", nullable=False)

    customer_name = db.Column(db.String(140), nullable=False)
    customer_email = db.Column(db.String(190), nullable=False, index=True)
    customer_phone = db.Column(db.String(40))

    recipient_name = db.Column(db.String(140), nullable=False)
    recipient_phone = db.Column(db.String(40))
    address_line1 = db.Column(db.String(190), nullable=False)
    address_line2 = db.Column(db.String(190))
    city = db.Column(db.String(120), nullable=False)
    county = db.Column(db.String(120), nullable=False)
    eircode = db.Column(db.String(20))
    delivery_notes = db.Column(db.Text)

    delivery_date = db.Column(db.Date, nullable=False)
    delivery_option = db.Column(db.String(30), nullable=False, default="standard")
    delivery_fee = db.Column(db.Integer, default=0, nullable=False)
    card_message = db.Column(db.Text)

    subtotal = db.Column(db.Integer, default=0, nullable=False)
    discount = db.Column(db.Integer, default=0, nullable=False)
    total = db.Column(db.Integer, default=0, nullable=False)
    coupon_code = db.Column(db.String(40))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan",
    )

    STATUSES = [
        "confirmed", "in_studio", "out_for_delivery", "delivered", "cancelled",
    ]

    STATUS_LABELS = {
        "confirmed": "Order confirmed",
        "in_studio": "Being made in the studio",
        "out_for_delivery": "Out for delivery",
        "delivered": "Delivered",
        "cancelled": "Cancelled",
    }

    @staticmethod
    def new_reference():
        """A short, human-readable, non-sequential order reference."""
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        while True:
            ref = "NB-" + "".join(secrets.choice(alphabet) for _ in range(6))
            if not db.session.query(
                Order.query.filter_by(reference=ref).exists()
            ).scalar():
                return ref

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status.title())

    @property
    def delivery_address(self):
        parts = [
            self.address_line1, self.address_line2, self.city,
            self.county, self.eircode,
        ]
        return ", ".join(p for p in parts if p)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

    @property
    def is_upcoming(self):
        return self.delivery_date >= date.today() and self.status not in (
            "delivered", "cancelled",
        )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    # Denormalised so an order remains readable even if a product is renamed
    # or withdrawn from sale later.
    product_name = db.Column(db.String(140), nullable=False)
    product_slug = db.Column(db.String(120))
    size_code = db.Column(db.String(20), default="classic")
    size_name = db.Column(db.String(40), default="Classic")
    addons = db.Column(db.String(255), default="")  # comma separated codes
    addon_names = db.Column(db.String(400), default="")
    unit_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    line_total = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    @property
    def addon_name_list(self):
        return [a for a in (self.addon_names or "").split("|") if a]


class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(190), nullable=False)
    phone = db.Column(db.String(40))
    subject = db.Column(db.String(160))
    message = db.Column(db.Text, nullable=False)
    is_handled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
