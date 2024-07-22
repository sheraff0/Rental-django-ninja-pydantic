from apps.properties.models import Property
from external.travelline.api import travelline_async_client, TravelLine
from external.travelline.schemas import (
    PropertiesRequest, PropertiesResponse, PropertiesBriefResponse, PropertyInfo,
    MealPlan, RoomCategory, AmenityCategory,
)

from .amenity import AmenityCategoryImport
from .room_category import RoomCategoryImport
from .property import PropertyImport
from .meal_plan import MealPlanImport


@travelline_async_client
async def import_properties(
    data: PropertiesRequest,
    save: bool = False,
    with_images: bool = True,
    client: TravelLine = None,
):
    res = await client.list_properties(data)
    if save and data.include.value == "All":
        await PropertyImport(res.properties, validated=True, with_images=with_images)()
    return res


async def unlink_all_properties():
    await Property.objects.aupdate(tl_linked=False)


async def import_all_properties(
    save: bool = False,
    with_images: bool = True,
):
    await unlink_all_properties()
    data = PropertiesRequest(include="All")
    while True:
        res = await import_properties(data, save=save, with_images=with_images)
        if not res.next:
            break
        data.since = res.next


@travelline_async_client
async def import_meal_plans(
    save: bool = False,
    client: TravelLine = None,
):
    res = await client.meal_plans()
    if save:
        await MealPlanImport(res)()
    return res


@travelline_async_client
async def import_room_categories(
    save: bool = False,
    client: TravelLine = None,
):
    res = await client.room_categories()
    if save:
        await RoomCategoryImport(res)()
    return res


@travelline_async_client
async def import_amenities(
    save: bool = False,
    client: TravelLine = None,
):
    res = await client.amenities()
    if save:
        await AmenityCategoryImport(res)()
    return res
