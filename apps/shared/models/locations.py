from django.apps import apps
from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from contrib.common.managers import SearchMixin


class RegionQuerySet(SearchMixin, models.QuerySet):
    ...


class Region(models.Model):
    tl_id = models.PositiveIntegerField(verbose_name=_("TL id"))
    name = models.CharField(max_length=64, verbose_name=_("Title"))

    objects = RegionQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class CityQuerySet(SearchMixin, models.QuerySet):
    search_fields = ["name", "region__name"]

    def popular(self):
        Search = apps.get_model("bookings", "Search")
        own_searches = Search.objects.values("city_id").filter(
            city_id=OuterRef("pk")
        ).annotate(
            count=Count("city_id")
        ).values("count")
        return self.annotate(
            count=Subquery(own_searches)
        )


class City(models.Model):
    region = models.ForeignKey("shared.Region", related_name="cities",
        on_delete=models.SET_NULL, null=True, verbose_name=_("Region"))
    tl_id = models.PositiveIntegerField(verbose_name=_("TL id"))
    name = models.CharField(max_length=64, verbose_name=_("Title"))

    objects = CityQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
