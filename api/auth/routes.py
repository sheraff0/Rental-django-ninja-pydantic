from django.utils.translation import gettext_lazy as _

from ninja import Router
from ninja.errors import HttpError

import api.auth.services as services
from api.profile.schemas import UserInfo
from ..common.schemas import SuccessMessage
from .schemas import (
    UserLogin, TokenInfo,
    OtpPhoneRequest, OtpPhoneVerify,
    OtpEmailRequest, OtpEmailVerify,
    PhoneChange, EmailChange,
)


router = Router()


#@router.post("/login", response=TokenInfo, auth=None)
def login(request,  # syncronous
    data: UserLogin,
):
    try:
        return services.login(request, data)
    except:
        raise HttpError(400, str(_("Bad credentials")))


@router.post("/otp/phone/obtain", auth=None, response=SuccessMessage)
async def otp_phone_obtain(request,
    data: OtpPhoneRequest,
):
    success = await services.otp_phone_obtain(data)
    return SuccessMessage(success=success)


@router.post("/otp/phone/verify", auth=None, response=TokenInfo)
async def phone_verify(request,
    data: OtpPhoneVerify,
):
    return await services.otp_phone_verify(data)


@router.post("/otp/email/obtain", auth=None, response=SuccessMessage)
async def otp_email_obtain(request,
    data: OtpEmailRequest,
):
    success = await services.otp_email_obtain(data)
    return SuccessMessage(success=success)


#@router.post("/otp/email/verify", auth=None, response=TokenInfo)
async def email_verify(request,
    data: OtpEmailVerify,
):
    return await services.otp_email_verify(data)


@router.post("/otp/email/verify", auth=None)
async def email_verify(request,
    data: OtpEmailVerify,
):
    raise HttpError(400, "Not implemented")


@router.post("/phone/change", response=UserInfo)
async def phone_change(request,
    data: PhoneChange,
):
    return await services.phone_change(request, data)


@router.post("/email/change", response=UserInfo)
async def email_change(request,
    data: EmailChange,
):
    return await services.email_change(request, data)


@router.post("/skip", auth=None, response=TokenInfo)
async def otp_skip(request):
    return await services.otp_skip()


@router.post("/clear-unused-guest-accounts")
async def clear_unused_guest_accounts(request):
    return await services.clear_unused_guest_accounts()
