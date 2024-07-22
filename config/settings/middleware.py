"""
Middleware settings
"""

from .env import *

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    #*(["contrib.common.middleware.DebounceUserRequestMiddleware"] if not TESTING_MODE else []),
    *(['debug_toolbar.middleware.DebugToolbarMiddleware', ] if DEBUG and TOOLBAR and not TESTING_MODE else []),
    *(['silk.middleware.SilkyMiddleware', ] if DEBUG and SILK and not TESTING_MODE else []),
]
