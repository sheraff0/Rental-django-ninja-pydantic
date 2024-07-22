from django.test import Client as ClientBase


class Client(ClientBase):
    def post(self, path, **kwargs):
        kwargs["content_type"] = "application/json"
        return super().post(path, **kwargs)
