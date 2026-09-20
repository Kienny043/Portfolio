"""
Django settings for the portfolio API. The React frontend is a separate static
site on its own origin, so CORS is enabled for the origins in CORS_ALLOWED_ORIGINS.

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
    "corsheaders",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# Origins of the deployed frontend, WITH scheme and no trailing slash, comma-separated,
# e.g. "https://portfolio-web.onrender.com". The localhost default only applies in local
# dev (DEBUG); in production nothing is allowed until CORS_ALLOWED_ORIGINS is set.
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173" if DEBUG else ""
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

STATIC_URL = "static/"

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
