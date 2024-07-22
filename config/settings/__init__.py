"""
Django settings for project
"""
from .env import *

SECRET_KEY = env('SECRET_KEY')
DEFAULT_PASSWORD = env('DEFAULT_PASSWORD', default=SECRET_KEY)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

ROOT_URLCONF = "config.urls"

AUTH_USER_MODEL = "users.User"

from .base import *
from .installed_apps import *
from .middleware import *
from .cors import *
from .database import *
from .email import *
from .locale import *
from .api_errors import *
from .rest_framework import *
from .swagger import *
from .jazzmin import *
from .debug_toolbar import *
from .silk import *
from .onesignal import *
from .travelline import *
from .channels import *
from .reho import *
from .sms_aero import *
from .sms_ru import *
from .paykeeper import *

if S3_STORAGE:
    from .s3 import *
