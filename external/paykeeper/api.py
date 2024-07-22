import aiohttp
from django.conf import settings
from functools import wraps
import json
from uuid import UUID

from contrib.common.cached import acached
from contrib.common.pydantic import json_clean, construct_params
from contrib.utils.async_api_client import AsyncClient, apply_api_client
from contrib.utils.decorators import default_on_error

from .schemas import (
    TokenInfo, InvoicePreviewRequest,
    PaymentsListParams, RefundRequest,
    PaymentsSearchParams,
    PayKeeperAccount,
)


class PayKeeper:
    def __init__(self, account: PayKeeperAccount):
        _suffix = account.upper()
        _api_url = getattr(settings, f"PAYKEEPER_API_URL_{_suffix}")
        _auth_header = getattr(settings, f"PAYKEEPER_BASIC_AUTH_HEADER_{_suffix}")
        self.client = AsyncClient(_api_url,
            default_headers={
                "Authorization": f"Basic {_auth_header}",
            })

    @acached(ttl=3600, with_args=False)
    @default_on_error(None)
    async def get_paykeeper_token(self):
        res = await self.get_token()
        return res["token"]

    async def get_token(self):
        return await self.client.request("/info/settings/token/")

    async def systems_list(self):
        res = await self.client.request("/info/systems/list/")
        return res

    @default_on_error([])
    async def payments_list(self, params: PaymentsListParams):
        _params = construct_params(params, replace={
            "payment_system_id": "payment_system_id[]",
            "status": "status[]"
        })
        return await self.client.request("/info/payments/bydate/", params=_params)

    @default_on_error([])
    async def payments_search(self, params: PaymentsSearchParams):
        _params = json_clean(params)
        return await self.client.request("/info/payments/search/", params=_params, log=True)

    async def payment_info(self, payment_id):
        _params = {"id": payment_id}
        return await self.client.request("/info/payments/byid/", params=_params, log=True)

    async def refund(self, data: RefundRequest):
        _data = json_clean(data)
        _data["partial"] = str(_data["partial"]).lower()
        return await self.post("/change/payment/reverse/", data=_data)

    @default_on_error([])
    async def payment_refunds(self, payment_id):
        _params = {"id": payment_id}
        return await self.client.request("/info/refunds/bypaymentid/", params=_params)

    async def post(self, *args, data=None, **kwargs):
        data["token"] = await self.get_paykeeper_token()
        return await self.client.request(*args, data=data, method="post", **kwargs)

    async def invoice_preview(self, data: InvoicePreviewRequest):
        _data = json_clean(data)
        return await self.post("/change/invoice/preview/", data=_data)

    async def reset_informer(self, payment_id: int):
        _data = {"id": payment_id}
        return await self.post("/change/payment/repeatcnt/", data=_data)


def paykeeper_client(func):
    @wraps(func)
    async def _(*args, **kwargs):
        print(func.__module__, *args, kwargs)
        _account: PayKeeperAccount = kwargs.pop("account", PayKeeperAccount.MOBILE)
        return await apply_api_client(PayKeeper, [_account], func, *args, **kwargs)
    return _
