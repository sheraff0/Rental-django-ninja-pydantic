import asyncio
from functools import wraps


def with_attrs(**kwargs):
    def __(cls):
        def update_attrs(name, bases, attrs):
            attrs.update(kwargs)
            return type(name, bases, attrs)

        @wraps(cls, updated=())
        class _(cls, metaclass=update_attrs):
            pass

        return _
    return __


def default_on_error(default=None):
    def __(coro):
        @wraps(coro)
        async def _(*args, **kwargs):
            try:
                return await coro(*args, **kwargs)
            except:
                return default
        return _
    return __


def nested_async(coro):
    @wraps(coro)
    def __(*args, **kwargs):
        async def _():
            await coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_())
    return __
