from .env import env

PAYKEEPER_API_URL_MOBILE = env("PAYKEEPER_API_URL_MOBILE", default=None)
PAYKEEPER_BASIC_AUTH_HEADER_MOBILE = env("PAYKEEPER_BASIC_AUTH_HEADER_MOBILE", default=None)

PAYKEEPER_API_URL_WEB = env("PAYKEEPER_API_URL_WEB", default=None)
PAYKEEPER_BASIC_AUTH_HEADER_WEB = env("PAYKEEPER_BASIC_AUTH_HEADER_WEB", default=None)

PAYKEEPER_CALLBACK_SECRET_SEED = env("PAYKEEPER_CALLBACK_SECRET_SEED", default=None)

PAYKEEPER_USER_RESULT_CALLBACK_PATH = "/api/v1/payments/paykeeper/user-callback"
