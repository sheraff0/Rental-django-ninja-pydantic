from .api import SMSAero, sms_aero_client
from .schemas import SendSms


@sms_aero_client
async def auth(
    client: SMSAero = None,
):
    return await client.auth()


@sms_aero_client
async def send_sms(
    data: SendSms,
    client: SMSAero = None,
):
    return await client.send(data)
