from django.db import models

from contrib.common.models import UuidTsModel
from .abstract import BookingBase


class Search(UuidTsModel, BookingBase):
    city = models.ForeignKey("shared.City", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-update_time"]
