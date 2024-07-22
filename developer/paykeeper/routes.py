from uuid import UUID

from ninja import Router, Form

from external.paykeeper.schemas import (
    TokenInfo, ResultResponse, ErrorResponse,
    InvoicePreviewRequest, InvoicePreviewResponse,
    PaymentsListParams, Payment,
    CallbackRequest,
    RefundRequest, Refund,
)
import external.paykeeper.services as services

router = Router(tags=["PayKeeper"])


@router.post("/systems-list")
async def systems_list(request):
    return await services.systems_list()


@router.post("/payments-list", response=list[Payment])
async def payments_list(request,
    params: PaymentsListParams,
):
    return await services.payments_list(params)


@router.post("/payments-search", response=list[Payment])
async def payments_search(request,
    booking_id: UUID,
):
    return await services.payments_search(booking_id)


@router.post("/payment-info", response=Payment)
async def payment_info(request,
    payment_id: int,
):
    return await services.payment_info(payment_id)


@router.post("/refund", response=ErrorResponse | ResultResponse)
async def refund(request,
    data: RefundRequest,
):
    return await services.refund(data)


@router.post("/refund/{payment_id}", response=list[Refund])
async def payment_refunds(request,
    payment_id: int,
):
    return await services.payment_refunds(payment_id)


@router.post("/token", response=TokenInfo)
async def token(request):
    return await services.token()


@router.post("/invoice-preview", response=InvoicePreviewResponse | ErrorResponse)
async def invoice_preview(request,
    data: InvoicePreviewRequest,
):
    return await services.invoice_preview(data)


@router.post("/callback", auth=None, response=str)
async def callback(request,
    data: Form[CallbackRequest],
):
    await services.callback(data)
    return f"OK {data.ok}"


@router.post("/reset-informer/{payment_id}")
async def reset_informer(request,
    payment_id: int,
):
    return await services.reset_informer(payment_id)
