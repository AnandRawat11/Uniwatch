"""
Django settings for Uniwatch project.

Supports two modes controlled by the DJANGO_ENV environment variable:
  - "development" (default): DEBUG=True, no HTTPS enforcement, SQLite
  - "production":             DEBUG=False, full HTTPS/HSTS/security headers

Usage:
  Development (local):
      python manage.py runserver

  Production (behind Nginx + Gunicorn):
      Set DJANGO_ENV=production in your .env or system environment.
      All security settings are automatically activated.

See: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────────────────────────
# Base Path
# ──────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────────────────────────
# Environment Detection
# ──────────────────────────────────────────────────────────────────

# Load .env file if python-dotenv is installed (optional in prod — use system env)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development').lower()
IS_PRODUCTION = DJANGO_ENV == 'production'


# ──────────────────────────────────────────────────────────────────
# Core Settings
# ──────────────────────────────────────────────────────────────────

# SECURITY WARNING: In production, set SECRET_KEY via environment variable.
# Generate a new one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-8v1sa45297%vxl@vjxet)*^$=wud=ivzibacdrxlj)_geofde_'  # Dev fallback only
)

# Never run DEBUG=True in production — exposes stack traces and internal paths.
DEBUG = not IS_PRODUCTION

# Production: set your domain(s) via DJANGO_ALLOWED_HOSTS env var (comma-separated).
# Example: "yourdomain.com,www.yourdomain.com"
ALLOWED_HOSTS_ENV = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_ENV.split(',') if h.strip()] or (
    ['localhost', '127.0.0.1', '[::1]'] if not IS_PRODUCTION else []
)


# ──────────────────────────────────────────────────────────────────
# Application Definition
# ──────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'monitor',
]

MIDDLEWARE = [
    # SecurityMiddleware must be FIRST — it handles HTTPS redirects and security headers.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Uniwatch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Uniwatch.wsgi.application'


# ──────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Production: override with DATABASE_URL via environment or update ENGINE here.


# ──────────────────────────────────────────────────────────────────
# Password Validation
# ──────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ──────────────────────────────────────────────────────────────────
# Internationalisation
# ──────────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────────────────────────────
# Static Files
# ──────────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # Used by collectstatic in production


# ──────────────────────────────────────────────────────────────────
# Primary Key Type
# ──────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ──────────────────────────────────────────────────────────────────
# ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
# ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝
# ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝
# ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║
# ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝
#
# All settings below are PRODUCTION-ONLY.
# They are explicitly disabled in development to avoid localhost issues.
# ──────────────────────────────────────────────────────────────────

if IS_PRODUCTION:

    # ── 1. HTTPS ENFORCEMENT ──────────────────────────────────────
    # Redirect every plain HTTP request to HTTPS at the Django layer.
    # Nginx also handles this (see nginx.conf), providing a double safety net.
    SECURE_SSL_REDIRECT = True

    # Tell Django it is running behind an SSL-terminating reverse proxy (Nginx).
    # Nginx forwards HTTPS requests with the X-Forwarded-Proto: https header.
    # Without this, Django cannot detect that the original request was HTTPS,
    # causing an infinite redirect loop.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # ── 2. HSTS (HTTP Strict Transport Security) ──────────────────
    # Instructs browsers to ONLY connect to this domain over HTTPS
    # for the next 31,536,000 seconds (1 year). After the first HTTPS
    # visit, the browser refuses to make any plain HTTP requests —
    # even if an attacker intercepts DNS and redirects to an HTTP server.
    # This is the primary defence against SSL stripping / MITM downgrade attacks.
    SECURE_HSTS_SECONDS = 31536000           # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True    # Protect api.yourdomain.com etc.
    SECURE_HSTS_PRELOAD = True               # Submit domain to browser HSTS preload lists

    # ── 3. SECURE COOKIES ─────────────────────────────────────────
    # Cookies marked Secure are NEVER sent over plain HTTP.
    # If an attacker intercepts an HTTP request, your session is not exposed.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Prevent JavaScript from reading the session cookie (XSS mitigation).
    SESSION_COOKIE_HTTPONLY = True

    # Limit session cookie to same-site requests (CSRF mitigation).
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # ── 4. SECURITY HEADERS ───────────────────────────────────────
    # Prevent this app from being embedded in an iframe on a foreign domain.
    # Mitigates clickjacking attacks.
    X_FRAME_OPTIONS = 'DENY'

    # Stop browsers from MIME-sniffing a response away from the declared content-type.
    # Prevents certain drive-by-download and XSS vectors.
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Activate the browser's built-in XSS filter (legacy browsers).
    SECURE_BROWSER_XSS_FILTER = True

    # Referrer Policy — don't leak the full URL when navigating to external sites.
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Development-safe defaults (explicitly set to avoid Django warnings)
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SECURE_CONTENT_TYPE_NOSNIFF = True   # Safe in all environments
    SECURE_BROWSER_XSS_FILTER = True     # Safe in all environments
