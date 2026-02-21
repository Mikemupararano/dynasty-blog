"""
Django settings for dynasty_blog project.

This version is corrected for:
- Clean env loading (no shadowing config)
- Proper BASE_DIR
- Local Postgres SSL disabled by default (fixes: "server does not support SSL, but SSL was required")
- Production SSL controllable via env (DATABASE_URL + DB_SSLMODE / DB_SSL_REQUIRE)
- Request context processor enabled (needed for canonical URLs in templates)
- Whitenoise + static/media sanity
"""

from pathlib import Path
import os

from django.core.management.utils import get_random_secret_key
from decouple import AutoConfig
import dj_database_url


# ---------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------
# Assuming structure: dynasty-blog/<project>/dynasty_blog/settings.py
# settings.py is 2 levels down from repo root -> adjust if needed
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read .env placed next to manage.py (BASE_DIR/.env)
env = AutoConfig(search_path=BASE_DIR)


def env_bool(key: str, default: bool = False) -> bool:
    """Robust bool parsing for env vars."""
    return str(env(key, default=str(int(default)))).strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


# ---------------------------------------------------------------------
# Security & core config
# ---------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default=get_random_secret_key())

DEBUG = env_bool("DEBUG", default=False)

ALLOWED_HOSTS = [
    h.strip()
    for h in env("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if h.strip()
]

# Trust proxy SSL header if behind nginx / reverse proxy
if env_bool("USE_X_FORWARDED_PROTO", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in env("CSRF_TRUSTED_ORIGINS", default="").split(",") if o.strip()
]

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "taggit",
    "blog",
]
SITE_ID = 1


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dynasty_blog.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # project-level templates folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Required for {{ request.* }} in templates
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dynasty_blog.wsgi.application"


# ---------------------------------------------------------------------
# Database (PostgreSQL)
# ---------------------------------------------------------------------
# You can control SSL behaviour with:
# - DB_SSLMODE: disable | require | verify-ca | verify-full
# - DB_SSL_REQUIRE: 1/0 (used only for DATABASE_URL parsing convenience)
#
# IMPORTANT: For local dev, DB_SSLMODE defaults to "disable"
DB_SSLMODE = env("DB_SSLMODE", default="disable").strip().lower()
DB_SSL_REQUIRE = env_bool("DB_SSL_REQUIRE", default=False)

DATABASE_URL = env("DATABASE_URL", default="").strip()

if DATABASE_URL:
    # Parse DATABASE_URL. Many hosted providers want SSL; you control with DB_SSL_REQUIRE and/or DB_SSLMODE.
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=env("DB_CONN_MAX_AGE", cast=int, default=600),
            ssl_require=DB_SSL_REQUIRE,
        )
    }

    # If you want explicit sslmode, add/override OPTIONS
    # (psycopg3 respects "sslmode")
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"].update(
        {
            "sslmode": DB_SSLMODE,  # ✅ fixes local "SSL required" error when set to disable
            "connect_timeout": 5,
        }
    )

else:
    # Discrete settings (local/dev or custom)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="blog"),
            "USER": env("DB_USER", default="blog"),
            "PASSWORD": env("DB_PASSWORD", default=""),
            "HOST": env("DB_HOST", default="localhost"),
            "PORT": env("DB_PORT", default="5432"),
            "CONN_MAX_AGE": env("DB_CONN_MAX_AGE", cast=int, default=600),
            "OPTIONS": {
                "connect_timeout": 5,
                "sslmode": DB_SSLMODE,  # ✅ default "disable" fixes your current error
            },
        }
    }


# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------
STATIC_URL = env("STATIC_URL", default="/static/")
MEDIA_URL = env("MEDIA_URL", default="/media/")

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

# Optional extra static directory: BASE_DIR/static (only if it exists)
STATICFILES_DIRS = [str(p) for p in [BASE_DIR / "static"] if p.exists()]

# WhiteNoise storage (compressed + hashed filenames)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}


# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", default=False)

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default=(EMAIL_HOST_USER or "webmaster@localhost")
)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)


# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
