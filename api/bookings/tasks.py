import json

from apps.bookings.models import BookingStatus
from config.celery import app
from contrib.utils.decorators import nested_async
from external.paykeeper.schemas import CallbackRequest
import api.bookings.services as services


@app.task
@nested_async
async def confirm_payment_and_create_booking_task(
    data: CallbackRequest,
):
    _data = CallbackRequest(**json.loads(data))
    await services.confirm_payment_and_create_booking(_data)


@app.task
def set_expired_bookings_task():
    services.set_expired_bookings()


@app.task
@nested_async
async def update_unsettled_payments_status_task():
    await services.update_unsettled_payments_status()
