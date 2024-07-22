from uuid import UUID

from ninja import Schema, ModelSchema, Field
from pydantic import model_validator

from api.locations.schemas import AddressInfo
from api.references.schemas import MealPlanInfo
from apps.properties.models import Property, StayUnit, RoomType, RatePlan, Service
from apps.shared.models import Amenity, AmenityCategory, Address, RoomTypeCategory


class ImageInfo(Schema):
    image: str


class AmenityInfo(ModelSchema):
    class Meta:
        model = Amenity
        exclude = ["id", "amenity_category"]


class RoomTypeCategoryInfo(ModelSchema):
    class Meta:
        model = RoomTypeCategory
        fields = ["code", "name"]


class RoomTypeInfo(ModelSchema):
    amenities: list[AmenityInfo]
    images: list[ImageInfo]
    address: AddressInfo | None
    category: RoomTypeCategoryInfo | None
    distance: float | None = None
    rating: float | None = None

    class Meta:
        model = RoomType
        exclude = ["property_obj", "tl_id", "sort_order", "create_time", "update_time"]


class RoomTypeInfoWithDistance(RoomTypeInfo):
    distance: float | None = None


class PropertyInfo(ModelSchema):
    images: list[ImageInfo] | None = []
    address: AddressInfo | None
    stay_unit: StayUnit | None
    is_reho: bool | None = None

    class Meta:
        model = Property
        exclude = ["tl_id", "tl_linked"]


class RatePlanInfo(ModelSchema):
    class Meta:
        model = RatePlan
        exclude = ["property_obj", "create_time", "update_time", "tl_id"]


class ServiceInfo(ModelSchema):
    meal_plan: MealPlanInfo | None = None
    price: int | None = None

    class Meta:
        model = Service
        fields = ["id", "name", "description", "meal_plan"]
