from datetime import datetime
from django.conf import settings

TIMEOUT = settings.MARI_DEBOUNCE_REQUESTS / 1000


class DebounceUserRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._cache = {}

    def __call__(self, request, *args, **kwargs):
        path = request.path

        if any((
            not path.startswith("/api/"),
            not (user := request.user and request.user.id)
        )):
            return self.get_response(request)

        method = request.method
        key = user, method, path

        ts, response = self._cache.get(key, (None, None))
        now = datetime.now().timestamp()

        if ts:
            if now < ts + settings.MARI_DEBOUNCE_REQUESTS / 1000:
                print("Reponse from cache", flush=True)
                return response

        response = self.get_response(request)
        self._cache[key] = now, response

        return response
