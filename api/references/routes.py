from ninja import Router

import api.references.services as services
from .schemas import AmenityCategoryInfo, MealPlanInfo, RoomTypeCategoryInfo

router = Router()


@router.get("amenities", response=list[AmenityCategoryInfo])
async def list_amenities(request,
):
    return await services.list_amenities()


@router.get("meal-plans", response=list[MealPlanInfo])
async def list_meal_plans(request,
):
    return await services.list_meal_plans()


@router.get("room-type-categories", response=list[RoomTypeCategoryInfo])
async def list_room_type_categories(request,
):
    return await services.list_room_type_categories()
