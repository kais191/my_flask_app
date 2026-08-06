"""Nested Blooms — application entry point.

Run locally:

    python app.py

In production the Procfile serves ``app:app`` through gunicorn.
"""

from nestedblooms import create_app

app = create_app()


if __name__ == "__main__":
    import os

    with app.app_context():
        from nestedblooms.models import Product
        from nestedblooms.seed import seed_all

        # An empty database on first run is almost always a fresh checkout
        # rather than a deliberately emptied shop.
        if Product.query.count() == 0:
            seed_all()

    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8000)),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )
