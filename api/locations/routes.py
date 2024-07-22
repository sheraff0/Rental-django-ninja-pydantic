from ninja import Router

import api.locations.services as services
from .schemas import RegionInfo, CityInfo

router = Router()


@router.get("regions", response=list[RegionInfo])
async def list_regions(request,
    q: str | None = None,
    limit: int | None = 10,
):
    return (await services.list_regions(q=q))[:limit]


@router.get("cities", response=list[CityInfo])
async def list_cities(request,
    q: str | None = None,
    limit: int | None = 10,
):
    return (await services.list_cities(q=q))[:limit]


@router.get("popular", response=list[CityInfo])
async def popular_cities(request,
    q: str | None = None,
    limit: int | None = 10,
):
    return (await services.popular())[:limit]
