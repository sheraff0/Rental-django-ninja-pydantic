from contrib.common.cached import acached
from external.travelline.api import travelline_async_client, TravelLine
from external.travelline.schemas import (
    VerifyBookingRequest, CreateBookingRequest,
    ModifyBookingRequest, CancelBookingRequest,
)


@travelline_async_client
async def verify_booking_tl(
    data: VerifyBookingRequest,
    client: TravelLine = None,
):
    return await client.verify_booking(data)


@travelline_async_client
async def create_booking_tl(
    data: CreateBookingRequest,
    client: TravelLine = None,
):
    return await client.create_booking(data)


@travelline_async_client
async def get_booking_tl(
    number: str,
    client: TravelLine = None,
):
    return await client.get_booking(number)


@travelline_async_client
async def update_booking_tl(
    number: str,
    data: ModifyBookingRequest,
    client: TravelLine = None,
):
    return await client.modify_booking(number, data)


@acached(ttl=300)
@travelline_async_client
async def cancellation_penalty_tl(
    number: str,
    client: TravelLine = None,
):
    return await client.cancellation_penalty(number)


@travelline_async_client
async def cancel_booking_tl(
    number: str,
    data: CancelBookingRequest,
    client: TravelLine = None,
):
    return await client.cancel_booking(number, data)
