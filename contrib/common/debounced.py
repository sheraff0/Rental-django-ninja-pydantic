import asyncio
from functools import wraps
import orjson
from datetime import timedelta
import time

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ninja import Schema
from ninja.errors import HttpError
from pydantic import BaseModel

from contrib.common.redis import redis_client, get_key
from contrib.common.pydantic import json_clean


def debounced(
    interval: int = 1,  # seconds
    max_queue: int = 1,
    with_args: bool = True,
):
    _error_message = str(_("Too many requests!"))

    def __(coro):
        @wraps(coro)
        async def _(*args, **kwargs):
            if settings.TESTING_MODE:
                return await coro(*args, **kwargs)

            _key = get_key(coro, args, kwargs, with_args=with_args)
            _now = time.time()

            if ts := redis_client.get(_key):
                _wait = max(0, float(ts) + interval - _now)
                _start_at = _wait + _now
                if _wait // interval >= max_queue:
                    raise HttpError(429, _error_message)
            else:
                _start_at = _now
                _wait = 0

            redis_client.set(_key, _start_at)

            if _wait > 0:
                await asyncio.sleep(_wait)
            return await coro(*args, **kwargs)
        return _
    return __
