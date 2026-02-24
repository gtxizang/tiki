import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "labs_wrapper",
    "tiki",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "labs_wrapper.context_processors.labs_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if os.environ.get("DATABASE_URL") == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "tiki"),
            "USER": os.environ.get("POSTGRES_USER", "tiki"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "tiki"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalisation
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("ga", "Gaeilge"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("nl", "Nederlands"),
    ("it", "Italiano"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Apache Tika
TIKA_SERVER_URL = os.environ.get("TIKA_SERVER_URL", "http://localhost:9998")

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# ---------------------------------------------------------------------------
# derilinx-labs Wrapper
# ---------------------------------------------------------------------------

LABS_PROJECT_NAME = "Tiki"
LABS_PROJECT_SLUG = "tiki"
LABS_HUB_URL = "https://derilinx-labs.regexflow.com"
LABS_GITHUB_URL = "https://github.com/gtxizang/tiki"
LABS_PRODUCT_PAGE = ""

LABS_SPLASH_TITLE = "Tiki"
LABS_SPLASH_DESCRIPTION = "DCAT-AP metadata generator \u2014 making your data findable"

LABS_TOUR_STEPS = [
    {
        "element": "#upload-zone",
        "title": "Upload a file",
        "text": "Drag and drop a file here, or click to browse. Tiki accepts PDF, DOCX, CSV, and many other formats.",
        "position": "bottom",
    },
    {
        "element": "#summary-content",
        "title": "Review the summary",
        "text": "After processing, you'll see extracted metadata here \u2014 title, description, language, keywords, and more.",
        "position": "top",
    },
    {
        "element": "#empty-fields",
        "title": "Fill required fields",
        "text": "Some DCAT-AP fields like license and publisher can't be extracted automatically. Fill them in here.",
        "position": "top",
    },
    {
        "element": "#jsonld-output",
        "title": "Get your JSON-LD",
        "text": "Copy or download the complete DCAT-AP JSON-LD record, ready for your data catalogue.",
        "position": "top",
    },
]

# Gate (disabled for local dev)
GATE_URL = os.environ.get("GATE_URL", "")
GATE_API_KEY = os.environ.get("GATE_API_KEY", "")
GATE_SUBDOMAIN = "tiki.derilinx-labs.com"
GATE_EXCLUDED_PATHS = ["/health/"]
