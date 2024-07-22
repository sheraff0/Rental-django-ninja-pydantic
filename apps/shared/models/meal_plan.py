from django.db import models
from django.utils.translation import gettext_lazy as _


class MealPlan(models.Model):
    code = models.CharField(max_length=32, verbose_name=_("TL code"))
    name = models.CharField(max_length=64, verbose_name=_("Title"))

    def __str__(self):
        return f"{self.code} ({self.name})"

    class Meta:
        verbose_name = _("Meal plan")
        verbose_name_plural = _("Meal plans")
