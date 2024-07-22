from enum import StrEnum, auto
from datetime import date, datetime, timedelta
from uuid import UUID

from django.conf import settings

from ninja.errors import HttpError

from pydantic import (
    BaseModel, EmailStr, Field,
    field_validator, model_validator,
    condecimal,
)

from contrib.common.enum import StrEnumWithChoices
from contrib.utils.hash import md5_hash
from contrib.utils.date_time import get_local_datetime, get_today, get_tomorrow


class PayKeeperAccount(StrEnumWithChoices):
    MOBILE = auto()
    WEB = auto()


class TokenInfo(BaseModel):
    token: str | None


class ResultResponse(BaseModel):
    result: str


class ErrorResponse(ResultResponse):
    msg: str | None = None


def get_expiry():
    _now_msk = get_local_datetime(zone="Europe/Moscow")
    return _now_msk + timedelta(minutes=settings.REHO_BOOKING_EXPIRY_MINUTES)


class Vat(StrEnum):
    none = auto()
    vat0 = auto()
    vat10 = auto()
    vat20 = auto()
    vat110 = auto()
    vat120 = auto()


class CartItem(BaseModel):
    name: str
    price: float
    quantity: int = 1
    sum: float = None
    tax: Vat = Vat.vat20
    #item_type: CartItemType
    #payment_type: CartPaymentType
    #agent: str
    #supplier: str

    @model_validator(mode="after")
    def calc_sum(cls, obj):
        obj.sum = obj.price * obj.quantity
        return obj


class ServiceName(BaseModel):
    user_result_callback: str | None = None
    service_name: str
    cart: list[CartItem]


class InvoicePreviewRequest(BaseModel):
    pay_amount: float
    clientid: str
    orderid: str
    service_name: str
    client_email: EmailStr
    client_phone: str
    expiry: str = Field(default_factory=get_expiry)
    token: str | None = None

    @model_validator(mode="after")
    def serialize_expiry_dt(cls, obj):
        obj.expiry = obj.expiry.strftime("%Y-%m-%d %H:%M:%S")
        return obj


class InvoicePreviewResponse(BaseModel):
    invoice_id: str
    invoice_url: str
    invoice: str


class PaymentStatus(StrEnumWithChoices):
    PENDING = auto()
    OBTAINED = auto()
    CANCELED = auto()
    SUCCESS = auto()
    FAILED = auto()
    STUCK = auto()
    REFUNDED = auto()
    REFUNDING = auto()
    PARTIALLY_REFUNDED = auto()


class RefundStatus(StrEnumWithChoices):
    STARTED = auto()
    DONE = auto()
    FAILED = auto()


class PaymentsListParams(BaseModel):
    start: date
    end: date
    payment_system_id: list[int] = [127]
    status: list[PaymentStatus] = [*PaymentStatus]
    from_: int | None = Field(default=None, alias="from")
    limit: int = 10


class PaymentsSearchParams(BaseModel):
    query: str
    beg_date: date = Field(default_factory=lambda: get_today(offset=-31))
    end_date: date = Field(default_factory=lambda: get_today(offset=1))


class Payment(BaseModel):
    id: int
    pay_amount: float
    refund_amount: float | None = None
    clientid: str
    orderid: str | None
    payment_system_id: int
    unique_id: str | None = None
    status: PaymentStatus
    repeat_counter: int
    pending_datetime: datetime | None = None
    obtain_datetime: datetime | None = None
    success_datetime: datetime | None = None


class CallbackRequestStatus(StrEnum):
    SUCCESS = auto()
    FAIL = auto()  # differs from PaymentStatus.FAILED


class CallbackRequest(BaseModel):
    id: int
    sum: float
    clientid: str
    orderid: str  # e.g. 'web-c7dccae0-b696-4415-a437-44cff7786cbd'
    key: str | None = None  # md5-hash of concatenated previuos 4 params
    service_name: str | None = None
    client_email: EmailStr | None = None
    client_phone: str | None = None
    ps_id: int | None = None
    batch_date: date | None = None
    fop_receipt_key: str | None = None
    bank_id: str | None = None
    card_number: str | None = None
    card_holder: str | None = None
    card_expiry: str | None = None
    ok: str | None = None
    status: CallbackRequestStatus | None = CallbackRequestStatus.SUCCESS
    booking_id: UUID | None = None
    account: PayKeeperAccount | None = None

    @model_validator(mode="after")
    def validate_hash(cls, obj):
        _id, _sum, _clientid, _orderid, _key = map(lambda x: getattr(obj, x), (
            "id", "sum", "clientid", "orderid", "key"))
        _sum = "{0:.2f}".format(_sum)
        _secret_seed = settings.PAYKEEPER_CALLBACK_SECRET_SEED
        _control_string = "".join(map(str, (
            _id, _sum, _clientid, _orderid, _secret_seed)))
        _hash = md5_hash(_control_string)
        print(_key, _hash)
        if obj.status == CallbackRequestStatus.SUCCESS:
            assert _key == _hash, HttpError(400, "Invalid key!")
        obj.ok = md5_hash(str(_id) + _secret_seed)
        return obj

    @model_validator(mode="after")
    def extract_account(cls, obj):
        _orderid = obj.orderid
        obj.account = _orderid[:-37] or PayKeeperAccount.MOBILE
        obj.booking_id = _orderid[-36:]
        return obj


class RefundRequest(BaseModel):
    id: int
    amount: float
    partial: bool = False
    token: str | None = None


class Refund(BaseModel):
    id: int
    payment_id: int
    refund_number: int
    user: str
    amount: float
    remainder: float
    datetime: datetime
    status: RefundStatus
