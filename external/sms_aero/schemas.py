from enum import IntEnum
from pydantic import BaseModel, Field, model_validator


class SmsAuthResponse(BaseModel):
    success: bool
    message: str


class SendSms(BaseModel):
    number: str | None = None
    numbers: list[str] | None = None
    sign: str
    text: str
    dateSend: int | None = None  # Date in Unix format
    callbackUrl: str | None = None
    shortLink: int | None = None  # 1 for true

    @model_validator(mode="before")
    def number_provided(cls, attrs):
        assert any(map(attrs.get, ("number", "numbers"))), "Number(s) not provided"
        return attrs


class SmsStatus(IntEnum):
    queued = 0
    delivered = 1
    not_delivered = 2
    transmitted = 3
    suspended = 4
    rejected = 5
    moderated = 8


class SmsData(BaseModel):
    id: int
    from_: str = Field(..., alias="from")
    number: int
    text: str
    status: SmsStatus
    extendStatus: str
    channel: str
    dateCreate: int | None = None
    dateSend: int | None = None
    dateAnswer: int | None = None


class SmsResponse(BaseModel):
    success: bool
    data: SmsData
    message: str | None = None
