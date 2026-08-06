"""Application configuration."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _database_uri():
    """Resolve the database URL, tolerating Heroku/Render's legacy scheme."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        instance = os.path.join(BASE_DIR, "instance")
        os.makedirs(instance, exist_ok=True)
        return "sqlite:///" + os.path.join(instance, "nestedblooms.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-production")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Sessions carry the shopping basket, so they need to outlive the browser
    # window without being permanent.
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "") == "1"

    # Static assets are content-hashed by name, so they can be cached hard.
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 7

    # Credentials for the seeded administrator account.
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@nestedblooms.ie")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "bloom-admin-2024")
