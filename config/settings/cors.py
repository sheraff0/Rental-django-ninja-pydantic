from corsheaders.defaults import default_headers
from .env import env

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

CORS_ALLOW_HEADERS = (
    *default_headers,
    "if-match",
)
