from ninja import Schema, ModelSchema
from pydantic import field_validator

from apps.shared.models import AmenityCategory, Amenity, MealPlan, RoomTypeCategory
from contrib.utils.gis import coords_to_list


class AmenityInfo(ModelSchema):
    class Meta:
        model = Amenity
        exclude = ["id", "amenity_category"]


class AmenityCategoryInfo(ModelSchema):
    amenities: list[AmenityInfo]

    class Meta:
        model = AmenityCategory
        exclude = ["id"]


class MealPlanInfo(ModelSchema):
    class Meta:
        model = MealPlan
        exclude = ["id"]


class RoomTypeCategoryInfo(ModelSchema):
    class Meta:
        model = RoomTypeCategory
        exclude = ["id"]
