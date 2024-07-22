from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from contrib.common.cached import acached
from apps.bookings.models import Search
from apps.shared.models import Region, City
from .schemas import CityInfo, RegionInfo


@acached(ttl=3600)
async def list_regions(
    q: str | None = None,
):
    qs = Region.objects.search(q=q).prefetch_related("cities")
    return [RegionInfo.from_orm(x).model_dump() async for x in qs]


@acached(ttl=3600)
async def list_cities(
    q: str | None = None,
):
    qs = City.objects.search(q=q).select_related("region")
    return [CityInfo.from_orm(x).model_dump() async for x in qs]


@acached(ttl=3600)
async def popular():
    qs = City.objects.popular().select_related("region")
    res = [CityInfo.from_orm(x).model_dump() async for x in qs]
    return sorted(res, key=lambda x: -(x["count"] or 0))


async def check_city(
    id: int | None
):
    if id is None:
        return
    city = await City.objects.filter(id=id).values("id").afirst()
    if not city:
        raise HttpError(400, str(_("City not found")))
