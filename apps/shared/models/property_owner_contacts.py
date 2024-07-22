from django.db import models

from contrib.common.enum import StrEnumWithChoices


class PropertyOwner(StrEnumWithChoices):
    REHO24 = "reho24"


class PropertyOwnerContacts(models.Model):
    owner = models.CharField("Собственник", max_length=50, choices=PropertyOwner.choices(),
        default=PropertyOwner.REHO24)
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Телефон")

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Контакты собственников объектов"
        verbose_name_plural = "Контакты собственников объектов"
