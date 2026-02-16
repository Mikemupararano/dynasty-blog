from .base import *
from decouple import config, Csv

DEBUG = False

ALLOWED_HOSTS = [
    h.strip() for h in config("ALLOWED_HOSTS", cast=Csv(), default="") if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")
    if o.strip()
]

# Behind reverse proxy (Nginx/Traefik/Caddy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Security
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=True)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=True)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool, default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# HSTS (enable only once HTTPS is confirmed working end-to-end)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", cast=int, default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", cast=bool, default=True
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", cast=bool, default=False)
