import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


from apps.shared.models import PropertyOwner
from contrib.common.enum import StrEnumWithChoices
from contrib.common.models import UuidTsModel
from .abstract import PropertyBase, Orderable, ImageBase


class StayUnit(StrEnumWithChoices):
    NIGHT_RATE = "NightRate"
    DAILY_RATE = "DailyRate"


class Property(UuidTsModel, PropertyBase):
    tl_linked = models.BooleanField(_("Linked to TravelLine"), default=False)
    check_in_time = models.TimeField(_("Check-in time"), default="14:00")
    check_out_time = models.TimeField(_("Check-out time"), default="12:00")
    time_zone = models.CharField(max_length=32, default="Europe/Moscow")
    stay_unit = models.CharField(max_length=32, choices=StayUnit.choices(), default=StayUnit.NIGHT_RATE)
    owner = models.CharField("Собственник", max_length=50, choices=PropertyOwner.choices(),
        null=True, blank=True)

    def is_reho(self):
        return self.owner == PropertyOwner.REHO24

    def is_reho_old(self):
        return bool(self.tl_id) and (self.tl_id in settings.REHO_PROPERTIES)

    def __str__(self):
        return f"({self.tl_id or 0}) {self.name}"

    class Meta:
        verbose_name = _("Property object")
        verbose_name_plural = _("Property objects")


class PropertyImage(ImageBase, Orderable, UuidTsModel):
    def upload_to(self, filename):
        return os.path.join("property", str(self.parent.id), filename)

    def delete(self, *args, **kwargs):
        self.image.delete()
        print("Deleting image...")
        super().delete(*args, **kwargs)

    tl_id = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("TL id"))
    parent = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_to, max_length=128)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Property image")
        verbose_name_plural = _("Property images")