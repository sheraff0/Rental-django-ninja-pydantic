from django.test import TestCase

from apps.shared.models import RoomTypeCategory, AmenityCategory, Amenity
from apps.properties.models import Property, RoomType
from .mixins import AuthSetupMixin, ContentSetupMixin


class ContentTestCase(ContentSetupMixin, AuthSetupMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setup_auth_data()
        cls.setup_content()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_content()

    def test_property(self):
        property_db = Property.objects.first()
        assert property_db
        room_types_count = property_db.room_types.count()
        assert room_types_count > 0
