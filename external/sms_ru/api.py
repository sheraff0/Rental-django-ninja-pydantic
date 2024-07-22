import aiohttp
from django.conf import settings

from contrib.common.pydantic import json_clean
from contrib.utils.async_api_client import AsyncClient, async_api_client

from .schemas import SendSms

SMS_RU_API_URL = "https://sms.ru"


class SmsRu:
    def __init__(self):
        self.client = AsyncClient(SMS_RU_API_URL)

    async def send(self, data: SendSms):
        data.api_id = settings.SMS_RU_API_ID
        params = json_clean(data)
        return await self.client.request("/sms/send", params=params)


sms_ru_client = async_api_client(SmsRu)
