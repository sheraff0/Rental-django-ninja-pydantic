from enum import auto
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime

from contrib.common.enum import StrEnumWithChoices
from contrib.common.models import UuidTsModel
from external.paykeeper.schemas import PaymentStatus, RefundStatus, PayKeeperAccount


class PaymentPurpose(StrEnumWithChoices):
    PREPAYMENT = auto()


class PaymentQuerySet(models.QuerySet):
    def unsettled(self):
        _localtime = localtime()
        return self.filter(
            update_time__range=(
                _localtime - timedelta(days=31),
                _localtime - timedelta(minutes=10),
            ),
            status__in=(PaymentStatus.PENDING, PaymentStatus.REFUNDING),
        )


class Payment(UuidTsModel):
    booking = models.ForeignKey("bookings.Booking", on_delete=models.CASCADE, related_name="payments")
    amount = models.FloatField(default=0, verbose_name=_("Amount"))
    refunded = models.FloatField(_("Refunded amount"), null=True, blank=True)
    purpose = models.CharField(max_length=32, choices=PaymentPurpose.choices(),
        default=PaymentPurpose.PREPAYMENT, verbose_name=_("Purpose"))
    status = models.CharField(max_length=32, choices=PaymentStatus.choices(),
        default=PaymentStatus.PENDING, verbose_name=_("Status"))

    paykeeper_id = models.PositiveSmallIntegerField("PayKeeper ID", null=True, blank=True)
    paykeeper_account = models.CharField(max_length=16, choices=PayKeeperAccount.choices(),
        default=PayKeeperAccount.MOBILE, verbose_name=_("PayKeeper account"))
    invoice_url = models.CharField(max_length=128, verbose_name="Ссылка на оплату", null=True, blank=True)
    expiry = models.DateTimeField(_("Invoice expiry"), null=True, blank=True)

    objects = PaymentQuerySet.as_manager()

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
