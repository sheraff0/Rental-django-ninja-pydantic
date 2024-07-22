from ninja import Router, Query
from ninja.errors import HttpError

from pydantic import conint

from api.locations.services import check_city
from api.locations.schemas import Coords
from api.properties.services import get_property, get_room_type
import api.search.services as services
from .schemas import (
    SearchRequest, SearchRequestDetailed,
    SearchResponse, SearchResponseDetailed,
    SearchInfo, SearchResultsOrderBy,
)

router = Router()


@router.post("", response=SearchResponse, exclude_none=True)
async def get_search(request,
    data: SearchRequest,
    page: conint(ge=1) | None = 1,
    size: conint(ge=1, le=96) | None = 4,
    order_by: SearchResultsOrderBy | None = None,
    reset_cache: bool = False,
):
    """Request
    ---
    All body attributes are optional.\n
    `params` - desired accomodation; if not provided, default values are used (1 person, 1 day);\n
    `city_id` - search by city;\n
    `coords` - search by (user) geolocation, within `radius` (km);\n
    `coords.radius: 0` - select closest offers, range by `distance`, number may vary;\n
    `filters` - filter by accomodation params;\n
    `order_by`: **price | -price | distance**\n
    if `coords.radius: 0` is set to `order_by=distance`

    ---
    Response
    ---
    `search` - search request object;\n
    `accomodation.results`:
    - `property_info` - property info;\n
    - `room_type_info`: `distance` - distance to user geolocation, if provided; `address` - may differ from `property.address`;
    - `lowest_price_offer` - accomodation offer with lowest price for this property/room.
    """
    await check_city(data.city_id)
    return await services.search(request.user, data=data,
        page=page, size=size, order_by=order_by, reset_cache=reset_cache)


@router.get("/history", response=list[SearchInfo])
async def history(request,
    include_past: bool = False,
    include_blank_city: bool = False,
    limit: int = 10,
):
    return await services.history(request.user, include_past=include_past,
        include_blank_city=include_blank_city, limit=limit)


@router.post("/detailed", exclude_none=True, response=SearchResponseDetailed)
async def search_detailed(request,
    data: SearchRequestDetailed,
    reset_cache: bool = False,
):
    return await services.search_detailed(request.user, data=data, reset_cache=reset_cache)
