from functools import wraps

from rest_framework import serializers


def use_images(cls):
    def update_attrs(name, bases, attrs):
        image_fields = [x for x in cls.Meta.fields if "image" in x]
        attrs.update(**{field: serializers.CharField(required=False, allow_null=True, source=f"{field}.file.url")
            for field in image_fields})
        return type(name, bases, attrs)

    @wraps(cls, updated=())
    class _(cls, metaclass=update_attrs):
        pass

    return _
