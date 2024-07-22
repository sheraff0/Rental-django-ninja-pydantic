from .api import SmsRu, sms_ru_client
from .schemas import SendSms


@sms_ru_client
async def auth(
    client: SmsRu = None,
):
    return await client.auth()


@sms_ru_client
async def send_sms(
    data: SendSms,
    client: SmsRu = None,
):
    return await client.send(data)
