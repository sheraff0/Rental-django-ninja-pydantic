"""
Common UUID model
"""
from uuid import uuid4

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    create_time = models.DateTimeField('Create time', auto_now_add=True, editable=False)
    update_time = models.DateTimeField('Last update time', auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UuidTsModel(TimeStampedModel, UUIDModel):
    class Meta:
        abstract = True
