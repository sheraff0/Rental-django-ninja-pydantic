from ninja import Router

from external.travelline.api import travelline_async_client
from external.travelline.schemas import (
    VerifyBookingRequest, VerifyBookingResponse,
    CreateBookingRequest, CreateBookingResponse,
)

router = Router()


@router.post("",
    response=CreateBookingResponse,
    exclude_unset=True,
)
@travelline_async_client
async def create_booking(request,
    data: CreateBookingRequest,
    client = None,
):
    return await client.create_booking(data)


@router.post("/verify",
    response=VerifyBookingResponse,
    exclude_unset=True,
)
@travelline_async_client
async def verify_booking(request,
    data: VerifyBookingRequest,
    client = None,
):
    res = await client.verify_booking(data)
    print(res)
    return res
