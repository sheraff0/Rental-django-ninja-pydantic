import json
from datetime import datetime

from django.conf import settings

from contrib.common.pydantic import json_clean
from contrib.utils.async_api_client import AsyncClient, async_api_client, async_to_sync_api_client
from .schemas import (
    PropertiesRequest, PropertiesResponse, PropertiesBriefResponse, PropertyInfo,
    SpecificAccomodationSearchRequest, LowestPriceSearchRequest,
    VerifyBookingRequest, CreateBookingRequest,
    ModifyBookingRequest, CancelBookingRequest,
)


class TravelLine:
    def __init__(self):
        self.client = AsyncClient(
            api_url=settings.TRAVELLINE_API_URL,
            default_headers={
                "X-API-KEY": settings.TRAVELLINE_API_KEY,
                "Content-Type": "application/json"
            }
        )

    # Content API
    async def list_properties(self, data: PropertiesRequest) -> PropertiesResponse:
        params = data.dict(exclude_unset=True)
        res = await self.client.request(f"/content/v1/properties", params=params)
        return (
            PropertiesResponse if params.get("include") == "All"
            else PropertiesBriefResponse
        )(**res)

    async def retrieve_property(self, property_id: int) -> PropertyInfo:
        return await self.client.request(f"/content/v1/properties/{property_id}")

    async def meal_plans(self):
        return await self.client.request("/content/v1/meal-plans")

    async def room_categories(self):
        return await self.client.request("/content/v1/room-type-categories")

    async def amenities(self):
        return await self.client.request("/content/v1/room-amenity-categories")

    # Search API
    async def lowest_price_search(self, data: LowestPriceSearchRequest):
        _json = json_clean(data)
        return await self.client.request(f"/search/v1/properties/room-stays/search", method="post", json=_json)

    async def specific_accomodation_search(self, data: SpecificAccomodationSearchRequest):
        params = json_clean(data)
        property_id = params.pop("property_id")
        return await self.client.request(f"/search/v1/properties/{property_id}/room-stays", params=params)

    # Reservations API
    async def verify_booking(self, data: VerifyBookingRequest):
        _json = json_clean(data)
        return await self.client.request(f"/reservation/v1/bookings/verify", method="post", json=_json)

    async def create_booking(self, data: CreateBookingRequest):
        _json = json_clean(data)
        return await self.client.request(f"/reservation/v1/bookings", method="post", json=_json)

    async def get_booking(self, number: str):
        return await self.client.request(f"/reservation/v1/bookings/{number}")

    async def modify_booking(self, number: str, data: ModifyBookingRequest):
        _json = json_clean(data)
        return await self.client.request(f"/reservation/v1/bookings/{number}/modify", method="post", json=_json)

    async def cancellation_penalty(self, number: str):
        params = dict(cancellationDateTimeUtc=str(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")))
        return await self.client.request(f"/reservation/v1/bookings/{number}/calculate-cancellation-penalty",
            params=params)

    async def cancel_booking(self, number: str, data: CancelBookingRequest):
        _json = json_clean(data)
        return await self.client.request(f"/reservation/v1/bookings/{number}/cancel", method="post", json=_json, log=True)


travelline_async_client = async_api_client(TravelLine)
travelline_sync_client = async_to_sync_api_client(TravelLine)
