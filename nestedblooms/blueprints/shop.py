"""Product listings, filtering and product detail pages."""

from __future__ import annotations

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, session, url_for,
)
from sqlalchemy import or_

from .. import catalog
from ..extensions import db
from ..models import Collection, Occasion, Product, Review, User
from ..utils import addon_options, size_options

bp = Blueprint("shop", __name__)

PER_PAGE = 12

SORT_OPTIONS = {
    "featured": ("Featured", Product.position.asc()),
    "price-asc": ("Price: low to high", Product.price.asc()),
    "price-desc": ("Price: high to low", Product.price.desc()),
    "name": ("Name: A–Z", Product.name.asc()),
    "newest": ("Newest first", Product.created_at.desc()),
}

PRICE_BANDS = [
    {"code": "under-50", "label": "Under €50", "min": 0, "max": 4999},
    {"code": "50-65", "label": "€50 – €65", "min": 5000, "max": 6500},
    {"code": "65-85", "label": "€65 – €85", "min": 6501, "max": 8500},
    {"code": "over-85", "label": "Over €85", "min": 8501, "max": 10_000_00},
]


def _apply_filters(query, args):
    """Apply price band and sort from the query string."""
    band_code = args.get("price")
    band = next((b for b in PRICE_BANDS if b["code"] == band_code), None)
    if band:
        query = query.filter(
            Product.price >= band["min"], Product.price <= band["max"]
        )

    sort_key = args.get("sort", "featured")
    if sort_key not in SORT_OPTIONS:
        sort_key = "featured"
    query = query.order_by(SORT_OPTIONS[sort_key][1])
    return query, band_code, sort_key


def _paginate(query, args):
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    return query.paginate(page=page, per_page=PER_PAGE, error_out=False)


@bp.route("/flowers")
def collections():
    """The complete range, with every collection listed alongside."""
    query = Product.query.filter(Product.is_active.is_(True))
    query, band, sort_key = _apply_filters(query, request.args)
    page = _paginate(query, request.args)

    return render_template(
        "shop/listing.html",
        title="All Flowers",
        headline="The complete range",
        blurb=(
            "Every arrangement we make, from a simple hand-tied bunch to a "
            "hundred roses in a box. All hand-made in Dublin 8 on the morning "
            "of delivery."
        ),
        products=page.items,
        pagination=page,
        active_price=band,
        active_sort=sort_key,
        sort_options=SORT_OPTIONS,
        price_bands=PRICE_BANDS,
        collections=Collection.query.order_by(Collection.position).all(),
        occasions=Occasion.query.order_by(Occasion.position).all(),
        endpoint="shop.collections",
        endpoint_args={},
        hero_image="img/collections/parisian-hatbox.svg",
    )


@bp.route("/flowers/<slug>")
def collection(slug):
    row = Collection.query.filter_by(slug=slug).first()
    if row is None:
        abort(404)

    query = Product.query.filter(
        Product.is_active.is_(True), Product.collection_id == row.id
    )
    query, band, sort_key = _apply_filters(query, request.args)
    page = _paginate(query, request.args)

    return render_template(
        "shop/listing.html",
        title=row.name,
        headline=row.headline,
        blurb=row.blurb,
        products=page.items,
        pagination=page,
        active_price=band,
        active_sort=sort_key,
        sort_options=SORT_OPTIONS,
        price_bands=PRICE_BANDS,
        collections=Collection.query.order_by(Collection.position).all(),
        occasions=Occasion.query.order_by(Occasion.position).all(),
        active_collection=row,
        endpoint="shop.collection",
        endpoint_args={"slug": slug},
        hero_image=row.image,
    )


@bp.route("/occasions")
def occasions():
    return render_template(
        "shop/occasions.html",
        occasions=Occasion.query.order_by(Occasion.position).all(),
    )


@bp.route("/occasions/<slug>")
def occasion(slug):
    row = Occasion.query.filter_by(slug=slug).first()
    if row is None:
        abort(404)

    query = Product.query.filter(Product.is_active.is_(True)).filter(
        Product.occasions.any(Occasion.id == row.id)
    )
    query, band, sort_key = _apply_filters(query, request.args)
    page = _paginate(query, request.args)

    return render_template(
        "shop/listing.html",
        title=row.name,
        headline=row.blurb,
        blurb=(
            f"Hand-tied {row.name.lower()} delivered anywhere in Ireland — "
            "same-day across Dublin, Kildare and Wicklow."
        ),
        products=page.items,
        pagination=page,
        active_price=band,
        active_sort=sort_key,
        sort_options=SORT_OPTIONS,
        price_bands=PRICE_BANDS,
        collections=Collection.query.order_by(Collection.position).all(),
        occasions=Occasion.query.order_by(Occasion.position).all(),
        active_occasion=row,
        endpoint="shop.occasion",
        endpoint_args={"slug": slug},
        hero_image=row.image,
    )


@bp.route("/product/<slug>")
def product(slug):
    row = Product.query.filter_by(slug=slug).first()
    if row is None or not row.is_active:
        abort(404)

    related = (
        Product.query.filter(
            Product.is_active.is_(True),
            Product.id != row.id,
            Product.collection_id == row.collection_id,
        )
        .order_by(Product.position)
        .limit(4)
        .all()
    )
    if len(related) < 4:
        extra = (
            Product.query.filter(
                Product.is_active.is_(True),
                Product.id != row.id,
                Product.id.notin_([p.id for p in related] or [0]),
            )
            .order_by(Product.position)
            .limit(4 - len(related))
            .all()
        )
        related += extra

    return render_template(
        "shop/product.html",
        product=row,
        related=related,
        sizes=size_options(),
        addons=addon_options(),
        reviews=[r for r in row.reviews if r.is_approved][:6],
    )


@bp.route("/product/<slug>/review", methods=["POST"])
def add_review(slug):
    row = Product.query.filter_by(slug=slug).first()
    if row is None:
        abort(404)

    author = request.form.get("author", "").strip()
    body = request.form.get("body", "").strip()
    try:
        rating = int(request.form.get("rating", 5))
    except (TypeError, ValueError):
        rating = 5
    rating = max(1, min(5, rating))

    if not author or not body:
        flash("Please add your name and a few words about the flowers.", "danger")
        return redirect(url_for("shop.product", slug=slug) + "#reviews")

    user_id = session.get("user_id")
    db.session.add(Review(
        product=row,
        user_id=user_id,
        author=author,
        location=request.form.get("location", "").strip() or None,
        rating=rating,
        title=request.form.get("title", "").strip() or None,
        body=body,
    ))
    db.session.commit()
    flash("Thank you for the review!", "success")
    return redirect(url_for("shop.product", slug=slug) + "#reviews")


@bp.route("/search")
def search():
    term = request.args.get("q", "").strip()
    results = []
    if term:
        like = f"%{term}%"
        results = (
            Product.query.filter(Product.is_active.is_(True))
            .filter(or_(
                Product.name.ilike(like),
                Product.blurb.ilike(like),
                Product.description.ilike(like),
                Product.contains.ilike(like),
            ))
            .order_by(Product.position)
            .limit(24)
            .all()
        )
    return render_template("shop/search.html", term=term, results=results)
