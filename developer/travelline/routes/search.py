from datetime import date

from ninja import Router

from external.travelline.api import travelline_async_client
from external.travelline.schemas import (
    SpecificAccomodationSearchRequest, SpecificAccomodationSearchResponse,
    LowestPriceSearchRequest, LowestPriceSearchResponse,
)

router = Router()


@router.post("/lowest-price-search",
    response=LowestPriceSearchResponse,
    exclude_unset=True
)
@travelline_async_client
async def lowest_price_search(request,
    data: LowestPriceSearchRequest,
    client = None,
):
    return await client.lowest_price_search(data)


@router.post("/specific-accomodation-search",
    response=SpecificAccomodationSearchResponse,
    exclude_unset=True
)
@travelline_async_client
async def specific_accomodation_search(request,
    data: SpecificAccomodationSearchRequest,
    client = None,
):
    return await client.specific_accomodation_search(data)
