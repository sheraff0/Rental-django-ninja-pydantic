from enum import StrEnum, auto
from uuid import UUID
from datetime import date, timedelta

from django.conf import settings

from ninja import Schema, ModelSchema
from pydantic import conint, model_validator, Field

from contrib.common.pagination import Paginated
from apps.bookings.models import Search
from api.locations.schemas import CityInfo, Coords
from api.properties.schemas import (
    PropertyInfo,
    RoomTypeInfo, RoomTypeInfoWithDistance,
    RatePlanInfo, ServiceInfo
)
from bridge.travelline.search.schemas import SearchParams
from external.travelline.schemas.common import MessageResponse
from external.travelline.schemas.content import Placement
from external.travelline.schemas.search import Total, StayDates, CancellationPolicy


class SearchInfo(ModelSchema):
    city: CityInfo | None

    class Meta:
        model = Search
        exclude = ["user", "create_time", "update_time"]


class AccomodationOffer(Schema):
    days: int
    rate_plan_info: RatePlanInfo | None
    placements: list[Placement]
    placements_description: str
    total: Total
    price_total: float | None = None
    price: float | None = None
    prepayment: float | None = None
    payment_upon_arrival: float | None = None
    stay_dates: StayDates
    cancellation_policy: CancellationPolicy
    included_services: list[ServiceInfo]
    available_services: list[ServiceInfo]
    checksum: str

    @model_validator(mode="after")
    def calc_price(cls, obj):
        try:
            obj.price_total = obj.total.priceBeforeTax + obj.total.taxAmount
            obj.price = round(obj.price_total / obj.days, 2)
            obj.prepayment = obj.price_total * settings.REHO_PREPAYMENT_RATE / 100
            obj.payment_upon_arrival = obj.price_total - obj.prepayment
            # Penalty
            _penalty = obj.cancellation_policy.penaltyAmount
            obj.cancellation_policy.penaltyAmount = min(obj.prepayment, _penalty)
        except: ...
        return obj


class FloorType(StrEnum):
    LAST = auto()
    NOT_FIRST = auto()
    NOT_LAST = auto()


class SearchFilters(Schema):
    price_min: float | None = None
    price_max: float | None = None
    room_type_categories: list[str] | None = None  # RoomTypeCategory codes
    rooms_count: int | None = None
    beds_count: list[int] | None = None
    downtown_distance: int | None = None
    floor_min: int | None = None
    floor_max: int | None = None
    floor_type: FloorType | None = None
    amenities: list[str] | None = None  # Amenity codes


class SearchCoords(Coords):
    radius: int = 50  # km


class SearchRequest(Schema):
    params: SearchParams | None = Field(default_factory=SearchParams)
    city_id: int | None = None
    coords: SearchCoords | None = None
    filters: SearchFilters | None = None


class SearchRequestDetailed(Schema):
    params: SearchParams
    room_type_id: UUID


class AccomodationBase(Schema):
    property_info: PropertyInfo | None
    room_type_info: RoomTypeInfo | None


class Accomodation(AccomodationBase):
    lowest_price_offer: AccomodationOffer


class AccomodationDetailed(AccomodationBase):
    offers: list[AccomodationOffer]


class SearchResponseBase(Schema):
    search: SearchInfo
    errors: list[MessageResponse] | None = None


PaginatedAccomodations = Paginated(Accomodation)


class SearchResponse(SearchResponseBase):
    accomodations: PaginatedAccomodations


class SearchResponseDetailed(SearchResponseBase):
    accomodation: AccomodationDetailed | None = None


class SearchResultsOrderBy(StrEnum):
    DEFAULT = auto()
    PRICE = auto()
    PRICE_DESC = "-price"
    DISTANCE = auto()
