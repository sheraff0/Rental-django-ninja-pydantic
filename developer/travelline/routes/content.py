from ninja import Router

from external.travelline.schemas import (
    PropertiesRequest, PropertiesResponse, PropertiesBriefResponse, PropertyInfo,
    MealPlan, RoomCategory, AmenityCategory,
)
import bridge.travelline.content.services as services

router = Router()


@router.post("",
    response=PropertiesResponse | PropertiesBriefResponse,
    exclude_unset=True
)
async def properties(request,
    data: PropertiesRequest,
    save: bool = False,
    with_images: bool = True,
):
    return await services.import_properties(data=data, save=save, with_images=with_images)


@router.get("/meal-plans", response=list[MealPlan])
async def meal_plans(request,
    save: bool = False,
):
    return await services.import_meal_plans(save=save)


@router.get("/room-categories", response=list[RoomCategory])
async def room_categories(request,
    save: bool = False,
):
    return await services.import_room_categories(save=save)


@router.get("/amenities", response=list[AmenityCategory])
async def amenities(request,
    save: bool = False,
):
    return await services.import_amenities(save=save)
