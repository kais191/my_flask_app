"""Nested Blooms — an Irish florist shop built on Flask."""

from __future__ import annotations

import click
from flask import Flask, render_template, session

from . import catalog
from .config import Config
from .extensions import db

__version__ = "1.0.0"


def create_app(config_object=Config):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_object)

    db.init_app(app)

    _register_blueprints(app)
    _register_context(app)
    _register_error_handlers(app)
    _register_cli(app)

    with app.app_context():
        db.create_all()

    return app


def _register_blueprints(app):
    from .blueprints.admin import bp as admin_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.cart import bp as cart_bp
    from .blueprints.checkout import bp as checkout_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.shop import bp as shop_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)


def _register_context(app):
    """Expose shop-wide data and helpers to every template."""
    from datetime import date

    from .models import Collection, Occasion, User
    from .utils import cart_count, money

    @app.context_processor
    def inject_globals():
        user = None
        if session.get("user_id"):
            user = db.session.get(User, session["user_id"])
            if user is None:
                session.pop("user_id", None)

        return {
            "brand": catalog.BRAND,
            "nav_collections": Collection.query.order_by(Collection.position).all(),
            "nav_occasions": Occasion.query.order_by(Occasion.position).all(),
            "delivery_areas": catalog.DELIVERY_AREAS,
            "current_user": user,
            "cart_count": cart_count(),
            "money": money,
            "free_delivery_threshold": catalog.FREE_DELIVERY_THRESHOLD,
            "now_year": date.today().year,
        }

    @app.template_filter("euro")
    def euro_filter(cents):
        return money(cents)

    @app.template_filter("nl2br")
    def nl2br(value):
        from markupsafe import Markup, escape

        if not value:
            return ""
        return Markup("<br>".join(escape(value).splitlines()))


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_cli(app):
    @app.cli.command("seed")
    def seed_command():
        """Create tables and load the catalogue."""
        from .seed import seed_all

        db.create_all()
        seed_all()

    @app.cli.command("reset-db")
    @click.confirmation_option(prompt="This deletes all orders. Continue?")
    def reset_command():
        """Drop every table and reseed from scratch."""
        from .seed import reset_all

        reset_all()
        click.echo("Database rebuilt.")
