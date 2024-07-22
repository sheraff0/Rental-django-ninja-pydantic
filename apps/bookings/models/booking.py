from enum import auto
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from contrib.common.models import UuidTsModel
from contrib.common.enum import StrEnumWithChoices
from contrib.common.querysets import ObjectAgeMixin
from contrib.utils.date_time import get_local_datetime
from contrib.utils.text import get_adults, get_children
from .abstract import BookingBase


class BookingStatus(StrEnumWithChoices):
    VERIFIED = auto()
    CONFIRMED = auto()
    REJECTED = auto()
    CANCELLED = auto()
    OUTDATED = auto()


class Currency(StrEnumWithChoices):
    RUB = "RUB"
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class BookingQuerySet(ObjectAgeMixin, models.QuerySet):
    def related(self):
        return self.select_related(
            "property_obj__address",
            "room_type__address", "room_type__category",
            "rate_plan",
        ).prefetch_related(
            "daily_rates", "history", "payments",
            "property_obj__images",
            "room_type__images", "room_type__amenities",
        )

    def outdated(self):
        return self.object_age().filter(
            object_age__gt=timedelta(minutes=settings.REHO_BOOKING_EXPIRY_MINUTES)
        )


class Booking(UuidTsModel, BookingBase):
    email = models.EmailField('email', null=True, blank=True)

    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    number = models.CharField(max_length=64, verbose_name=_("Number"), null=True)
    status = models.CharField(max_length=32, choices=BookingStatus.choices(),
        default=BookingStatus.VERIFIED, verbose_name=_("Status"))

    property_obj = models.ForeignKey("properties.Property", on_delete=models.SET_NULL, null=True, related_name="bookings")
    room_type = models.ForeignKey("properties.RoomType", on_delete=models.SET_NULL, null=True, related_name="bookings")
    rate_plan = models.ForeignKey("properties.RatePlan", on_delete=models.SET_NULL, null=True, related_name="bookings")

    placements = ArrayField(models.CharField(max_length=32), default=list, verbose_name=_("Bed types"))

    currency = models.CharField(max_length=8, choices=Currency.choices(),
        default=Currency.RUB, verbose_name=_("Currency"))
    price_before_tax = models.FloatField(verbose_name=_("Price before tax"), default=0)
    tax = models.FloatField(verbose_name=_("Tax amount"), default=0)
    price_total = models.FloatField(verbose_name=_("Total price"), default=0)

    prepayment = models.FloatField(verbose_name=_("Prepayment"), default=0)
    paid = models.BooleanField(_("Paid"), default=False)

    cancellation_policy = models.TextField(_("Cancellation policy"), null=True, blank=True)

    create_token = models.CharField(max_length=512, null=True)
    tl_request_memo = models.TextField(_("TL request memo"), null=True, blank=True)
    version = models.CharField(max_length=64, null=True, blank=True)

    corrupted = models.BooleanField(default=False)

    locked = models.BooleanField(_("Locked"), default=False)

    rating = models.PositiveSmallIntegerField(_("Rating"), null=True, blank=True)
    rating_comment = models.CharField(_("Rating comment"), max_length=256, null=True, blank=True)

    objects = BookingQuerySet.as_manager()

    @property
    def payment_upon_arrival(self):
        try: return self.price_total - (self.prepayment or 0)
        except: ...

    @property
    def arrival_datetime(self):
        try:
            return get_local_datetime(self.property_obj.time_zone, datetime.combine(
                self.arrival_date, self.arrival_time))
        except: ...

    @property
    def guests(self):
        return ", ".join((get_adults(self.adults), get_children(len(self.children or []))))

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")


class BookingHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=32, choices=BookingStatus.choices())
    create_time = models.DateTimeField('Create time', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Booking history")
        verbose_name_plural = _("Booking history")


class BookingDailyRate(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="daily_rates")
    stay_date = models.DateField()
    price_before_tax = models.FloatField(verbose_name=_("Price before tax"))

    class Meta:
        verbose_name = _("Booking daily rate")
        verbose_name_plural = _("Booking daily rates")
