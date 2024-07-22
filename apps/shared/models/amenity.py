from django.db import models
from django.utils.translation import gettext_lazy as _


class AmenityCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("Title"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Amenity category")
        verbose_name_plural = _("Amenity categories")


class Amenity(models.Model):
    amenity_category = models.ForeignKey(AmenityCategory, related_name="amenities",
        on_delete=models.CASCADE, verbose_name=_("Amenity category"))
    code = models.CharField(max_length=64, verbose_name=_("TL code"))
    name = models.CharField(max_length=64, verbose_name=_("Title"))

    def __str__(self):
        return f"{self.code} ({self.name})"

    class Meta:
        verbose_name = _("Amenity")
        verbose_name_plural = _("Amenities")
