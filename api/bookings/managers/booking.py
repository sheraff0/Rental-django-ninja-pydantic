import abc
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import jwt
from uuid import UUID

from django.conf import settings
from django.db.models import Q
from django.template import loader
from django.template.defaulttags import date as date_tag
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from api.common.tasks import send_mail_task
from api.search.schemas import AccomodationOffer
from apps.bookings.models import (
    Search, Booking, Payment,
    BookingHistory, BookingDailyRate,
    BookingStatus, PaymentStatus,
)
from apps.properties.models import Property, RoomType, RatePlan, Service
from bridge.travelline.reservation import (
    verify_booking_tl, create_booking_tl,
    update_booking_tl,
    cancellation_penalty_tl, cancel_booking_tl,
)
from bridge.travelline.search.schemas import SearchParams
from contrib.common.cached import get_memo
from contrib.common.pagination import get_paginated_queryset
from contrib.users.models import User
from contrib.utils.text import phone_str
from external.travelline.schemas.reservation import (
    VerifyBookingRequest, Booking as BookingRq, BookingRoomStay, BookingRoomType,
    CommonGuestInfo, BookingGuest, BookingCustomer, GuestCount,
    BookingPersonContacts, BookingPhone, BookingEmail,
    BookingPrepayment, PaymentType,
    VerifyBookingResponse, ModifyBookingRequest, CancelBookingRequest,
    CreateBookingRequest, CreateBookingResponse, BookingStatus as BookingStatusTl,
    CancellationPenaltyResponse, CancellationPolicy,
)
from ..schemas import BookingVerify, BookingCustomizable, BookingRating
from .common import ProcessBookingManagerBase


async def get_booking(pk: UUID, user: User):
    try:
        return await Booking.objects.related().aget(pk=pk, user=user)
    except:
        raise HttpError(404, str(_("Booking not found")))


async def list_bookings(
    user: User,
    page: int | None = 1,
    size: int | None = 4,
    include_outdated: bool | None = False,
):
    qs = Booking.objects.related().filter(
        Q() if include_outdated else ~Q(status=BookingStatus.OUTDATED),
        user=user,
    ).order_by("-update_time")
    return await get_paginated_queryset(qs, page, size)


async def get_user(pk: UUID):
    try:
        return await User.objects.aget(pk=pk)
    except:
        raise HttpError(404, str(_("User not found")))


@dataclass
class VerifyBookingManager:
    user: User
    data: BookingVerify
    corrupted: bool = False

    def __post_init__(self):
        self._response = None
        self._booking = None

    def set_contacts(self):
        assert self.user.is_verified, _("User not verified")
        self._phone = phone_str(self.user.phone or self.user.contact_phone)
        assert len(self._phone) > 5, _("Please provide phone")
        self._email = self.user.email or "-"
        assert len(self._email) > 5, _("Please provide email")
        self._first_name = self.user.first_name
        self._last_name = self.user.last_name
        self._middle_name = self.user.middle_name
        assert self._first_name and self._last_name, _("Please provide first and last name")

    async def set_search(self):
        self._search = await Search.objects.filter(
            #pk=self.data.search_id, user=self.user).select_related("city").afirst()
            pk=self.data.search_id).select_related("city").afirst()
        assert self._search, _("Search object not found")

    async def set_property(self):
        self._property = await Property.objects.filter(pk=self.data.property_id).afirst()
        assert self._property, _("Property type not found")

    async def set_room_type(self):
        self._room_type = await RoomType.objects.filter(pk=self.data.room_type_id).select_related(
            "property_obj__address").afirst()
        assert self._room_type, _("Room type not found")
        assert self._room_type.property_obj_id == self._property.id, _("Room type and property do not match")
        assert any((
            self._search.city_id is None,
            self._room_type.property_obj.address.city_id == self._search.city_id,
        )), \
            _("Room type and search city do not match")
        self._placements = [dict(code=x) for x in self.data.placements]

    async def set_rate_plan(self):
        self._rate_plan = await RatePlan.objects.filter(pk=self.data.rate_plan_id).afirst()
        assert self._rate_plan, _("Rate plan not found")
        assert self._rate_plan.property_obj_id == self._room_type.property_obj_id, \
            _("Room type and rate plan do not match")

    def set_offer(self):
        self._offer = get_memo(self.data.checksum, AccomodationOffer)
        assert self._offer, _("Invalid checksum")

    async def set(self):
        try:
            self.set_contacts()
            await self.set_search()
            await self.set_property()
            await self.set_room_type()
            await self.set_rate_plan()
            self.set_offer()
        except Exception as e:
            raise HttpError(400, str(e))

    def get_verify_request(self) -> VerifyBookingRequest:
        return VerifyBookingRequest(
            booking=BookingRq(
                propertyId=str(self._property.tl_id),
                roomStays=[self.get_room_stay()],
                # services: list[IdInfo] | None = None
                customer=self.get_customer(),
                prepayment=BookingPrepayment(
                    paymentType=PaymentType.PrePay,
                    prepaidSum=self._offer.prepayment,
                ),
                #bookingComments: list[str] | None = None
            )
        )

    def get_common_guest_info(self):
        return CommonGuestInfo(
            firstName=self._first_name,
            lastName=self._last_name,
            middleName=self._middle_name,
            #citizenship=
        ).model_dump()

    def get_guest(self):
        return BookingGuest(
            **self.get_common_guest_info(),
            #sex=
        )

    def get_customer(self):
        return BookingCustomer(
            **self.get_common_guest_info(),
            contacts=BookingPersonContacts(
                phones=[BookingPhone(phoneNumber=self._phone)] if len(self._phone) > 5 else [],
                emails=[BookingEmail(emailAddress=self._email)] if len(self._email) > 5 else [],
            ),
            comment="Comment",
        )

    def get_room_stay(self):
        return BookingRoomStay(
            stayDates=self._offer.stay_dates.model_dump(),
            ratePlan=dict(id=str(self._rate_plan.tl_id)),
            roomType=BookingRoomType(
                id=str(self._room_type.tl_id),
                placements=self._placements,
            ),
            guests=[self.get_guest()],
            guestCount=GuestCount(
                adultCount=self._search.adults,
                childAges=self._search.children,
            ),
            checksum=self.data.checksum,
        )

    async def verify_booking_tl(self):
        self._request = self.get_verify_request()
        try:
            res = await verify_booking_tl(self._request)
            self._response = VerifyBookingResponse(**res)
        except:
            raise HttpError(400, str(_("TL server error")))
        if self._response.alternativeBooking:
            raise HttpError(400, str(_("Booking conditions changed!")))
        return self._response

    async def save(self):
        try:
            # Booking
            _room_stay = self._response.booking.roomStays[0]
            _price_before_tax = _room_stay.total.priceBeforeTax
            _tax = _room_stay.total.taxAmount
            _price_total = _price_before_tax + _tax
            self._booking, _ = await Booking.objects.aupdate_or_create(
                user=self.user,
                create_token=self._response.booking.createBookingToken,
                defaults=dict(
                    email=self._email,
                    adults=self._search.adults,
                    children=self._search.children,
                    arrival_date=self._search.arrival_date,
                    departure_date=self._search.departure_date,
                    arrival_time=self._offer.stay_dates.arrivalDateTime.time,
                    departure_time=self._offer.stay_dates.departureDateTime.time,
                    property_obj=self._property,
                    room_type=self._room_type,
                    rate_plan=self._rate_plan,
                    placements=self.data.placements,
                    currency=self._rate_plan.currency,
                    price_before_tax=_price_before_tax,
                    tax=_tax,
                    price_total=_price_total,
                    prepayment=self._response.booking.prepayment.prepaidSum or 0,
                    tl_request_memo=self._request.model_dump_json(exclude_none=True),
                    corrupted=self.corrupted,
                    cancellation_policy=self._response.booking.cancellationPolicy.model_dump_json(exclude_none=True),
                ),
            )
            # BookingDailyRate
            _daily_rates = [BookingDailyRate(
                booking=self._booking,
                stay_date=x.date,
                price_before_tax=x.priceBeforeTax,
            ) for x in _room_stay.dailyRates or []]
            await BookingDailyRate.objects.filter(booking=self._booking).adelete()
            await BookingDailyRate.objects.abulk_create(_daily_rates)
            # BookingHistory
            await BookingHistory.objects.aupdate_or_create(
                booking=self._booking,
                status=BookingStatus.VERIFIED,
            )
            return self._booking
        except Exception as e:
            print(e)


class NotifyBookingMixin:
    def get_cancel_token(self):
        _exp = (datetime.combine(self._booking.arrival_date, datetime.min.time())
            + timedelta(days=1)).timestamp()
        return jwt.encode(dict(
            user_id=str(self.user.id),
            booking_id=str(self._booking.id),
            aud="bookings:cancel",
            exp=_exp,
        ), settings.SECRET_KEY, algorithm="HS256")

    def get_cancel_url(self):
        _cancel_token = self.get_cancel_token()
        return settings.FRONTEND_CANCEL_BOOKING_URL + \
            f"?booking_id={self._booking.id}&token={_cancel_token}"

    def get_address(self):
        return self._booking.room_type.address or self._booking.property_obj.address

    @staticmethod
    def get_cancellation_deadline_verbose(cancellation_policy):
        try:
            res = cancellation_policy.freeCancellationDeadlineLocal
            return format_html("&nbsp;".join([
                *[date_tag(res, x) for x in ("d", "E", "H:i")],
                "UTC", date_tag(res, "O").replace("0", "")
            ]))
        except: ...

    def notify(self):
        template = loader.get_template("email/booking.html")
        _cancellation_policy = CancellationPolicy(**json.loads(self._booking.cancellation_policy))
        _cancellation_refund = max(0, self._booking.prepayment - _cancellation_policy.penaltyAmount)
        body = template.render({
            "user": self.user,
            "booking": self._booking,
            "address": self.get_address(),
            "booking_request": json.loads(self._booking.tl_request_memo),
            "cancellation_policy": _cancellation_policy,
            "cancellation_deadline": self.get_cancellation_deadline_verbose(_cancellation_policy),
            "cancellation_penalty": self._booking.prepayment - _cancellation_refund,
            "cancellation_refund": _cancellation_refund,
            "cancel_url": self.get_cancel_url()
        })
        subject = f"""[Reho24] Новая бронь!"""
        send_mail_task.delay(subject, body, [self.email], attachments=["logo_png"])


@dataclass
class CreateBookingManager(NotifyBookingMixin, ProcessBookingManagerBase):
    status_on_success: BookingStatus = BookingStatus.CONFIRMED
    status_on_failure: BookingStatus = None  # is set to REJECTED lower

    def set_payment(self):
        self._payment = None
        if self._booking.prepayment > 0:
            assert self._booking.paid, _("Booking is not paid")
            self._payment = Payment.objects.filter(booking=self._booking).first()
            assert self._payment, _("Payment not found")
            assert self._payment.status == PaymentStatus.SUCCESS, _("Payment needed")

    def set(self):
        self.set_payment()
        assert self._booking.status == BookingStatus.VERIFIED, _("Booking impossible")
        # REJECTED if cannot confirm booking; changes in payment status don't matter
        self.status_on_failure = BookingStatus.REJECTED
        assert self._booking.create_token, _("No create token found")
        assert not self._booking.corrupted, _("Booking object is corrupted")
        _validate_params = SearchParams.from_orm(self._booking)

    def set_request(self):
        try:
            _create_token = self._booking.create_token
            _request_data = json.loads(self._booking.tl_request_memo)
            _request_data["booking"]["createBookingToken"] = _create_token
            self._request = CreateBookingRequest(**_request_data)
        except:
            assert False, _("Error in request data")

    async def process(self):
        self.set_request()
        res = await create_booking_tl(self._request)
        self._response = CreateBookingResponse(**res)
        self._response_booking = self._response.booking
        assert self._response_booking and self._response_booking.number, _("Booking not confirmed")

    def save(self):
        self._request.booking.roomStays[0].checksum = self._response_booking.roomStays[0].checksum
        self._booking.tl_request_memo = self._request.model_dump_json(exclude_none=True)
        self._booking.number = self._response_booking.number
        self._booking.version = self._response_booking.version

    def post_save(self):
        self.notify()


class CheckBookingMixin:
    def check_booking(self):
        assert self._booking.status != BookingStatus.CANCELLED, _("Booking is already cancelled")
        assert self._booking.status == BookingStatus.CONFIRMED, _("Booking not confirmed")
        assert self._booking.number, _("Booking number not assigned")
        assert self._booking.arrival_datetime > localtime(), _("Cannot do this past arrival time")


@dataclass
class UpdateBookingManager(CheckBookingMixin, ProcessBookingManagerBase):
    data: BookingCustomizable = None

    def set(self):
        self.check_booking()
        self.set_request()

    def set_request(self):
        try:
            _request_data = json.loads(self._booking.tl_request_memo)
            _request_data["booking"]["version"] = self._booking.version
            self._request = ModifyBookingRequest(**_request_data)
            self._request.booking.bookingComments = [self.data.comment]
        except:
            assert False, _("Error in request data")

    async def process(self):
        self.set_request()
        res = await update_booking_tl(self._booking.number, self._request)
        self._response = CreateBookingResponse(**res)
        self._response_booking = self._response.booking
        assert self._response_booking and self._response_booking.version, _("Cannot obtain version")

    def save(self):
        self._booking.tl_request_memo = self._request.model_dump_json(exclude_none=True)
        self._booking.version = self._response_booking.version
        self._booking.save()


class CancelBookingManagerBase(CheckBookingMixin, ProcessBookingManagerBase):
    def set(self):
        self.check_booking()

    async def process(self):
        res = await cancellation_penalty_tl(self._booking.number)
        self._response = CancellationPenaltyResponse(**res)
        self._penalty_amount = self._response.penaltyAmount

    @property
    def penalty(self):
        return min(self._booking.prepayment, self._penalty_amount)

    @property
    def refund(self):
        return max(0, self._booking.prepayment - self._penalty_amount)


class CancellationPenaltyBookingManager(NotifyBookingMixin, CancelBookingManagerBase):
    def save(self):
        ...

    def post_save(self):
        ...
        #self.notify()


@dataclass
class CancelBookingManager(CancelBookingManagerBase):
    status_on_success: BookingStatus = BookingStatus.CANCELLED

    async def process(self):
        await super().process()
        _data = CancelBookingRequest(reason="", expectedPenaltyAmount=self._penalty_amount)
        res = await cancel_booking_tl(self._booking.number, _data)
        self._response = CreateBookingResponse(**res)
        self._response_booking = self._response.booking
        assert self._response_booking and self._response_booking.status == BookingStatusTl.Cancelled, \
            _("Booking not cancelled")

    def save(self):
        ...


@dataclass
class RateBookingManager(ProcessBookingManagerBase):
    data: BookingRating = None

    def set(self):
        #assert self._booking.status == BookingStatus.DONE, _("Booking cannot be rated")
        ...

    async def process(self):
        ...

    def save(self):
        self._booking.rating = self.data.rating
        self._booking.rating_comment = self.data.rating_comment
