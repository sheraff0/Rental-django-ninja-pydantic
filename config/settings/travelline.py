from .env import env

TRAVELLINE_API_URL = "https://partner.qatl.ru/api"
TRAVELLINE_API_KEY = env("TRAVELLINE_API_KEY")

TRAVELLINE_SEARCH_CACHE_EXPIRATION = 10