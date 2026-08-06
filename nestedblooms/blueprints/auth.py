"""Registration, sign-in and the customer account area."""

from __future__ import annotations

import re
from functools import wraps
from urllib.parse import urlparse

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, session, url_for,
)

from ..extensions import db
from ..models import Address, Order, User

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to continue.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def _safe_next(target):
    """Only redirect to paths on this site — never to an absolute URL."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/"):
        return None
    return target


@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("auth.account"))

    form = {}
    errors = {}

    if request.method == "POST":
        form = {
            key: (request.form.get(key, "") or "").strip()
            for key in ("first_name", "last_name", "email", "phone")
        }
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not form["first_name"]:
            errors["first_name"] = "Please enter your first name."
        if not form["last_name"]:
            errors["last_name"] = "Please enter your surname."
        if not EMAIL_RE.match(form["email"]):
            errors["email"] = "Please enter a valid email address."
        elif User.query.filter_by(email=form["email"].lower()).first():
            errors["email"] = (
                "There is already an account with that email. Try signing in."
            )
        if len(password) < MIN_PASSWORD_LENGTH:
            errors["password"] = (
                f"Passwords need at least {MIN_PASSWORD_LENGTH} characters."
            )
        elif password != confirm:
            errors["confirm"] = "The two passwords don't match."

        if not errors:
            user = User(
                first_name=form["first_name"],
                last_name=form["last_name"],
                email=form["email"].lower(),
                phone=form["phone"] or None,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            session.permanent = True
            flash(f"Welcome to Nested Blooms, {user.first_name}!", "success")
            return redirect(_safe_next(request.args.get("next")) or url_for("auth.account"))

        flash("Please check the highlighted fields.", "danger")

    return render_template("auth/register.html", form=form, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("auth.account"))

    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session.permanent = bool(request.form.get("remember"))
            flash(f"Welcome back, {user.first_name}.", "success")
            target = _safe_next(request.form.get("next") or request.args.get("next"))
            if user.is_admin and not target:
                target = url_for("admin.dashboard")
            return redirect(target or url_for("auth.account"))

        # Deliberately vague: revealing which half was wrong helps attackers
        # enumerate registered addresses.
        flash("Those details don't match an account.", "danger")

    return render_template("auth/login.html", email=email)


@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/account")
@login_required
def account():
    user = current_user()
    orders = (
        Order.query.filter_by(user_id=user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template(
        "auth/account.html",
        user=user,
        orders=orders,
        upcoming=[o for o in orders if o.is_upcoming],
    )


@bp.route("/account/orders/<reference>")
@login_required
def order_detail(reference):
    user = current_user()
    order = Order.query.filter_by(reference=reference).first_or_404()
    if order.user_id != user.id and not user.is_admin:
        abort(404)
    return render_template("auth/order_detail.html", order=order)


@bp.route("/account/details", methods=["POST"])
@login_required
def update_details():
    user = current_user()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not first_name or not last_name:
        flash("Names cannot be blank.", "danger")
        return redirect(url_for("auth.account"))

    user.first_name = first_name
    user.last_name = last_name
    user.phone = request.form.get("phone", "").strip() or None
    db.session.commit()
    flash("Your details have been updated.", "success")
    return redirect(url_for("auth.account"))


@bp.route("/account/password", methods=["POST"])
@login_required
def change_password():
    user = current_user()
    current = request.form.get("current_password", "")
    new = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if not user.check_password(current):
        flash("Your current password is not correct.", "danger")
    elif len(new) < MIN_PASSWORD_LENGTH:
        flash(f"New passwords need at least {MIN_PASSWORD_LENGTH} characters.", "danger")
    elif new != confirm:
        flash("The two new passwords don't match.", "danger")
    else:
        user.set_password(new)
        db.session.commit()
        flash("Your password has been changed.", "success")

    return redirect(url_for("auth.account"))


@bp.route("/account/addresses", methods=["POST"])
@login_required
def add_address():
    user = current_user()
    required = ("recipient_name", "line1", "city", "county")
    values = {
        key: (request.form.get(key, "") or "").strip()
        for key in required + ("label", "line2", "eircode", "phone")
    }

    if any(not values[key] for key in required):
        flash("Please fill in the name, address, town and county.", "danger")
        return redirect(url_for("auth.account") + "#addresses")

    db.session.add(Address(
        user=user,
        label=values["label"] or "Saved address",
        recipient_name=values["recipient_name"],
        line1=values["line1"],
        line2=values["line2"] or None,
        city=values["city"],
        county=values["county"],
        eircode=values["eircode"] or None,
        phone=values["phone"] or None,
    ))
    db.session.commit()
    flash("Address saved.", "success")
    return redirect(url_for("auth.account") + "#addresses")


@bp.route("/account/addresses/<int:address_id>/delete", methods=["POST"])
@login_required
def delete_address(address_id):
    user = current_user()
    address = db.session.get(Address, address_id)
    if address is None or address.user_id != user.id:
        abort(404)
    db.session.delete(address)
    db.session.commit()
    flash("Address removed.", "info")
    return redirect(url_for("auth.account") + "#addresses")
