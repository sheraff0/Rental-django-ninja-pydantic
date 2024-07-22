from dataclasses import dataclass
from random import sample

from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from api.properties.services import (
    get_property,
    get_room_type,
    get_room_type_object,
    get_rate_plan,
    get_service,
    GeoDistances,
)
from apps.properties.models import Property, RoomType
from apps.bookings.models import Search
from bridge.travelline.search import lowest_price_search, specific_accomodation_search
from contrib.users.models import User
from contrib.common.cached import acached, amemo
from contrib.common.pagination import get_paginated
from contrib.utils.date_time import timeit
from external.travelline.schemas import LowestPriceSearchResponse, SpecificAccomodationSearchResponse
from external.travelline.schemas.search import DetailedRoomStay, IncludedRoomStayService, AvailableRoomStayService
from .filters import SearchFilterSet
from .schemas import (
    SearchParams, SearchCoords,
    SearchRequest, SearchRequestDetailed,
    SearchResponse, SearchResponseDetailed,
    Accomodation, AccomodationOffer, AccomodationDetailed,
    SearchResultsOrderBy,
)


@dataclass
class SearchLocation:
    region_id: int | None = None
    city_id: int | None = None
    coords: SearchCoords | None = None
    only_tl: bool = True

    def __post_init__(self):
        if self.coords:
            self.coords = SearchCoords(**self.coords)
        self._location_filter = self.get_location_filter()

    def get_location_filter(self):
        _filter = Q(tl_id__isnull=False, property_obj__tl_linked=True) if self.only_tl else Q()
        if self.region_id:
            _filter &= Q(address__region_id=self.region_id) | Q(property_obj__address__region_id=self.region_id)
        if self.city_id:
            _filter &= Q(address__city_id=self.city_id) | Q(property_obj__address__city_id=self.city_id)
        if self.coords and self.coords.radius > 0:
            _filter &= Q(distance__lt=self.coords.radius * 1000)
        return _filter

    @property
    def queryset(self):
        _qs = RoomType.objects
        if self.coords:
            _qs = _qs.coords().distance(self.coords.lon, self.coords.lat)
        _qs = _qs.filter(self._location_filter).values_list("property_obj__tl_id", flat=True)
        if self.coords and self.coords.radius == 0:
            _qs = _qs.order_by("distance")[:20]
        return _qs


    async def get_property_ids(self):
        _ids = tuple(set([x async for x in self.queryset]))
        if not self.region_id and not self.city_id and not self.coords:
            n = min(10, len(_ids))
            _ids = sample(_ids, n)
        return _ids

    async def __call__(self):
        return await self.get_property_ids()


@timeit
@acached(ttl=300)
async def seek_properties_by_location(**kwargs):
    return await SearchLocation(**kwargs)()


@timeit
@acached(ttl=300)
async def search_tl(property_ids, params: SearchParams, **kwargs):
    if not property_ids:
        return {}
    try:
        return await lowest_price_search(params, property_ids)
    except:
        raise HttpError(400, str(_("TL server error")))


async def get_search(
    user: User,
    city_id: int,
    params: SearchParams,
):
    search, _ = await Search.objects.aupdate_or_create(
        user=user, city_id=city_id, **params.model_dump())
    search = await Search.objects.select_related("city__region").filter(pk=search.pk).afirst()
    return search


async def get_services(
    services: list[IncludedRoomStayService] | list[AvailableRoomStayService]
):
    return [
        {
            **(service_data),
            "price": getattr(y, "price", None)
        }
        for y in services
        if (service_data := await get_service(y.id))
    ]


@amemo(key_attr="checksum")
async def get_offer(
    x: DetailedRoomStay,
    days: int,
    reset_cache: bool = False,
):
    included_services, available_services = [
        await get_services(services)
        for services in (
            x.includedServices or [],
            x.availableServices or [],
        )
    ]

    return AccomodationOffer(
        rate_plan_info=await get_rate_plan(x.ratePlan.id, reset_cache=reset_cache),
        placements=x.roomType.placements,
        total=x.total,
        days=days,
        placements_description=x.fullPlacementsName,
        stay_dates=x.stayDates,
        cancellation_policy=x.cancellationPolicy,
        included_services=included_services,
        available_services=available_services,
        checksum=x.checksum,
    )


async def get_room_type_with_distance(
    tl_id,
    distances: GeoDistances,
    reset_cache: bool = False,
):
    _room_type = await get_room_type(tl_id, reset_cache=reset_cache)
    if distances:
        _distance = await distances.get_distance(_room_type["id"])
        _room_type["distance"] = _distance
    return _room_type


async def search(
    user: User,
    data: SearchRequest,
    page: int | None = 1,
    size: int | None = 4,
    order_by: SearchResultsOrderBy | None = None,
    reset_cache: bool = False,
):
    property_ids = await seek_properties_by_location(**{
        **(dict(city_id=data.city_id) if data.city_id else {}),
        **(dict(coords=data.coords.model_dump()) if data.coords else {}),
        "reset_cache": reset_cache,
    })

    res = await search_tl(property_ids, data.params, reset_cache=reset_cache)
    response = LowestPriceSearchResponse(**res)

    search = await get_search(user=user, city_id=data.city_id, params=data.params)

    distances = None
    if data.coords:
        distances = GeoDistances(lon=data.coords.lon, lat=data.coords.lat)
        await distances.set()

    accomodations = response.roomStays and [
        Accomodation(
            property_info=await get_property(x.propertyId, reset_cache=reset_cache),
            room_type_info=await get_room_type_with_distance(x.roomType.id, distances=distances, reset_cache=reset_cache),
            lowest_price_offer=await get_offer(x, days=data.params.days, reset_cache=True),  # reset_cache),
        ) for x in response.roomStays
    ] or []

    if accomodations and data.filters:
        accomodations = SearchFilterSet(data=accomodations, filters=data.filters)()

    OB = SearchResultsOrderBy
    if data.coords and data.coords.radius == 0:
        order_by = OB.DISTANCE

    accomodations = sorted(accomodations, key=lambda x: [
        -int(x.property_info.is_reho),
        *([{
            OB.PRICE: x.lowest_price_offer.price,
            OB.PRICE_DESC: -x.lowest_price_offer.price,
            OB.DISTANCE: x.room_type_info.distance or 99999,
        }[order_by]] if order_by else []),
    ])

    return SearchResponse(
        search=search,
        accomodations=get_paginated(accomodations, page, size),
        errors=response.errors,
    )


async def history(
    user: User,
    include_past: bool = False,
    include_blank_city: bool = False,
    limit: int = 10,
):
    return [x async for x in Search.objects.select_related("city__region").filter(
        user=user,
        **(dict(arrival_date__gte=now().date()) if not include_past else {}),
        **(dict(city_id__isnull=False) if not include_blank_city else {}),
    ).all()[:limit]]


@timeit
@acached(ttl=300)
async def search_tl_detailed(property_tl_id, params: SearchParams, **kwargs):
    try:
        return await specific_accomodation_search(params, property_tl_id)
    except:
        raise HttpError(400, str(_("TL server error")))


async def search_detailed(
    user: User,
    data: SearchRequestDetailed,
    reset_cache: bool = False,
):
    room_type_obj = await get_room_type_object(data.room_type_id)
    property_tl_id = room_type_obj.property_obj.tl_id
    room_type_tl_id = room_type_obj.tl_id
    city_id = room_type_obj.property_obj.address.city_id

    search = await get_search(user=user, city_id=city_id, params=data.params)

    res = await search_tl_detailed(property_tl_id, data.params, reset_cache=reset_cache)
    response = SpecificAccomodationSearchResponse(**res)

    offers = [
        await get_offer(x, days=data.params.days, reset_cache=True)  #reset_cache)
        for x in response.roomStays or []
        if x.roomType.id == str(room_type_tl_id)
    ]

    offers = sorted(offers, key=lambda x: x.price)

    accomodation = AccomodationDetailed(
        property_info=await get_property(property_tl_id, reset_cache=reset_cache),
        room_type_info=await get_room_type(room_type_tl_id, reset_cache=reset_cache),
        offers=offers,
    )

    return SearchResponseDetailed(
        search=search,
        accomodation=accomodation,
        errors=response.errors,
    )
