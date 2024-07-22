from external.travelline.schemas.content import (
    AmenityCategory as AmenityCategoryInfo,
    Amenity as AmenityInfo,
)
from apps.shared.models import Amenity, AmenityCategory
from contrib.common.cached import CachedModelMap
from .import_data import ImportData


class AmenityCategoryImport(ImportData):
    source_model = AmenityCategoryInfo

    async def import_object(self, data: AmenityCategoryInfo):
        _category, _ = await AmenityCategory.objects.aget_or_create(name=data.name)
        for amenity in data.amenities:
            await Amenity.objects.aget_or_create(amenity_category=_category, **amenity.model_dump())
        return _category


get_amenity = CachedModelMap(model=Amenity)

AMENITIES_TO_FIELD = {
    "two_rooms": ("rooms", 2),
    "three_rooms": ("rooms", 3),
    "four_rooms": ("rooms", 4),
    "non_smoking_room": ("non_smoking", True),
}
