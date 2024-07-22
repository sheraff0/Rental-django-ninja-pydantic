from django.db.models import F
from django.utils.timezone import localtime


class ObjectAgeMixin:
    def object_age(self):
        return self.annotate(
            object_age=localtime() - F("create_time")
        )
