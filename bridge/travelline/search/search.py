from external.travelline.api import travelline_async_client, TravelLine
from external.travelline.schemas import LowestPriceSearchRequest, SpecificAccomodationSearchRequest
from .schemas import SearchParams


@travelline_async_client
async def lowest_price_search(
    params: SearchParams,
    property_ids: list[int],
    client: TravelLine = None,
):
    request_data = LowestPriceSearchRequest(
        propertyIds=map(str, property_ids),
        arrivalDate=params.arrival_date,
        departureDate=params.departure_date,
        adults=params.adults,
        childAges=params.children
    )
    return await client.lowest_price_search(request_data)


@travelline_async_client
async def specific_accomodation_search(
    params: SearchParams,
    property_id: int,
    client: TravelLine = None,
):
    request_data = SpecificAccomodationSearchRequest(
        property_id=str(property_id),
        arrivalDate=params.arrival_date,
        departureDate=params.departure_date,
        adults=params.adults,
        childAges=params.children
    )
    return await client.specific_accomodation_search(request_data)
