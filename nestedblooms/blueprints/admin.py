"""A small back-office for running the shop day to day."""

from __future__ import annotations

from datetime import date, timedelta
from functools import wraps

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, session, url_for,
)
from sqlalchemy import func

from ..extensions import db
from ..models import (
    ContactMessage, NewsletterSubscriber, Order, OrderItem, Product, Review, User,
)

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user is None:
            flash("Please sign in.", "info")
            return redirect(url_for("auth.login", next=request.path))
        if not user.is_admin:
            abort(404)  # Don't advertise that an admin area exists.
        return view(*args, **kwargs)

    return wrapped


@bp.route("/")
@admin_required
def dashboard():
    today = date.today()
    week_ago = today - timedelta(days=7)

    revenue = db.session.query(func.sum(Order.total)).filter(
        Order.status != "cancelled"
    ).scalar() or 0
    revenue_week = db.session.query(func.sum(Order.total)).filter(
        Order.status != "cancelled", Order.created_at >= week_ago
    ).scalar() or 0

    top_products = (
        db.session.query(
            OrderItem.product_name,
            OrderItem.product_slug,
            func.sum(OrderItem.quantity).label("units"),
            func.sum(OrderItem.line_total).label("revenue"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status != "cancelled")
        .group_by(OrderItem.product_name, OrderItem.product_slug)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(8)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        order_count=Order.query.count(),
        revenue=revenue,
        revenue_week=revenue_week,
        pending=Order.query.filter(
            Order.status.in_(["confirmed", "in_studio"])
        ).count(),
        today_deliveries=Order.query.filter(
            Order.delivery_date == today, Order.status != "cancelled"
        ).order_by(Order.created_at).all(),
        recent_orders=Order.query.order_by(Order.created_at.desc()).limit(10).all(),
        top_products=top_products,
        unread_messages=ContactMessage.query.filter_by(is_handled=False).count(),
        subscriber_count=NewsletterSubscriber.query.count(),
        product_count=Product.query.filter_by(is_active=True).count(),
    )


@bp.route("/orders")
@admin_required
def orders():
    query = Order.query
    status = request.args.get("status", "")
    if status in Order.STATUSES:
        query = query.filter_by(status=status)

    term = request.args.get("q", "").strip()
    if term:
        like = f"%{term}%"
        query = query.filter(
            db.or_(
                Order.reference.ilike(like),
                Order.customer_email.ilike(like),
                Order.customer_name.ilike(like),
                Order.recipient_name.ilike(like),
            )
        )

    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    return render_template(
        "admin/orders.html",
        pagination=pagination,
        orders=pagination.items,
        status=status,
        term=term,
        statuses=Order.STATUSES,
    )


@bp.route("/orders/<reference>")
@admin_required
def order_detail(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()
    return render_template(
        "admin/order_detail.html", order=order, statuses=Order.STATUSES
    )


@bp.route("/orders/<reference>/status", methods=["POST"])
@admin_required
def update_status(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()
    status = request.form.get("status", "")
    if status not in Order.STATUSES:
        flash("Unknown status.", "danger")
    else:
        order.status = status
        db.session.commit()
        flash(f"{order.reference} marked as {order.status_label.lower()}.", "success")
    return redirect(
        request.form.get("next") or url_for("admin.order_detail", reference=reference)
    )


@bp.route("/products")
@admin_required
def products():
    return render_template(
        "admin/products.html",
        products=Product.query.order_by(Product.position).all(),
    )


@bp.route("/products/<int:product_id>", methods=["POST"])
@admin_required
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)

    raw_price = request.form.get("price", "").strip()
    try:
        price = int(round(float(raw_price) * 100))
        if price <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a price such as 64.95.", "danger")
        return redirect(url_for("admin.products"))

    product.price = price
    product.is_active = request.form.get("is_active") == "on"
    db.session.commit()
    flash(f"{product.name} updated.", "success")
    return redirect(url_for("admin.products"))


@bp.route("/messages")
@admin_required
def messages():
    return render_template(
        "admin/messages.html",
        messages=ContactMessage.query.order_by(
            ContactMessage.is_handled, ContactMessage.created_at.desc()
        ).all(),
        subscribers=NewsletterSubscriber.query.order_by(
            NewsletterSubscriber.created_at.desc()
        ).all(),
    )


@bp.route("/messages/<int:message_id>/handled", methods=["POST"])
@admin_required
def handle_message(message_id):
    message = db.session.get(ContactMessage, message_id)
    if message is None:
        abort(404)
    message.is_handled = not message.is_handled
    db.session.commit()
    return redirect(url_for("admin.messages"))


@bp.route("/reviews")
@admin_required
def reviews():
    return render_template(
        "admin/reviews.html",
        reviews=Review.query.order_by(
            Review.is_approved, Review.created_at.desc()
        ).limit(200).all(),
    )


@bp.route("/reviews/<int:review_id>/approve", methods=["POST"])
@admin_required
def approve_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None:
        abort(404)
    review.is_approved = not review.is_approved
    db.session.commit()
    return redirect(url_for("admin.reviews"))


@bp.route("/reviews/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None:
        abort(404)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("admin.reviews"))
