# Internationalization

from .env import BASE_DIR

TIME_ZONE = "Europe/Moscow"
LANGUAGE_CODE = "ru-ru"

LANGUAGES = [
    ("ru", "Russian"),
    ("en", "English"),
    ("uk", "Ukrainian"),
]

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "contrib/locale",
    BASE_DIR / "api/locale",
    BASE_DIR / "apps/locale",
]
