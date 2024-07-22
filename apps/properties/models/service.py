from django.db import models
from django.utils.translation import gettext_lazy as _

from contrib.common.models import UuidTsModel
from .abstract import PropertyBase, Orderable, ImageBase


class Service(Orderable, UuidTsModel, PropertyBase):
    address = None
    property_obj = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="services")
    meal_plan = models.ForeignKey("shared.MealPlan", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="services")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order"]
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
