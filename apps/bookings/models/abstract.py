from django.db import models
from django.contrib.postgres.fields import ArrayField


class BookingBase(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    adults = models.PositiveSmallIntegerField()
    children = ArrayField(models.PositiveSmallIntegerField(), default=list)
    arrival_date = models.DateField()
    departure_date = models.DateField()

    class Meta:
        abstract = True
