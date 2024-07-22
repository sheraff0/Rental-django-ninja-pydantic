from .env import *

redis_channel_layer = {
    "BACKEND": "channels_redis.core.RedisChannelLayer",
    "CONFIG": {
        "hosts": [(REDIS_HOST, REDIS_PORT)],
    },
}

CHANNEL_LAYERS = {
    "default": redis_channel_layer,
    "chat": redis_channel_layer,
}

WS_CLIENT_ID_EXPIRATION = 3600
