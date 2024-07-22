import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pprint import pprint as print
from channels.layers import get_channel_layer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    channel_layer_alias = "chat"

    async def connect(self):
        if user := self.scope.get("user"):
            await self.channel_layer.group_add("invite", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, event):
        ...

    async def receive_json(self, content):
        await self.send_json({
            "echo": content
        })

    async def chat_invite(self, event):
        await self.send_json(event)
