import abc

from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class PropertyBase(models.Model):
    tl_id = models.IntegerField(null=True, blank=True, verbose_name=_("TL id"))
    name = models.CharField(max_length=128, verbose_name=_("Title"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    address = models.ForeignKey("shared.Address", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_("Address"))

    class Meta:
        abstract = True


class Orderable(models.Model):
    sort_order = models.IntegerField(null=True, blank=True, editable=False)

    class Meta:
        abstract = True
        ordering = ["sort_order"]


class ImageBase(models.Model):
    def image_tag(self):
        return format_html(f'<img style="max-height: 50vh;" src="{self.image.url}">')
    image_tag.short_description = _("Image")
    image_tag.allow_tags = True

    class Meta:
        abstract = True