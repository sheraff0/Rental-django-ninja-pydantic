import asyncio
from datetime import datetime
from uuid import UUID

from django.conf import settings
from django.db import transaction

from contrib.common.debounced import debounced
from contrib.users.models import User
from external.paykeeper.schemas import CallbackRequest, PayKeeperAccount
from apps.bookings.models import (
    Booking, BookingHistory, BookingStatus,
    Payment, PaymentStatus,
)
from .managers import (
    get_booking, list_bookings, get_user,
    VerifyBookingManager,
    CreateBookingManager, UpdateBookingManager,
    CancellationPenaltyBookingManager, CancelBookingManager,
    RateBookingManager, RefreshPaymentStatusManager,
    InitPaymentManager, ConfirmPaymentManager, RefundManager,
)
from .schemas import (
    BookingVerify, BookingCustomizable, BookingRating,
    PayBookingRequest, PayBookingResponse,
    PenaltyInfo,
)


@debounced(interval=10, max_queue=1)
async def debounce_booking_operations(user_id: UUID):
    ...


@debounced(interval=10, max_queue=1)
async def debounce_payment_operations(user_id: UUID):
    ...


async def verify_booking(
    user: User,
    data: BookingVerify,
    corrupted: bool = False,
):
    await debounce_booking_operations(str(user.id))
    manager = VerifyBookingManager(user, data, corrupted=corrupted)
    await manager.set()
    _response = await manager.verify_booking_tl()
    _booking = await manager.save()
    if _booking:
        _booking = await get_booking(_booking.pk, user)
        return _booking
    else:
        return _response


async def init_payment(
    id: UUID,
    request,
    data: PayBookingRequest,
):
    user = request.user
    await debounce_payment_operations(str(user.id))
    _callback = request.build_absolute_uri(settings.PAYKEEPER_USER_RESULT_CALLBACK_PATH)
    _manager = InitPaymentManager(id, user, data=PayBookingRequest(
        account=data.account,
        user_result_callback=data.user_result_callback or _callback,
    ))
    await _manager()
    return PayBookingResponse(**_manager._response.model_dump())


async def confirm_payment_and_create_booking(
    data: CallbackRequest,
):
    _booking_id = data.booking_id
    _user = await get_user(data.clientid)
    _account = data.account

    # Update payment status
    try:
        _booking = await ConfirmPaymentManager(_booking_id, _user, data=data, account=_account)()
    except Exception as e:
        print(e)
        return

    # Create booking
    try:
        _booking = await CreateBookingManager(_booking_id, _user)()
        return
    except Exception as e:
        print(e)

    # Refund if failed creating booking
    try:
        await RefundManager(_booking_id, _user, amount=_booking.prepayment)()
    except Exception as e:
        print(e)


async def refresh_payment_status(
    id: UUID,
    user: User,
):
    await debounce_payment_operations(str(user.id))
    await RefreshPaymentStatusManager(id, user)()
    return await get_booking(id, user)


async def create_booking(
    id: UUID,
    user: User,
):
    await debounce_booking_operations(str(user.id))
    return await CreateBookingManager(id, user)()


async def update_booking(
    id: UUID,
    user: User,
    data: BookingCustomizable,
):
    await debounce_booking_operations(str(user.id))
    await UpdateBookingManager(id, user, data=data)()
    return await get_booking(pk, user)


async def cancellation_penalty(
    id: UUID,
    user: User,
):
    await debounce_booking_operations(str(user.id))
    manager = CancellationPenaltyBookingManager(id, user)
    await manager()
    return PenaltyInfo(
        arrival_date=manager._booking.arrival_date,
        departure_date=manager._booking.departure_date,
        prepayment=manager._booking.prepayment,
        penalty=manager.penalty,
        refund=manager.refund,
        amount=manager.penalty,
    )


async def cancel_booking(
    id: UUID,
    user: User,
):
    await debounce_booking_operations(str(user.id))
    manager = CancelBookingManager(id, user)
    await manager()
    if (_refund := manager.refund) > 0:
        await RefundManager(id, user, amount=_refund)()
    return await get_booking(id, user)


async def rate_booking(
    id: UUID,
    user: User,
    data: BookingRating,
):
    await debounce_booking_operations(str(user.id))
    manager = RateBookingManager(id, user, data=data)
    await manager._save()
    _booking = manager._booking
    return await get_booking(_booking.pk, user)


def set_expired_bookings():
    _outdated = BookingStatus.OUTDATED
    _ids = Booking.objects.outdated().filter(
        status=BookingStatus.VERIFIED,
        locked=False,
    ).values_list("pk", flat=True)
    print(f"Verified bookings outdated: {len(_ids)}")
    _count = 0
    for pk in _ids:
        with transaction.atomic():
            _booking = Booking.objects.select_for_update().get(pk=pk)
            if not _booking.locked:
                _booking.status = _outdated
                _booking.save()
                BookingHistory.objects.get_or_create(booking=_booking, status=_outdated)
                _count += 1
    print(f"Marked as outdated: {_count}")


async def update_unsettled_payments_status():
    async for booking_id, user_id in (
        Payment.objects.unsettled().select_related("booking").values_list(
            "booking_id", "booking__user_id")
    ):
        manager = RefreshPaymentStatusManager(booking_id, user_id)
        try:
            await manager()
        except:
            if _payment := manager._payment:
                await _payment.asave()  # rewrite `update_time`
