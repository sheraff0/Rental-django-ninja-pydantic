"""
Database settings
"""

from .env import env

DATABASES = {
    "default": {
        **env.db(),
        "ENGINE": "django.contrib.gis.db.backends.postgis",
    },
}
