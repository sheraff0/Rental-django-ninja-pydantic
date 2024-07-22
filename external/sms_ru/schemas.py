from enum import IntEnum
from pydantic import BaseModel, Field, model_validator


class SendSms(BaseModel):
    api_id: str | None = None
    to: str
    msg: str
    json_: int = Field(default=1, alias="json")


class SmsResponse(BaseModel):
    status: str
    status_code: int
    balance: float
