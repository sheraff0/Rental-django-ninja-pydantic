from dataclasses import dataclass
from uuid import UUID

from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from apps.properties.models import Property, RoomType, RatePlan, Service
from contrib.common.cached import acached
from contrib.common.pydantic import json_clean
from contrib.common.redis import redis_client
from contrib.utils.date_time import timeit
from .schemas import PropertyInfo, RoomTypeInfo, RatePlanInfo, ServiceInfo


@acached(ttl=900)
async def get_properties_map_entries():
    return [(str(x.tl_id), PropertyInfo.from_orm(x).model_dump())
        async for x in Property.objects.select_related(
            "address"
        ).prefetch_related(
            "images",
            "room_types__amenities",
            "room_types__images",
            "room_types__address",
        ).all()]


@acached(ttl=900)
async def get_property(tl_id: int | str):
    _map_entries = await get_properties_map_entries()
    _map = dict(_map_entries)
    return _map.get(str(tl_id))


@acached(ttl=900)
async def get_room_types_map_entries():
    return [(str(x.tl_id), RoomTypeInfo.from_orm(x).model_dump())
        async for x in RoomType.objects.rating().select_related(
            "address",
            "category",
        ).prefetch_related(
            "images",
            "amenities",
        ).all()]


@acached(ttl=900)
async def get_room_type(tl_id: int | str):
    _map_entries = await get_room_types_map_entries()
    _map = dict(_map_entries)
    return _map.get(str(tl_id))


async def get_room_type_object(pk: UUID):
    try:
        room_type_obj = await RoomType.objects.select_related("property_obj__address").filter(pk=pk).afirst()
        assert room_type_obj
        return room_type_obj
    except:
        raise HttpError(400, str(_("Room type not found")))


@acached(ttl=900)
async def get_rate_plans_map_entries():
    return [(str(x.tl_id), RatePlanInfo.from_orm(x).model_dump())
        async for x in RatePlan.objects.all()]


@acached(ttl=900)
async def get_rate_plan(tl_id: int | str):
    _map_entries = await get_rate_plans_map_entries()
    _map = dict(_map_entries)
    return _map.get(str(tl_id))


@acached(ttl=900)
async def get_services_map_entries():
    return [(str(x.tl_id), ServiceInfo.from_orm(x).model_dump())
        async for x in Service.objects.select_related(
            "meal_plan"
        ).all()]


@acached(ttl=900)
async def get_service(tl_id: int | str):
    _map_entries = await get_services_map_entries()
    _map = dict(_map_entries)
    return _map.get(str(tl_id))


@timeit
@acached(ttl=900)
async def set_room_type_coords():
    _map = [x for y in [(x.coords.x, x.coords.y, str(x.pk))  # longitude, latitude, name
        async for x in RoomType.objects.coords() if x.coords] for x in y]
    redis_client.geoadd("room_type", _map)
    return True


@acached(ttl=900)
async def get_distance(key1, key2):
    return redis_client.geodist("room_type", key1, key2, "km")


def set_key(lon, lat):
    _key = f"point_{lon}_{lat}"
    redis_client.geoadd("room_type", (lon, lat, _key))


@dataclass
class GeoDistances:
    lon: float
    lat: float
    round_by: int = 4

    def __post_init__(self):
        self.round()
        self._key = f"point_{self.lon}_{self.lat}"
        redis_client.geoadd("room_type", (self.lon, self.lat, self._key))

    def round(self):
        self.lon, self.lat = [round(x, self.round_by) for x in (self.lon, self.lat)]

    @classmethod
    async def set(cls):
        await set_room_type_coords()
    
    async def get_distance(self, room_type_id):
        return await get_distance(self._key, str(room_type_id))

    @classmethod
    def close(cls):
        redis_client.zrem("room_type", _key)