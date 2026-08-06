"""The shopping basket."""

from __future__ import annotations

from flask import (
    Blueprint, flash, jsonify, redirect, render_template, request, session,
    url_for,
)

from ..models import Coupon, Product
from ..utils import (
    COUPON_KEY, add_to_cart, cart_count, cart_items, cart_totals,
    remove_cart_line, update_cart_line,
)

bp = Blueprint("cart", __name__)


@bp.route("/basket")
def view():
    items = cart_items()
    totals = cart_totals(items)
    suggestions = []
    if items:
        seen = {item["product"].id for item in items}
        suggestions = (
            Product.query.filter(
                Product.is_active.is_(True), Product.id.notin_(seen or [0])
            )
            .order_by(Product.position)
            .limit(4)
            .all()
        )
    return render_template("shop/cart.html", totals=totals, suggestions=suggestions)


@bp.route("/basket/add", methods=["POST"])
def add():
    try:
        product_id = int(request.form.get("product_id", 0))
    except (TypeError, ValueError):
        product_id = 0

    product = Product.query.get(product_id)
    if product is None or not product.is_active:
        flash("Sorry, that arrangement is no longer available.", "danger")
        return redirect(request.referrer or url_for("shop.collections"))

    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    add_to_cart(
        product_id=product.id,
        size_code=request.form.get("size", "classic"),
        addon_codes=request.form.getlist("addons"),
        quantity=max(1, quantity),
    )

    if request.form.get("ajax"):
        totals = cart_totals()
        return jsonify({
            "ok": True,
            "count": cart_count(),
            "subtotal": totals["subtotal"],
            "name": product.name,
        })

    flash(f"{product.name} added to your basket.", "success")
    if request.form.get("buy_now"):
        return redirect(url_for("checkout.details"))
    return redirect(url_for("cart.view"))


@bp.route("/basket/update", methods=["POST"])
def update():
    key = request.form.get("key", "")
    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        remove_cart_line(key)
        flash("Item removed from your basket.", "info")
    else:
        update_cart_line(key, quantity)
    return redirect(url_for("cart.view"))


@bp.route("/basket/remove", methods=["POST"])
def remove():
    remove_cart_line(request.form.get("key", ""))
    flash("Item removed from your basket.", "info")
    return redirect(url_for("cart.view"))


@bp.route("/basket/coupon", methods=["POST"])
def coupon():
    code = request.form.get("code", "").strip().upper()
    next_url = request.form.get("next") or url_for("cart.view")

    if not code:
        session.pop(COUPON_KEY, None)
        flash("Discount code removed.", "info")
        return redirect(next_url)

    row = Coupon.query.filter_by(code=code, is_active=True).first()
    if row is None:
        flash(f"'{code}' isn't a valid discount code.", "danger")
        return redirect(next_url)

    totals = cart_totals(coupon=row)
    if row.min_spend and totals["subtotal"] < row.min_spend:
        from ..utils import money

        flash(
            f"{code} needs a basket of {money(row.min_spend)} or more.", "danger"
        )
        return redirect(next_url)

    session[COUPON_KEY] = code
    flash(f"Discount applied — {row.description}.", "success")
    return redirect(next_url)
