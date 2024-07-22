import shutil

from django.conf import settings

from apps.properties.models import Property
from contrib.common.redis import redis_client


class ContentSetupMixin:
    @classmethod
    def setup_content(cls):
        res = cls.client.get("/developer/travelline/content/room-categories?save=true", headers=cls.auth_header)
        cls.client.get("/developer/travelline/content/meal-plans?save=true", headers=cls.auth_header)
        cls.client.get("/developer/travelline/content/amenities?save=true", headers=cls.auth_header)
        cls.client.post("/developer/travelline/content?save=True&with_images=false", data={"include": "All"},
            headers=cls.auth_header)

    @classmethod
    def destroy_content(cls):
        for property_db in Property.objects.all():
            try: shutil.rmtree(f"{settings.MEDIA_ROOT}property/{property_db.pk}")
            except: ...

    @classmethod
    def clear_redis_cache(self):
        redis_client.flushdb()
