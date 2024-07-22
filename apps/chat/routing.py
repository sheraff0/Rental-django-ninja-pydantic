from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpaterns = [
    re_path(r"ws/chat", ChatConsumer.as_asgi())
]
