from external.travelline.api import travelline_async_client
from external.travelline.schemas import VerifyBookingRequest


@travelline_async_client
async def verify_booking_tl(
    data: VerifyBookingRequest,
    client=None,
):
    return await client.verify_booking(data)
