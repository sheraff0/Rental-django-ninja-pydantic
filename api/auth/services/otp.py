from dataclasses import dataclass, fields
from enum import StrEnum
import orjson

from asgiref.sync import sync_to_async
from django.conf import settings
from django.template import loader
from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from api.assets import attachments_dict
from config.settings import ApiErrors as AE
from contrib.common.redis import redis_client
from contrib.common.schemas import Phone
from contrib.users.models import User
from contrib.utils.date_time import get_timestamp
from contrib.utils.email import send_mail
from contrib.utils.verify import get_verification_code
from external.sms_aero.api import SMSAero, sms_aero_client
from external.sms_aero.schemas import SendSms
from external.sms_ru.api import SmsRu, sms_ru_client
from external.sms_ru.schemas import SendSms as SendSmsSmsRu

from ..schemas import OtpField, OtpError, OtpData


@dataclass
class OtpManager:
    field: OtpField
    target: str | dict
    attempts: int = settings.AUTH_OTP_ATTEMPTS
    lock_interval: int | None = None
    message: str = _("Verification code")
    timeout: int = settings.AUTH_OTP_EXPIRATION

    def __post_init__(self):
        self.lock_interval = self.lock_interval or self.timeout
        self.set_key()

    def set_key(self):
        self._key = orjson.dumps({"field": self.field, "target": self.target})

    async def obtain(self):
        try:
            self.set_code()
            self.store()
        except AssertionError as e:
            raise HttpError(400, str(e))
        await self.send_code()
    
    def verify(self, code):
        try:
            self.retrieve()
            self.set_attempts()
            self.check_code(code)
        except AssertionError as e:
            raise HttpError(400, str(e))
        return True

    def set_code(self):
        self._code = get_verification_code()

    def store(self, data=None):
        if data is None:
            self.check_not_locked()
            _ttl = dict(ex=self.timeout)
        else:
            _ttl = dict(keepttl=True)

        _dump = self.get_dump(data=data)
        redis_client.set(self._key, _dump, **_ttl)

    def get_dump(self, data=None):
        _data = data or OtpData(
            code=self._code,
            attempts_left=self.attempts,
            locked_until=get_timestamp() + self.lock_interval,
        )
        return orjson.dumps(_data.model_dump())

    def retrieve(self, check=True):
        _dump = redis_client.get(self._key)
        if check:
            assert bool(_dump), AE.CODE_DOESN_T_EXIST
        self._stored_data = _dump and OtpData(**orjson.loads(_dump))

    def check_not_locked(self):
        self.retrieve(check=False)
        if self._stored_data:
            _wait = self._stored_data.wait
            assert settings.TESTING_MODE or (_wait == 0), OtpError(
                code=AE.TOO_MANY_REQUESTS,
                wait=_wait
            ).model_dump_json(exclude_none=True)

    def set_attempts(self):
        assert self._stored_data.attempts_left > 0, OtpError(
            code=AE.NO_ATTEMPTS_LEFT,
            wait=self._stored_data.wait,
        ).model_dump_json(exclude_none=True)
        self._stored_data.attempts_left -= 1
        self.store(data=self._stored_data)

    def check_code(self, code):
        assert any((
            code == self._stored_data.code,
            all((
                settings.DEBUG,
                code in settings.AUTH_OTP_BYPASS,
            )),
            all((
                not settings.DEBUG,
                self.is_bypass_phone,
                code in settings.AUTH_OTP_BYPASS,
            ))
        )), OtpError(
            code=AE.CODES_DON_T_MATCH,
            attempts_left=self._stored_data.attempts_left,
            wait=0 if self._stored_data.attempts_left > 0 else self._stored_data.wait, 
        ).model_dump_json(exclude_none=True)


    def delete_code(self):
        redis_client.delete(self._key)

    async def send_code(self):
        send_method = getattr(self, f"send_code_{self.field}", None)
        if send_method:
            await send_method()

    @sync_to_async
    def send_code_email(self):
        subject = "[Reho24] " + _("Verification code")
        template = loader.get_template("email/otp.html")
        body = template.render({
            "code": self._code,
        })
        try:
            send_mail(subject, body, [self.target], attachments=["logo_png"])
        except Exception as e:
            self.delete_code()
            _error = e.__class__.__name__
            raise {
                "TimeoutError": HttpError(503, ". ".join(map(str, (
                    _("Cannot send email"), AE.SERVICE_UNAVAILABLE)))),
                "SMTPRecipientsRefused": HttpError(400, AE.EMAIL_DOESN_T_EXIST),
            }.get(_error, HttpError(400, AE.CANNOT_SEND_EMAIL))
        
    @sms_aero_client
    async def send_code_phone_sms_aero(self, client: SMSAero = None):
        data = SendSms(
            number="".join((self._target["countryCode"], self._target["nsn"])),
            sign="Sms Aero",
            text=f"Reho24 verification code: {self._code}",
        )
        await client.send(data)

    @sms_ru_client
    async def send_code_phone_sms_ru(self, client: SmsRu = None):
        data = SendSmsSmsRu(
            to="".join((self._target["countryCode"], self._target["nsn"])),
            msg=f"Reho24 verification code: {self._code}",
        )
        await client.send(data)

    async def send_code_phone(self):
        if not settings.AUTH_DO_SEND_SMS:
            return
        if self.is_bypass_phone:
            return
        print("Sending SMS...")
        try:
            #await self.send_code_phone_sms_aero()
            await self.send_code_phone_sms_ru()
        except Exception as e:
            print(e)
            self.delete_code()
            raise HttpError(400, str(_("Cannot send SMS")))

    @property
    def is_bypass_phone(self):
        return (self.field == OtpField.phone) and \
            Phone(**self.target) in settings.AUTH_BYPASS_PHONES
