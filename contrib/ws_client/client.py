from uuid import uuid4, UUID
from functools import cache

from django.contrib.auth import get_user_model
from django.conf import settings

from contrib.common.redis import redis_client


async def get_user(pk):
    User = get_user_model()
    return await User.objects.filter(pk=pk).afirst()


class WSClient:
    @staticmethod
    def get_client_id(user):
        user_id = str(user.id)
        user_client_key = f"user-client:{user_id}"
        if client_id := redis_client.get(user_client_key):
            return client_id.decode()
        else:
            EX = settings.WS_CLIENT_ID_EXPIRATION
            client_id = str(uuid4())
            redis_client.set(user_client_key, client_id, ex=EX)
            client_user_key = f"client-user:{client_id}"
            redis_client.set(client_user_key, user_id, ex=EX)
            return client_id

    @staticmethod
    async def get_user(client_id):
        client_user_key = f"client-user:{client_id}"
        if user_id := redis_client.get(client_user_key):
            user_id = user_id.decode()
            return await get_user(user_id)
