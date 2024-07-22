from datetime import date
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, EmailStr, AwareDatetime


from .common import IdInfo, CodeInfo, GuestCount, StayDatesRequest, Citizenship, Gender, Currency, MessageResponse
from .content import Placement, Service
from .search import CancellationPolicy


class BookingRoomType(IdInfo):
    placements: list[CodeInfo]


class CommonGuestInfo(BaseModel):
    firstName: str
    lastName: str
    middleName: str | None = None
    citizenship: Citizenship | None = None


class BookingGuest(CommonGuestInfo):
    sex: Gender | None = None


class BookingRoomStay(BaseModel):
    stayDates: StayDatesRequest
    ratePlan: IdInfo
    roomType: BookingRoomType
    guests: list[BookingGuest] | None = None
    guestCount: GuestCount
    services: list[IdInfo] | None = None
    checksum: str


class BookingPhone(BaseModel):
    phoneNumber: str


class BookingEmail(BaseModel):
    emailAddress: EmailStr


class BookingPersonContacts(BaseModel):
    phones: list[BookingPhone]
    emails: list[BookingEmail]


class BookingCustomer(CommonGuestInfo):
    contacts: BookingPersonContacts
    comment: str | None = None


class PaymentType(StrEnum):
    Cash = "Cash"
    PrePay = "PrePay"


class BookingPrepayment(BaseModel):
    remark: str | None = None
    paymentType: PaymentType
    prepaidSum: float | None = None


class Booking(BaseModel):
    propertyId: str
    roomStays: list[BookingRoomStay]
    services: list[IdInfo] | None = None
    customer: BookingCustomer
    prepayment: BookingPrepayment | None = None
    bookingComments: list[str] | None = None


class VerifyBookingRequest(BaseModel):
    booking: Booking


class CreateBooking(Booking):
    createBookingToken: str  # obtained from `/bookings/verify` method


class CreateBookingRequest(BaseModel):
    booking: CreateBooking


class ModifyBooking(Booking):
    version: str


class ModifyBookingRequest(BaseModel):
    booking: ModifyBooking


class CancelBookingRequest(BaseModel):
    reason: str | None = None
    expectedPenaltyAmount: float | None = None


# --- RESPONSE ---

class BookingDailyRate(BaseModel):
    priceBeforeTax: float
    date: date


class BookingTaxAmount(BaseModel):
    amount: float
    index: int


class BookingTotal(BaseModel):
    priceBeforeTax: float
    taxAmount: float
    taxes: list[BookingTaxAmount] | None = None


class Vat(BaseModel):
    applicable: bool
    included: bool | None = None
    percent: int | None = None


class BookingRatePlanRs(IdInfo):
    name: str
    description: str | None = None
    vat: Vat | None = None


class BookingRoomTypeRs(IdInfo):
    placements: list[Placement]
    name: str


class RoomStayServiceRs(Service):
    totalPrice: float | None = None
    inclusive: bool
    vat: Vat | None = None


class BookingServiceRs(IdInfo):
    name: str
    description: str | None = None
    price: float


class BookingRoomStayRs(BookingRoomStay):
    ratePlan: BookingRatePlanRs
    roomType: BookingRoomTypeRs
    dailyRates: list[BookingDailyRate] | None = None
    total: BookingTotal
    services: list[RoomStayServiceRs]


class BookingTax(BaseModel):
    index: int
    name: str | None = None
    description: str | None = None


class BookingCancellation(BaseModel):
    penaltyAmount: float | None = None
    reason: str | None = None
    cancelledUtc: AwareDatetime


class BookingRs(Booking):
    roomStays: list[BookingRoomStayRs]
    services: list[BookingServiceRs] | None = None
    total: BookingTotal
    taxes: list[BookingTax]
    currencyCode: Currency | None = None
    cancellation: BookingCancellation | None = None
    cancellationPolicy: CancellationPolicy


class VerifyBookingRs(BookingRs):
    createBookingToken: str


class WarningRs(CodeInfo):
    message: str | None = None


class VerifyBookingResponse(BaseModel):
    booking: VerifyBookingRs | None = None
    alternativeBooking: VerifyBookingRs | None = None
    warnings: list[MessageResponse] | None = None
    errors: list[MessageResponse] | None = None


class BookingStatus(StrEnum):
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"


class CreatedBookingRs(BookingRs):
    number: str | None = None
    status: BookingStatus
    createdDateTime: AwareDatetime
    modifiedDateTime: AwareDatetime
    version: str | None = None


class CreateBookingResponse(BaseModel):
    booking: CreatedBookingRs | None = None
    warnings: list[MessageResponse] | None = None
    errors: list[MessageResponse] | None = None


class CancellationPenaltyResponse(BaseModel):
    penaltyAmount: float
