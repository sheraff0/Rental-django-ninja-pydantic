from enum import StrEnum
from datetime import datetime

from pydantic import BaseModel, NaiveDatetime, model_validator


class IdInfo(BaseModel):
    id: str


class CodeInfo(BaseModel):
    code: str


class Resource(BaseModel):
    url: str


class Standard(CodeInfo):
    name: str


class Currency(StrEnum):
    RUB = "RUB"
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class Citizenship(StrEnum):
    RUS = "RUS"
    GBR = "GBR"


class Gender(StrEnum):
    Male = "Male"
    Female = "Female"


class GuestCount(BaseModel):
    adultCount: int
    childAges: list[int] | None = None


class StayDates(BaseModel):
    arrivalDateTime: NaiveDatetime
    departureDateTime: NaiveDatetime


class StayDatesRequest(StayDates):
    @model_validator(mode="after")
    def to_string(cls, attrs):
        try:
            for key in ["arrivalDateTime", "departureDateTime"]:
                setattr(attrs, key, datetime.strftime(getattr(attrs, key), "%Y-%m-%dT%H:%M"))
        except: ...
        return attrs


class MessageResponse(CodeInfo):
    message: str


class ErrorsResponse(BaseModel):
    errors: list[MessageResponse]
