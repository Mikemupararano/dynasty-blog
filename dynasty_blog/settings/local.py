from .base import *
from decouple import config
import dj_database_url

# -------------------------
# Local development
# -------------------------
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]

# -------------------------
# DATABASE (Local)
# Default to SQLite for convenience,
# but allow DATABASE_URL to override.
# -------------------------
DATABASE_URL = config("DATABASE_URL", default="").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=config("DB_CONN_MAX_AGE", cast=int, default=0),
            ssl_require=False,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -------------------------
# Email (Local)
# Console backend by default to avoid
# sending real emails during development.
# You can override in .env if needed.
# -------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# Optional: if you switch EMAIL_BACKEND to SMTP in .env,
# these settings will be picked up (assuming base.py defines them),
# otherwise they’re harmless here.
