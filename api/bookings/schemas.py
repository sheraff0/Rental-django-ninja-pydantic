from datetime import date, datetime
import json
from uuid import UUID

from django.conf import settings

from ninja import Schema, ModelSchema
from pydantic import BaseModel, model_validator, field_validator, conint, Field

from bridge.travelline.search.schemas import get_days
from contrib.common.pagination import Paginated
from contrib.utils.date_time import get_local_datetime
from external.paykeeper.schemas import PayKeeperAccount
from external.travelline.schemas.common import CodeInfo, GuestCount
from external.travelline.schemas.search import CancellationPolicy
from apps.bookings.models import (
    Booking, BookingStatus, Currency,
    BookingHistory, BookingDailyRate,
    Payment, PaymentStatus,
)
from api.properties.schemas import PropertyInfo, RoomTypeInfo, RatePlanInfo


class BookingVerify(Schema):
    search_id: UUID
    property_id: UUID
    room_type_id: UUID
    rate_plan_id: UUID
    placements: list[str]
    checksum: str


class DaysMixin(Schema):
    days: int | None = None

    @model_validator(mode="after")
    def set_days(cls, obj):
        obj.days = get_days(obj)
        return obj


class BookingBrief(ModelSchema):
    status: BookingStatus

    class Meta:
        model = Booking
        fields = ["id", "number", "status"]


class BookingDailyRateInfo(ModelSchema):
    class Meta:
        model = BookingDailyRate
        exclude = ["id", "booking"]


class BookingHistoryInfo(ModelSchema):
    class Meta:
        model = BookingHistory
        exclude = ["id", "booking"]


class PaymentInfo(ModelSchema):
    status: PaymentStatus

    class Meta:
        model = Payment
        exclude = ["booking"]


class BookingInfo(DaysMixin, ModelSchema):
    property: PropertyInfo = Field(alias="property_obj")
    room_type: RoomTypeInfo
    rate_plan: RatePlanInfo
    placements: list[str]
    children: list[int]
    status: BookingStatus
    currency: Currency
    daily_rates: list[BookingDailyRateInfo]
    history: list[BookingHistoryInfo]
    payments: list[PaymentInfo]
    payment_upon_arrival: float | None
    cancellation_policy: CancellationPolicy | None
    arrival_datetime: datetime | None = None

    @field_validator("cancellation_policy", mode="before")
    def load_cancellation_policy(cls, value):
        try: return json.loads(value)
        except: return value

    @model_validator(mode="after")
    def correct_penalty_amount(cls, obj):
        try:
            _penalty = obj.cancellation_policy.penaltyAmount
            obj.cancellation_policy.penaltyAmount = min(obj.prepayment, _penalty)
        except: ...
        return obj

    class Meta:
        model = Booking
        exclude = ["user", "create_token", "property_obj", "tl_request_memo"]


PaginatedBookingInfo = Paginated(BookingInfo)


class BookingCustomizable(Schema):
    comment: str | None = ""


class PenaltyInfo(Schema):
    arrival_date: date
    departure_date: date
    prepayment: float | None = None
    penalty: float
    refund: float
    amount: float | None = None  # to be deprecated


class BookingRating(Schema):
    rating: conint(ge=1, le=5)
    rating_comment: str | None = None


class PayBookingRequest(BaseModel):
    user_result_callback: str | None = None
    account: PayKeeperAccount | None = PayKeeperAccount.MOBILE


class PayBookingResponse(BaseModel):
    invoice_url: str
