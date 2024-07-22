from ninja.errors import HttpError

from .api import PayKeeper, paykeeper_client
from .schemas import (
    TokenInfo, InvoicePreviewRequest,
    InvoicePreviewResponse, ErrorResponse,
    PaymentsListParams, PaymentsSearchParams,
    CallbackRequest, RefundRequest,
    PayKeeperAccount,
)


@paykeeper_client
async def systems_list(
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    res = await client.systems_list()
    return res
    

@paykeeper_client
async def payments_list(
    params: PaymentsListParams,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    return await client.payments_list(params)


@paykeeper_client
async def payments_search(
    params: PaymentsSearchParams,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    return await client.payments_search(params)


@paykeeper_client
async def payment_info(
    payment_id: int,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    try:
        res = await client.payment_info(payment_id)
        return res[0]
    except:
        raise HttpError(404, "Not found")


@paykeeper_client
async def refund(
    data: RefundRequest,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    return await client.refund(data)


@paykeeper_client
async def payment_refunds(
    payment_id: int,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    return await client.payment_refunds(payment_id)


@paykeeper_client
async def token(
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
) -> TokenInfo:
    return await client.get_token()


@paykeeper_client
async def invoice_preview(
    data: InvoicePreviewRequest,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
) -> InvoicePreviewResponse | ErrorResponse:
    return await client.invoice_preview(data)


async def callback(
    data: CallbackRequest,
):
    print(data)


@paykeeper_client
async def reset_informer(
    payment_id: int,
    account: PayKeeperAccount = None,
    client: PayKeeper = None,
):
    return await client.reset_informer(payment_id)
