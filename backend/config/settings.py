"""
Django settings for the portfolio: a single service that serves both the DRF API
(/api/...) and the built React app (frontend/dist), so everything is same-origin.

All secrets/config come from environment variables (see .env.example and the
"Deployment" section of CLAUDE.md). The app maps onto pre-existing Aiven tables
(managed = False) and uses no Django-native auth/session/admin tables, so
`migrate` is not required.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"  # output of `npm run build`

load_dotenv(BASE_DIR / ".env")


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


# Secure by default: DEBUG is only on when DJANGO_DEBUG=true is set explicitly.
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is not true.")
    SECRET_KEY = "dev-only-insecure-key-change-me"

# Comma-separated hostnames, e.g. "portfolio-api.onrender.com". Render also
# injects RENDER_EXTERNAL_HOSTNAME for the service, which is allowed automatically.
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
]

if DEBUG:
    # CORS is only a local-dev convenience (e.g. hitting :8000 directly from :5173).
    # In production the frontend and API share an origin, so it's not installed at all.
    INSTALLED_APPS.insert(2, "corsheaders")
    MIDDLEWARE.insert(2, "corsheaders.middleware.CorsMiddleware")
    CORS_ALLOWED_ORIGINS = env_list(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# DATABASE_URL = Aiven connection string (must include ?sslmode=require)
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        # Aiven's small plans allow very few connections. Default: close after each
        # request. Raise DB_CONN_MAX_AGE only with few, fixed workers (e.g. gunicorn).
        conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE") or 0),
        ssl_require=not DEBUG,
    )
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = False
USE_TZ = True

# Static files: `collectstatic` copies the built React app (frontend/dist) into
# STATIC_ROOT, gzip/brotli-compresses it, and WhiteNoise serves it. The built app
# expects to live at the site root (/assets/..., /images/..., /favicon.svg), so
# WhiteNoise is told to serve STATIC_ROOT at "/" rather than under STATIC_URL.
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [FRONTEND_DIST] if FRONTEND_DIST.is_dir() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
WHITENOISE_STATIC_PREFIX = "/"
WHITENOISE_INDEX_FILE = True  # serve index.html for "/"


def _immutable_file_test(path, url):
    # Vite content-hashes everything under /assets/, so it can be cached forever.
    return url.startswith("/assets/")


WHITENOISE_IMMUTABLE_FILE_TEST = _immutable_file_test

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    # Render terminates TLS at its proxy; trust its forwarded-proto header.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    # Public, unauthenticated API — no Django auth/session tables involved.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PAGINATION_CLASS": None,
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_RATES": {"contact": "5/hour", "analytics": "60/hour"},
}
