from uuid import UUID
from datetime import datetime

from django.template.response import TemplateResponse, HttpResponse

from ninja import Router, Form, Query
from ninja.errors import HttpError
from ninja.responses import Response

import api.bookings.services as services
from contrib.ninja.auth import AuthBearer, AuthIfMatch
from external.paykeeper.schemas import CallbackRequest, PayKeeperAccount
from external.travelline.schemas.common import MessageResponse
from .schemas import (
    BookingVerify, BookingBrief,
    BookingInfo, PaginatedBookingInfo,
    PayBookingRequest, PayBookingResponse,
    BookingCustomizable, PenaltyInfo,
    BookingRating,
)
from .tasks import confirm_payment_and_create_booking_task

router = Router()

backdoor_auth = dict(auth=[
    AuthIfMatch(audience="bookings:cancel"),
    AuthBearer(),
])


@router.post("/verify", response=BookingInfo | list[MessageResponse])
async def verify_booking(request,
    data: BookingVerify,
    corrupted: bool = False,
):
    """Request
    ---
    Data from (1) `/search` or (2) `/search/detailed` results (from (1) `accomodations.results[]` or (2) `accomodation` respectively):\n
    - `search.id` - search objects containing essential booking params;
    - `property_info.id`;
    - `room_type_info.id`;
    - `rate_plan_info.id`, `placements`, `checksum` (from (1) `lowest_price_offer` or (2) `offers[]`);

    ---
    Response
    ---
    Brief booking object:
    - `id` - for further requests;
    - `status` - should be `verified` at this stage.
    """
    res = await services.verify_booking(request.user, data, corrupted=corrupted)
    try:
        return res
    except:
        return Response((res.warnings or []) + (res.errors or []), status=400)


@router.get("", response=PaginatedBookingInfo)
async def list_bookings(request,
    page: int | None = 1,
    size: int | None = 4,
    include_outdated: bool | None = False,
):
    return await services.list_bookings(request.user, page=page, size=size, include_outdated=include_outdated)


def check_booking_id(request, id):
    if _data := getattr(request, "data", None):
        try:
            assert str(_data["booking_id"]) == str(id)
        except:
            raise HttpError(403, "Resource unavailable")


@router.get("/{id}", **backdoor_auth, response=BookingInfo)
async def get_booking(request,
    id: UUID,
):
    """Dual auth:
    - standard - `Authorization: Bearer <token>`;
    - temporary - `If-Match: Token <JWT token>`; JWT is valid only for this resource.
    """
    check_booking_id(request, id)
    return await services.get_booking(id, request.user)


@router.post("/{id}/pay", response=PayBookingResponse)
async def init_payment(request,
    id: UUID,
    data: PayBookingRequest,
):
    """Response
    ---
    Brief booking object, including:
    - `payments`:
        - should contain PaymentInfo object, with `invoice_url` and `status: pending`.
    """
    return await services.init_payment(id, request, data)


@router.post("/{id}/refresh-payment-status", response=BookingInfo)
async def refresh_payment_status(request,
    id: UUID,
):
    return await services.refresh_payment_status(id, request.user)


@router.post("/{id}/book", response=BookingBrief)
async def create_booking(request,
    id: UUID,
):
    """For testing purposes only
    ---
    """
    return await services.create_booking(id, request.user)


@router.patch("/{id}", response=BookingInfo)
async def update_booking(request,
    id: UUID,
    data: BookingCustomizable,
):  
    return await services.update_booking(id, request.user, data)


@router.get("/{id}/cancel/penalty", **backdoor_auth, response=PenaltyInfo)
async def cancellation_penalty(request,
    id: UUID,
):
    """Dual auth:
    - standard - `Authorization: Bearer <token>`;
    - temporary - `If-Match: Token <JWT token>`; JWT is valid only for this resource.
    """
    check_booking_id(request, id)
    return await services.cancellation_penalty(id, request.user)


@router.post("/{id}/cancel", **backdoor_auth, response=BookingInfo)
async def cancel_booking(request,
    id: UUID,
):
    """Dual auth:
    - standard - `Authorization: Bearer <token>`;
    - temporary - `If-Match: Token <JWT token>`; JWT is valid only for this resource.
    """
    check_booking_id(request, id)
    return await services.cancel_booking(id, request.user)


@router.post("/{id}/rate", response=BookingInfo)
async def rate_booking(request,
    id: UUID,
    data: BookingRating,
):  
    return await services.rate_booking(id, request.user, data)


bookings_router = router
router = Router()


@router.post("/paykeeper/callback", auth=None, response=str)
async def confirm_payment(request,
    data: Form[CallbackRequest],
):
    confirm_payment_and_create_booking_task.delay(data.model_dump_json())
    return HttpResponse(f"OK {data.ok}", content_type="text/plain")


@router.get("/paykeeper/user-callback", auth=None)
async def user_result_callback(request):
    return TemplateResponse(request, "payments/paykeeper/user-result-callback.html")


@router.get("/sleep")
async def sleep(request):
    return await services.sleep()


payments_router = router
