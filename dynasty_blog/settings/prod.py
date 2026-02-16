from .base import *
from decouple import config, Csv

# -------------------------
# Production
# -------------------------
DEBUG = False

# Comma-separated in env:
# ALLOWED_HOSTS=example.com,www.example.com
# Csv() already returns a Python list, so DO NOT call .tolist()
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="")

# Comma-separated in env (must include scheme):
# CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")

# Security
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
