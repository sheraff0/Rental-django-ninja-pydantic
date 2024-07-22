from contrib.utils.text import parse_phone
from .env import env

AUTH_OTP_EXPIRATION = 60  # seconds
AUTH_OTP_ATTEMPTS = 3  # 3 attempts per minute
AUTH_OTP_BYPASS = env.list("OTP_BYPASS", default=[])
AUTH_BYPASS_PHONES = [parse_phone(x) for x in env.list("OTP_BYPASS_PHONES", default=[])]
AUTH_DO_SEND_SMS = env.bool("OTP_DO_SEND_SMS", default=False)
AUTH_GUEST_ACCOUNT_UNUSED = 7  # days

REHO_PREPAYMENT_RATE = 20  # percent
REHO_BOOKING_EXPIRY_MINUTES = env("REHO_BOOKING_EXPIRY_MINUTES", default=30)

REHO_PROPERTIES = env.list("REHO_PROPERTIES", default=[])
REHO_PROPERTIES = [*map(int, REHO_PROPERTIES)]

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
FRONTEND_CANCEL_BOOKING_URL = env("FRONTEND_CANCEL_BOOKING_URL", default="http://localhost:3000/booking/cancel")
