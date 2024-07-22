from django.db import models
from django.utils.translation import gettext_lazy as _


class RoomTypeCategory(models.Model):
    code = models.CharField(max_length=16, verbose_name=_("TL code"))
    name = models.CharField(max_length=32, verbose_name=_("Title"))

    def __str__(self):
        return f"{self.code} ({self.name})"

    class Meta:
        verbose_name = _("Room type category")
        verbose_name_plural = _("Room type categories")
