import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR.parent / "src"

# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-n!bd1#+7ufw5#9ipayu9k(lyu@za$c2ajbro7es(v8_7w1$=&c"

# Run in production mode when using a real web server
DEBUG = not any(sys.argv[0].endswith(webserver_name) for webserver_name in ["hypercorn", "uvicorn", "daphne"])
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "servestatic.runserver_nostatic",
    "daphne",  # Overrides `runserver` command with an ASGI server
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "reactpy_django",  # Django compatiblity layer for ReactPy
    "test_app",  # This test application
    "django_bootstrap5",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "servestatic.middleware.ServeStaticMiddleware",
    "test_app.middleware.AutoCreateAdminMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "test_app.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "test_app", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
ASGI_APPLICATION = "test_app.asgi.application"
sys.path.append(str(SRC_DIR))

# Database
# WARNING: There are overrides in `test_components.py` that require no in-memory
# databases are used for testing. Make sure all SQLite databases are on disk.
DB_NAME = "single_db"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, f"{DB_NAME}.sqlite3"),
        "TEST": {
            "NAME": os.path.join(BASE_DIR, f"{DB_NAME}.sqlite3"),
            "OPTIONS": {"timeout": 20},
            "DEPENDENCIES": [],
        },
        "OPTIONS": {"timeout": 20},
    },
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_ROOT = os.path.join(BASE_DIR, "static-deploy")

# Static Files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "test_app", "static"),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Logging
LOG_LEVEL = "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "reactpy_django": {"handlers": ["console"], "level": LOG_LEVEL},
        "reactpy": {"handlers": ["console"], "level": LOG_LEVEL},
        "django.request": {"handlers": ["console"], "level": LOG_LEVEL},
    },
}

# Django Channels Settings
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# ReactPy-Django Settings
REACTPY_BACKHAUL_THREAD = any(sys.argv[0].endswith(webserver_name) for webserver_name in ["hypercorn", "uvicorn"])

# ServeStatic Settings
SERVESTATIC_USE_FINDERS = True
SERVESTATIC_AUTOREFRESH = True
