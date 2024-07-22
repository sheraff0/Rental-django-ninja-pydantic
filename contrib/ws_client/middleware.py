from urllib import parse
from .client import WSClient


class ClientIdAuth:
    def __init__(self, app):
        self.app = app

    def get_client_id(self, scope):
        try:
            qs = scope["query_string"].decode()
            params = parse.parse_qs(qs)
            return params["client_id"][0]
        except: ...

    async def __call__(self, scope, receive, send):
        user = None
        if client_id := self.get_client_id(scope):
            user = await WSClient.get_user(client_id)
        scope["user"] = user
        return await self.app(scope, receive, send)
