"""Homepage, editorial pages and local delivery landing pages."""

from __future__ import annotations

import re

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import func

from .. import catalog
from ..extensions import db
from ..models import (
    Collection, ContactMessage, NewsletterSubscriber, Occasion, Product, Review,
)

bp = Blueprint("main", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(value):
    return bool(value and EMAIL_RE.match(value.strip()))


@bp.route("/")
def index():
    bestsellers = (
        Product.query.filter(
            Product.is_active.is_(True), Product.badges.like("%bestseller%")
        )
        .order_by(Product.position)
        .limit(8)
        .all()
    )
    collections = Collection.query.order_by(Collection.position).all()
    occasions = Occasion.query.order_by(Occasion.position).limit(8).all()

    return render_template(
        "index.html",
        bestsellers=bestsellers,
        collections=collections,
        occasions=occasions,
        testimonials=catalog.TESTIMONIALS[:3],
        delivery_options=catalog.DELIVERY_OPTIONS,
    )


@bp.route("/about")
def about():
    return render_template("pages/about.html")


@bp.route("/delivery")
def delivery():
    return render_template(
        "pages/delivery.html",
        delivery_options=catalog.DELIVERY_OPTIONS,
        areas=catalog.DELIVERY_AREAS,
        faqs=[f for f in catalog.FAQS if f["category"] == "Delivery"],
    )


@bp.route("/faq")
def faq():
    categories = []
    for entry in catalog.FAQS:
        if entry["category"] not in categories:
            categories.append(entry["category"])
    grouped = [
        (name, [f for f in catalog.FAQS if f["category"] == name])
        for name in categories
    ]
    return render_template("pages/faq.html", grouped=grouped)


@bp.route("/reviews")
def reviews():
    recent = (
        Review.query.filter_by(is_approved=True)
        .order_by(Review.created_at.desc())
        .limit(24)
        .all()
    )
    average = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.is_approved.is_(True))
        .scalar()
    )
    total = Review.query.filter_by(is_approved=True).count()
    return render_template(
        "pages/reviews.html",
        reviews=recent,
        testimonials=catalog.TESTIMONIALS,
        average=round(average, 1) if average else None,
        total=total,
    )


@bp.route("/corporate")
def corporate():
    return render_template("pages/corporate.html")


@bp.route("/weddings")
def weddings():
    return render_template("pages/weddings.html")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = {}
    if request.method == "POST":
        form = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "subject": request.form.get("subject", "").strip(),
            "message": request.form.get("message", "").strip(),
        }
        errors = []
        if not form["name"]:
            errors.append("Please tell us your name.")
        if not valid_email(form["email"]):
            errors.append("Please enter a valid email address.")
        if not form["message"]:
            errors.append("Please include a message.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            db.session.add(ContactMessage(
                name=form["name"],
                email=form["email"],
                phone=form["phone"],
                subject=form["subject"] or "General enquiry",
                message=form["message"],
            ))
            db.session.commit()
            flash(
                "Thanks — your message is with the studio. We reply to "
                "everything within one working day.",
                "success",
            )
            return redirect(url_for("main.contact"))

    return render_template("pages/contact.html", form=form)


@bp.route("/newsletter", methods=["POST"])
def newsletter():
    email = request.form.get("email", "").strip().lower()
    next_url = request.form.get("next") or url_for("main.index")

    if not valid_email(email):
        flash("That email address doesn't look right.", "danger")
        return redirect(next_url)

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        flash("You're already on the list — thank you!", "info")
    else:
        db.session.add(NewsletterSubscriber(email=email))
        db.session.commit()
        flash(
            "Welcome to Nested Blooms. Use code WELCOME10 for 10% off your "
            "first order.",
            "success",
        )
    return redirect(next_url)


@bp.route("/flower-delivery/<slug>")
def delivery_area(slug):
    area = next((a for a in catalog.DELIVERY_AREAS if a["slug"] == slug), None)
    if area is None:
        abort(404)

    featured = (
        Product.query.filter(Product.is_active.is_(True))
        .order_by(Product.position)
        .limit(4)
        .all()
    )
    return render_template(
        "pages/delivery_area.html",
        area=area,
        featured=featured,
        delivery_options=catalog.DELIVERY_OPTIONS,
    )


@bp.route("/terms")
def terms():
    return render_template("pages/legal.html", page="terms")


@bp.route("/privacy")
def privacy():
    return render_template("pages/legal.html", page="privacy")


@bp.route("/returns")
def returns():
    return render_template("pages/legal.html", page="returns")


@bp.route("/robots.txt")
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /basket",
        "Disallow: /checkout",
        "Disallow: /account",
        f"Sitemap: {url_for('main.sitemap', _external=True)}",
    ]
    return "\n".join(lines), 200, {"Content-Type": "text/plain"}


@bp.route("/sitemap.xml")
def sitemap():
    urls = [
        url_for("main.index", _external=True),
        url_for("shop.collections", _external=True),
        url_for("main.about", _external=True),
        url_for("main.delivery", _external=True),
        url_for("main.faq", _external=True),
        url_for("main.reviews", _external=True),
        url_for("main.contact", _external=True),
        url_for("main.corporate", _external=True),
        url_for("main.weddings", _external=True),
    ]
    urls += [
        url_for("shop.collection", slug=c.slug, _external=True)
        for c in Collection.query.all()
    ]
    urls += [
        url_for("shop.occasion", slug=o.slug, _external=True)
        for o in Occasion.query.all()
    ]
    urls += [
        url_for("shop.product", slug=p.slug, _external=True)
        for p in Product.query.filter_by(is_active=True).all()
    ]
    urls += [
        url_for("main.delivery_area", slug=a["slug"], _external=True)
        for a in catalog.DELIVERY_AREAS
    ]

    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>"
    )
    return xml, 200, {"Content-Type": "application/xml"}
