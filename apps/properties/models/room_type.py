import os

from django.db import models
from django.db.models import Avg
from django.db.models.functions import Coalesce, Round
from django.utils.translation import gettext_lazy as _

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from contrib.common.models import UuidTsModel
from .abstract import PropertyBase, Orderable, ImageBase


class RoomTypeQuerySet(models.QuerySet):
    def coords(self):
        return self.annotate(
            coords=Coalesce("address__coords", "property_obj__address__coords")
        ).filter(coords__isnull=False)

    def distance(self, lon, lat):
        return self.annotate(
            distance=Distance(
                "coords",
                Point(lon, lat, srid=4326)
            )
        )

    def rating(self):
        return self.annotate(rating=Round(Avg("bookings__rating"), 1))


class RoomType(Orderable, UuidTsModel, PropertyBase):
    property_obj = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="room_types")
    category = models.ForeignKey("shared.RoomTypeCategory", on_delete=models.SET_NULL,
        null=True, blank=True)
    amenities = models.ManyToManyField("shared.Amenity", blank=True)
    area = models.FloatField(_("Area"), null=True, blank=True)
    rooms = models.PositiveSmallIntegerField(_("Rooms count"), null=True, blank=True)
    beds = models.PositiveSmallIntegerField(_("Beds count"), null=True, blank=True)
    bedrooms = models.PositiveSmallIntegerField(_("Bedrooms"), null=True, blank=True)
    non_smoking = models.BooleanField(_("Non smoking room"), null=True, blank=True)

    storey = models.PositiveSmallIntegerField(_("Storey"), null=True, blank=True)
    storeys = models.PositiveSmallIntegerField(_("Storeys"), null=True, blank=True)
    elevator = models.BooleanField(_("Elevator"), null=True, blank=True)

    objects = RoomTypeQuerySet.as_manager()

    def __str__(self):
        return self.name

    def property_name(self):
        return self.property_obj.name
    property_name.short_description = _("Property object")

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Room type")
        verbose_name_plural = _("Room types")


class RoomTypeImage(ImageBase, Orderable, UuidTsModel):
    def upload_to(self, filename):
        return os.path.join("property", str(self.parent.property_obj.id),
            "room_types", str(self.parent.id), filename)

    tl_id = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("TL id"))
    parent = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_to, max_length=256)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Room type image")
        verbose_name_plural = _("Room type images")
