from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
    postal_code = models.CharField(max_length=16, verbose_name=_("Postal code"))
    region = models.ForeignKey("shared.Region", on_delete=models.SET_NULL, null=True, verbose_name=_("Region"))
    city = models.ForeignKey("shared.City", on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    address_line = models.CharField(max_length=128, verbose_name=_("Address"))
    coords = models.PointField(geography=True, verbose_name="Координаты")

    def __str__(self):
        return self.address_line

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
