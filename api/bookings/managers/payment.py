import asyncio
from dataclasses import dataclass

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import (
    Booking, BookingStatus,
    Payment, PaymentStatus, PaymentPurpose,
)
from api.common.tasks import send_mail_task
from external.paykeeper.services import invoice_preview, refund, payments_search, payment_info
from external.paykeeper.schemas import (
    InvoicePreviewRequest, InvoicePreviewResponse,
    ServiceName, CartItem,
    CallbackRequest, CallbackRequestStatus, RefundRequest, ErrorResponse,
    PaymentsSearchParams, Payment as PaymentPayKeeper,
    PayKeeperAccount,
)
from ..schemas import PayBookingRequest
from .common import ProcessBookingManagerBase


@dataclass
class InitPaymentManager(ProcessBookingManagerBase):
    purpose: PaymentPurpose = PaymentPurpose.PREPAYMENT
    data: PayBookingRequest = None

    def check_payment(self):
        assert not Payment.objects.filter(
            booking=self._booking,
            purpose=self.purpose,
        ).exists(), _("Payment for this purpose already exists")

    def set_amount(self):
        assert self.purpose == PaymentPurpose.PREPAYMENT, \
            _("Algorithm not defined for this purpose")
        self._amount = self._booking.prepayment

    def set_service_name(self):
        self._service_name = "Бронирование номера"

    def check_account(self):
        _suffix = self.data.account.upper()
        assert all((
            getattr(settings, f"PAYKEEPER_API_URL_{_suffix}"),
            getattr(settings, f"PAYKEEPER_BASIC_AUTH_HEADER_{_suffix}")
        )), _("Payment account credentials not defined")

    def set(self):
        assert self._booking.status == BookingStatus.VERIFIED, _("Payment impossible")
        assert not self._booking.paid, _("Booking already paid")
        assert self._booking.prepayment > 0, _("No prepayment needed")
        self.check_account()
        self.check_payment()
        self.set_amount()
        self.set_service_name()

    def get_cart(self):
        return [CartItem(
            name=self._service_name,
            price=self._amount,
        )]

    def get_service_name(self):
        return ServiceName(
            user_result_callback=self.data.user_result_callback,
            service_name=self._service_name,
            cart=self.get_cart(),
        ).model_dump_json(exclude_none=True)

    def get_order_id(self):
        return f"{self.data.account}-{self._booking.id}"

    def get_invoice_request(self):
        return InvoicePreviewRequest(
            pay_amount=self._amount,
            clientid=str(self.user.id),
            orderid=self.get_order_id(),
            service_name=self.get_service_name(),
            client_email=self.email,
            client_phone=self.user.phone_str,
        )

    async def process(self):
        self._request = self.get_invoice_request()
        _response = await invoice_preview(self._request, account=self.data.account)
        _error = _response.get("msg")
        assert not _error, _error
        try:
            self._response = InvoicePreviewResponse(**_response)
        except:
            assert False, _("Unable to get invoice")

    def save(self):
        self._payment = Payment.objects.create(
            booking=self._booking,
            purpose=self.purpose,
            amount=self._amount,
            invoice_url=self._response.invoice_url,
            expiry=self._request.expiry,
            paykeeper_account=self.data.account,
        )

    def post_save(self):
        ...
        #self.notify()

    def notify(self):
        _booking_prepayment = _("Booking prepayment")
        subject = f"""[Reho24] {_booking_prepayment}!"""
        html_message = self._response.invoice
        message = html_message
        send_mail_task.delay(self.email, subject, message, html_message)


@dataclass
class ProcessBookingPaymentManagerBase(ProcessBookingManagerBase):
    purpose: PaymentPurpose = PaymentPurpose.PREPAYMENT
    account: PayKeeperAccount = None

    def set_payment(self):
        self._payment = Payment.objects.select_for_update().filter(**{
            **dict(
                booking=self._booking,
                purpose=self.purpose,
            ),
            **(dict(paykeeper_account=self.account) if self.account else {}),
        }).first()
        assert self._payment, _("Payment not found")


@dataclass
class RefreshPaymentStatusManager(ProcessBookingPaymentManagerBase):
    lock: bool = False

    def set(self):
        self.set_payment()

    def get_search_params(self):
        return PaymentsSearchParams(
            query="-".join((self._payment.paykeeper_account, str(self._booking.id))),
        )

    async def process(self):
        if _id := self._payment.paykeeper_id:
            res = await payment_info(_id)
            assert res, _("Payment not found")
            self._response_object = PaymentPayKeeper(**res)
        else:
            _params = self.get_search_params()
            res = await payments_search(_params, account=self._payment.paykeeper_account)
            assert res, _("Payment not found")
            self._response_object = PaymentPayKeeper(**res[0])

    def save(self):
        _status = self._response_object.status
        self._payment.paykeeper_id = self._response_object.id
        self._payment.status = _status
        self._payment.refunded = self._response_object.refund_amount
        self._payment.save()


@dataclass
class ConfirmPaymentManager(ProcessBookingPaymentManagerBase):
    data: CallbackRequest = None

    def set(self):
        self.set_payment()
        assert int(self.data.sum) >= int(self._payment.amount), \
            _("Confirmed amount too small to proceed with booking")

    async def process(self):
        ...

    def save(self):
        if self.data.status == CallbackRequestStatus.FAIL:
            self._payment.status = PaymentStatus.FAILED
        else:
            self._payment.status = PaymentStatus.SUCCESS
            self._booking.paid = True
        self._payment.paykeeper_id = self.data.id
        self._payment.save()



@dataclass
class RefundManager(ProcessBookingPaymentManagerBase):
    amount: float = None

    def set(self):
        self.set_payment()
        assert self._payment.status == PaymentStatus.SUCCESS, _("Cannot be refunded")
        self.amount = min(self._payment.amount, self.amount)

    def get_request(self):
        return RefundRequest(
            id=self._payment.paykeeper_id,
            amount=self.amount,
            partial=False,
        )

    async def process(self):
        # Init refund
        _data = self.get_request()
        _response = await refund(_data)
        _response = ErrorResponse(**_response)
        assert _response.result == "success", _response.msg
        # Await refund
        _count = 5
        while _count > 0:
            await asyncio.sleep(3)
            res = await payment_info(self._payment.paykeeper_id)
            assert res, _("Cannot retrieve payment info")
            self._response_object = PaymentPayKeeper(**res)
            if self._response_object.status == PaymentStatus.REFUNDED:
                break
            _count -= 1

    def save(self):
        self._payment.status = self._response_object.status
        self._payment.save()

        self._booking.paid = False
