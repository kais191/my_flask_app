"""Checkout: delivery details, payment and order confirmation."""

from __future__ import annotations

import re
from datetime import date, timedelta

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session,
    url_for,
)

from .. import catalog
from ..extensions import db
from ..models import Order, OrderItem, User
from ..utils import (
    SAME_DAY_COUNTIES, active_coupon, cart_items, cart_totals, clear_cart,
    delivery_option_for, earliest_delivery_date, money, parse_delivery_date,
    same_day_available,
)

bp = Blueprint("checkout", __name__, url_prefix="/checkout")

CHECKOUT_KEY = "checkout_details"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CARD_RE = re.compile(r"^\d{12,19}$")
EXPIRY_RE = re.compile(r"^(0[1-9]|1[0-2])\s*/\s*(\d{2})$")

COUNTIES = [
    "Antrim", "Armagh", "Carlow", "Cavan", "Clare", "Cork", "Derry", "Donegal",
    "Down", "Dublin", "Fermanagh", "Galway", "Kerry", "Kildare", "Kilkenny",
    "Laois", "Leitrim", "Limerick", "Longford", "Louth", "Mayo", "Meath",
    "Monaghan", "Offaly", "Roscommon", "Sligo", "Tipperary", "Tyrone",
    "Waterford", "Westmeath", "Wexford", "Wicklow",
]


def _require_basket():
    """Redirect to the basket when there is nothing to check out."""
    if not cart_items():
        flash("Your basket is empty.", "info")
        return redirect(url_for("cart.view"))
    return None


def _validate_details(form):
    """Return (cleaned, errors) for the delivery details step."""
    cleaned = {
        key: (form.get(key, "") or "").strip()
        for key in (
            "customer_name", "customer_email", "customer_phone",
            "recipient_name", "recipient_phone", "address_line1",
            "address_line2", "city", "county", "eircode", "delivery_notes",
            "card_message", "delivery_option", "delivery_date",
        )
    }
    errors = {}

    if not cleaned["customer_name"]:
        errors["customer_name"] = "Please enter your name."
    if not EMAIL_RE.match(cleaned["customer_email"] or ""):
        errors["customer_email"] = "We need a valid email for your receipt."
    if not cleaned["recipient_name"]:
        errors["recipient_name"] = "Who are the flowers for?"
    if not cleaned["address_line1"]:
        errors["address_line1"] = "Please enter the delivery address."
    if not cleaned["city"]:
        errors["city"] = "Please enter a town or city."
    if not cleaned["county"]:
        errors["county"] = "Please choose a county."

    if len(cleaned["card_message"]) > 450:
        errors["card_message"] = "Card messages are limited to 450 characters."

    option = delivery_option_for(cleaned["delivery_option"] or "standard")
    cleaned["delivery_option"] = option["code"]

    county = cleaned["county"]
    if option["code"] == "sameday":
        if county and county.strip().lower() not in SAME_DAY_COUNTIES:
            errors["delivery_option"] = (
                "Same-day delivery is only available in Dublin, Kildare and "
                "Wicklow. Please choose next-day delivery."
            )
        elif not same_day_available(county):
            errors["delivery_option"] = (
                "Same-day orders close at 2pm. Please choose another date."
            )

    delivery_date = parse_delivery_date(cleaned["delivery_date"])
    earliest = earliest_delivery_date(option["code"], county or None)
    if delivery_date is None:
        errors["delivery_date"] = "Please choose a delivery date."
    elif delivery_date < earliest:
        errors["delivery_date"] = (
            f"The earliest we can deliver this is {earliest.strftime('%A %-d %B')}."
        )
    elif delivery_date > date.today() + timedelta(days=90):
        errors["delivery_date"] = "We take orders up to 90 days ahead."

    cleaned["delivery_date_obj"] = delivery_date
    return cleaned, errors


@bp.route("/", methods=["GET", "POST"])
def details():
    redirected = _require_basket()
    if redirected:
        return redirected

    stored = session.get(CHECKOUT_KEY, {})
    errors = {}

    if request.method == "POST":
        cleaned, errors = _validate_details(request.form)
        if not errors:
            saved = dict(cleaned)
            saved["delivery_date"] = cleaned["delivery_date_obj"].isoformat()
            saved.pop("delivery_date_obj", None)
            session[CHECKOUT_KEY] = saved
            return redirect(url_for("checkout.payment"))
        stored = request.form.to_dict()
        flash("Please check the highlighted fields.", "danger")
    else:
        # Prefill from the signed-in account where we can.
        user_id = session.get("user_id")
        if user_id and not stored:
            user = db.session.get(User, user_id)
            if user:
                stored = {
                    "customer_name": user.full_name,
                    "customer_email": user.email,
                    "customer_phone": user.phone or "",
                }

    totals = cart_totals(delivery_code=stored.get("delivery_option", "standard"))
    return render_template(
        "checkout/details.html",
        totals=totals,
        form=stored,
        errors=errors,
        counties=COUNTIES,
        delivery_options=catalog.DELIVERY_OPTIONS,
        same_day_open=same_day_available(),
        earliest=earliest_delivery_date(),
        earliest_sameday=earliest_delivery_date("sameday"),
        max_date=date.today() + timedelta(days=90),
    )


@bp.route("/payment", methods=["GET", "POST"])
def payment():
    redirected = _require_basket()
    if redirected:
        return redirected

    stored = session.get(CHECKOUT_KEY)
    if not stored:
        flash("Please enter your delivery details first.", "info")
        return redirect(url_for("checkout.details"))

    totals = cart_totals(delivery_code=stored.get("delivery_option", "standard"))
    errors = {}

    if request.method == "POST":
        errors = _validate_payment(request.form)
        if not errors:
            order = _create_order(stored, totals, request.form)
            clear_cart()
            session.pop(CHECKOUT_KEY, None)
            session["last_order"] = order.reference
            return redirect(url_for("checkout.confirmation", reference=order.reference))
        flash("Your payment details need a second look.", "danger")

    return render_template(
        "checkout/payment.html",
        totals=totals,
        details=stored,
        errors=errors,
        form=request.form,
        delivery_date=parse_delivery_date(stored.get("delivery_date")),
    )


def _validate_payment(form):
    """Validate the (simulated) card form.

    No card data is stored or transmitted anywhere — this stands in for a
    payment provider's hosted fields, which is where a real integration would
    take over.
    """
    errors = {}
    number = re.sub(r"[\s-]", "", form.get("card_number", ""))
    if not CARD_RE.match(number):
        errors["card_number"] = "Enter a card number (12–19 digits)."
    elif not _luhn(number):
        errors["card_number"] = "That card number doesn't check out."

    if not form.get("card_name", "").strip():
        errors["card_name"] = "Enter the name on the card."

    expiry = form.get("card_expiry", "").strip()
    match = EXPIRY_RE.match(expiry)
    if not match:
        errors["card_expiry"] = "Use MM/YY."
    else:
        month, year = int(match.group(1)), 2000 + int(match.group(2))
        today = date.today()
        if (year, month) < (today.year, today.month):
            errors["card_expiry"] = "That card has expired."

    if not re.match(r"^\d{3,4}$", form.get("card_cvc", "").strip()):
        errors["card_cvc"] = "Enter the 3-digit security code."

    return errors


def _luhn(number):
    """Standard Luhn checksum — catches most mistyped card numbers."""
    total = 0
    for index, digit in enumerate(reversed(number)):
        value = int(digit)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _create_order(details_data, totals, payment_form):
    """Persist the basket as an order. Called once payment has 'succeeded'."""
    coupon = totals["coupon"]
    order = Order(
        reference=Order.new_reference(),
        user_id=session.get("user_id"),
        status="confirmed",
        customer_name=details_data["customer_name"],
        customer_email=details_data["customer_email"].lower(),
        customer_phone=details_data.get("customer_phone"),
        recipient_name=details_data["recipient_name"],
        recipient_phone=details_data.get("recipient_phone"),
        address_line1=details_data["address_line1"],
        address_line2=details_data.get("address_line2"),
        city=details_data["city"],
        county=details_data["county"],
        eircode=details_data.get("eircode"),
        delivery_notes=details_data.get("delivery_notes"),
        delivery_date=parse_delivery_date(details_data["delivery_date"]),
        delivery_option=details_data["delivery_option"],
        delivery_fee=totals["delivery_fee"],
        card_message=details_data.get("card_message"),
        subtotal=totals["subtotal"],
        discount=totals["discount"],
        total=totals["total"],
        coupon_code=coupon.code if coupon and totals["coupon_applied"] else None,
    )
    db.session.add(order)

    for item in totals["items"]:
        order.items.append(OrderItem(
            product_id=item["product"].id,
            product_name=item["product"].name,
            product_slug=item["product"].slug,
            size_code=item["size"]["code"],
            size_name=item["size"]["name"],
            addons=",".join(a["code"] for a in item["addons"]),
            addon_names="|".join(a["name"] for a in item["addons"]),
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            line_total=item["line_total"],
        ))

    if coupon is not None and totals["coupon_applied"]:
        coupon.times_used = (coupon.times_used or 0) + 1

    db.session.commit()
    current_app.logger.info(
        "Order %s placed for %s", order.reference, order.customer_email
    )
    return order


@bp.route("/confirmation/<reference>")
def confirmation(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()

    # Only show a full confirmation to the person who just placed it, or to
    # the signed-in account that owns it.
    if session.get("last_order") != reference:
        user_id = session.get("user_id")
        if not user_id or order.user_id != user_id:
            user = db.session.get(User, user_id) if user_id else None
            if not (user and user.is_admin):
                return redirect(url_for("checkout.track", reference=reference))

    return render_template("checkout/confirmation.html", order=order)


@bp.route("/track", methods=["GET", "POST"])
@bp.route("/track/<reference>", methods=["GET", "POST"])
def track(reference=None):
    order = None
    reference = (
        request.form.get("reference", reference) or reference or ""
    ).strip().upper()
    email = request.form.get("email", "").strip().lower()

    if request.method == "POST":
        if not reference or not email:
            flash("Enter both your order reference and email address.", "danger")
        else:
            order = Order.query.filter_by(
                reference=reference, customer_email=email
            ).first()
            if order is None:
                flash(
                    "We couldn't find an order with those details. Check the "
                    "reference from your confirmation email.",
                    "danger",
                )

    return render_template(
        "checkout/track.html",
        order=order,
        reference=reference,
        statuses=Order.STATUSES,
    )
