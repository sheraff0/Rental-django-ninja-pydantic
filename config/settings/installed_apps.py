"""
Installed apps settings
"""

from .env import *

# developed new apps
APPS = [
    "contrib.users",
    "apps.bookings",
    "apps.shared",
    "apps.properties",
]

THIRDPARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    *(["debug_toolbar", ] if DEBUG and TOOLBAR and not TESTING_MODE else []),
    *(["silk", ] if DEBUG and SILK and not TESTING_MODE else []),
    "channels",
    "corsheaders",
    "ninja",
    "django_celery_beat",
]

SYSTEM_APPS = [
    *(["daphne"] if DEBUG and DAPHNE else []),
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres.search",
]

GEO_APPS = [
    "django.contrib.gis",
]

INSTALLED_APPS = [
    *SYSTEM_APPS,
    *THIRDPARTY_APPS,
    *APPS,
    *GEO_APPS,
]

if DEBUG:
    if SWAGGER:
        INSTALLED_APPS += [
            "drf_spectacular",
        ]
elif S3_STORAGE:
    INSTALLED_APPS += [
        'storages'
    ]
