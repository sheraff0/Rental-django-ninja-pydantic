from asgiref.sync import sync_to_async

from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from pydantic import BaseModel
from ninja.errors import HttpError

from contrib.ninja.auth import authenticate
from contrib.common.debounced import debounced
from contrib.users.models import User
from contrib.users.utils import GuestUser
from ..schemas import (
    UserLogin,
    OtpPhoneRequest, OtpPhoneVerify,
    OtpEmailRequest, OtpEmailVerify,
    PhoneChange, EmailChange,
)
from .otp import OtpManager, OtpField as OF


def login(request,
    data: UserLogin
):
    user = authenticate(request, **data.model_dump())
    assert user
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key}


def get_target(data, field):
    target = getattr(data, field)
    if issubclass(type(target), BaseModel):
        target = target.model_dump()
    return target


def get_target_and_verify(data: OtpPhoneVerify | OtpEmailVerify, field: OF):
    target = get_target(data, field)
    manager = OtpManager(field, target)
    manager.verify(data.code)
    return target


async def otp_obtain(data: OtpEmailRequest | OtpPhoneRequest, field: OF):
    target = get_target(data, field)
    manager = OtpManager(field, target)
    await manager.obtain()
    return True


async def get_token_dict(user: User):
    token, _ = await Token.objects.aget_or_create(user=user)
    return dict(token=token.key)


async def otp_verify(data: OtpPhoneVerify | OtpEmailVerify, field: OF):
    _target = get_target_and_verify(data, field)
    _kwargs = {field: _target}
    _user = await User.objects.filter(**_kwargs).afirst()
    if not _user:
        username = GuestUser().username if field == OF.phone else _target
        _user = User(username=username, **_kwargs)
        _user.contact_phone = _user.phone
    _user.is_verified = True
    await _user.asave()
    return await get_token_dict(user=_user)


@debounced(interval=10)
async def otp_phone_obtain(data: OtpPhoneRequest):
    return await otp_obtain(data, OF.phone)


@debounced(interval=10)
async def otp_phone_verify(data: OtpEmailVerify):
    return await otp_verify(data, OF.phone)


@debounced(interval=10)
async def otp_email_obtain(data: OtpEmailRequest):
    return await otp_obtain(data, OF.email)


@debounced(interval=10)
async def otp_email_verify(data: OtpEmailVerify):
    return await otp_verify(data, OF.email)


@sync_to_async
@transaction.atomic
def _change(request, data: PhoneChange | EmailChange, field: OF):
    _target = get_target_and_verify(data, field)
    _user = User.objects.select_for_update().get(pk=request.user.pk)
    if field == OF.phone:
        try:
            _exists_other = User.objects.filter(~Q(pk=_user.pk), **{field: _target}).exists()
            assert not _exists_other, _("Alredy taken")
        except Exception as e:
            raise HttpError(400, str(e))
    setattr(_user, field, _target)
    _user.is_verified = True
    _user.save()
    return _user


async def change(request, data: PhoneChange | EmailChange, field: OF):
    _user = await _change(request, data, field)
    # Reset cache
    _token, _ = await Token.objects.aget_or_create(user=_user)
    _token = _token.key
    await authenticate(_token, reset_cache=True)
    return _user


async def phone_change(request,
    data: PhoneChange,
):
    return await change(request, data, OF.phone)


async def email_change(request,
    data: EmailChange,
):
    return await change(request, data, OF.email)


@debounced(interval=10, with_args=False)
async def otp_skip():
    user = GuestUser().user
    user.email = None
    try:
        await user.asave()
    except:
        raise HttpError(429, str(_("Too many requests!")))
    return await get_token_dict(user=user)


async def clear_unused_guest_accounts():
    async for user in User.objects.unused_guest_accounts().all():
        print(f"Deleting user: {user.username}")
        await user.adelete()
