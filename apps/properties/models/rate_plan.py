from django.db import models
from django.utils.translation import gettext_lazy as _

from contrib.common.models import UuidTsModel


class RatePlan(UuidTsModel):
    property_obj = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="rate_plans")
    tl_id = models.IntegerField(null=True, blank=True, verbose_name=_("TL id"))
    name = models.CharField(max_length=128, verbose_name=_("Title"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    currency = models.CharField(max_length=16, verbose_name=_("Currency"), default="RUB")
    with_children_only = models.BooleanField(verbose_name=_("With children only"), default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Rate plan")
        verbose_name_plural = _("Rate plans")
