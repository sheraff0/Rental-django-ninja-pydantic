from enum import StrEnum, auto
from pydantic import (
    BaseModel, field_validator, model_validator,
    EmailStr, SecretStr,
    constr,
)

from api.common.schemas import ErrorBase
from api.profile.schemas import Phone
from contrib.utils.date_time import get_timestamp


Code = constr(pattern=r"\d{4}")


class OtpField(StrEnum):
    email = auto()
    phone = auto()


class OtpError(ErrorBase):
    wait: int | None = None
    attempts_left: int | None = None


class OtpData(BaseModel):
    code: Code
    attempts_left: int
    locked_until: int
    wait: int | None = None

    @model_validator(mode="after")
    def wait(cls, obj):
        ts = get_timestamp()
        obj.wait = max(0, obj.locked_until - ts)
        return obj


class UserLogin(BaseModel):
    username: str | EmailStr
    password: SecretStr


class TokenInfo(BaseModel):
    token: str


class OtpPhoneRequest(BaseModel):
    phone: Phone


class OtpPhoneVerify(OtpPhoneRequest):
    code: Code



@field_validator("email", mode="after")
def lower_email(cls, value):
    return value.lower()


class OtpEmailRequest(BaseModel):
    email: EmailStr

    lower_email = lower_email


class OtpEmailVerify(OtpEmailRequest):
    code: Code


class PhoneChange(BaseModel):
    phone: Phone
    code: Code


class EmailChange(BaseModel):
    email: EmailStr
    code: Code

    lower_email = lower_email
