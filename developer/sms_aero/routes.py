from ninja import Router

from external.sms_aero.schemas import SendSms, SmsResponse, SmsAuthResponse
import external.sms_aero.services as services

router = Router(tags=["sms-aero"])


@router.get("auth", response=SmsAuthResponse)
async def auth(request):
    return await services.auth()


@router.post("send", response=SmsResponse)
async def send_sms(request,
    data: SendSms,
):
    return await services.send_sms(data)
