import aiohttp
from django.conf import settings

from contrib.common.pydantic import json_clean
from contrib.utils.async_api_client import AsyncClient, async_api_client

from .schemas import SendSms

SMS_AERO_API_URL = "https://gate.smsaero.ru/v2"
SIGN = "SMS Aero"


class SMSAero:
    def __init__(self):
        self.client = AsyncClient(SMS_AERO_API_URL,
            default_headers={"Authorization": f"Basic {settings.SMS_AERO_BASIC_AUTH}"})

    async def auth(self):
        return await self.client.request("/auth")

    async def send(self, data: SendSms):
        params = json_clean(data)
        return await self.client.request("/sms/send", params=params)
        """
        Response body:
        {
            "success": true,
            "data": {
                "id": 539820423,
                "from": "SMS Aero",
                "number": "79186475294",
                "text": "Stronghold",
                "status": 8,
                "extendStatus": "moderation",
                "channel": "FREE SIGN",
                "cost": 4.19,
                "dateCreate": 1677576947,
                "dateSend": 1677576947
            },
            "message": null
        }
        """


sms_aero_client = async_api_client(SMSAero)
