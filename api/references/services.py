from contrib.common.cached import acached
from apps.shared.models import AmenityCategory, MealPlan, RoomTypeCategory
from .schemas import AmenityCategoryInfo, MealPlanInfo, RoomTypeCategoryInfo


@acached
async def list_amenities():
    qs = AmenityCategory.objects.prefetch_related("amenities")
    return [AmenityCategoryInfo.from_orm(x).model_dump() async for x in qs]


@acached
async def list_meal_plans():
    qs = MealPlan.objects.all()
    return [MealPlanInfo.from_orm(x).model_dump() async for x in qs]


@acached
async def list_room_type_categories():
    qs = RoomTypeCategory.objects.all()
    return [RoomTypeCategoryInfo.from_orm(x).model_dump() async for x in qs]
