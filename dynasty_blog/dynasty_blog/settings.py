"""
Django settings for dynasty_blog project.
"""

from pathlib import Path
from decouple import AutoConfig, Csv
import dj_database_url
from django.db.utils import OperationalError

# ---------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Make decouple read .env placed next to manage.py (BASE_DIR/.env)
config = AutoConfig(search_path=BASE_DIR)

# ---------------------------------------------------------------------
# Security & core config
# ---------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="fallback-secret-key")
DEBUG = config("DEBUG", cast=bool, default=False)

# Comma-separated list in .env, e.g. "127.0.0.1,localhost"
ALLOWED_HOSTS = [
    h.strip()
    for h in config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if h.strip()
]

# For deployments behind a proxy/HTTPS (optional: set USE_X_FORWARDED_PROTO=1 in .env)
if config("USE_X_FORWARDED_PROTO", default="0") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF trusted origins for prod, e.g. "https://your-app.onrender.com,https://www.yourdomain.com"
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if o.strip()
]

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
    "taggit",
    "blog",
]
SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dynasty_blog.wsgi.application"

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
# Primary: PostgreSQL (via Docker)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="blog"),
        "USER": config("DB_USER", default="blog"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "connect_timeout": 5,  # prevents hanging if Postgres is unreachable
        },
    }
}

# Support DATABASE_URL for deployments
DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=config("DB_CONN_MAX_AGE", cast=int, default=600),
        ssl_require=config("DB_SSL_REQUIRE", cast=bool, default=False),
    )

# Automatic fallback to SQLite if Postgres connection fails
try:
    from django.db import connections

    connections["default"].cursor()
except Exception:
    print("⚠️  PostgreSQL not available — falling back to SQLite.")
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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
STATIC_URL = config("STATIC_URL", default="/static/")
MEDIA_URL = config("MEDIA_URL", default="/media/")

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [p for p in [BASE_DIR / "static"] if p.exists()]
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "webmaster@localhost"
)
SERVER_EMAIL = config("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# ---------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
