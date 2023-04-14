from __future__ import annotations

from typing import NamedTuple, Optional

import aiohttp
import pybotters
import requests
from aiohttp.client import ClientResponse
from requests import Response

from .._typedefs import TRequestMethod, TSide
from .exchange_property import ExchangeProperty
from .normalized_store_order import OrderItem
from .normalized_store_orderbook import OrderbookItem
from .normalized_store_position import PositionItem
from .normalized_store_ticker import TickerItem


class OrderResponse(NamedTuple):
    order_id: str
    resp: aiohttp.ClientResponse
    resp_data: dict | None = None

    @property
    def status(self):
        return self.resp.status

    def is_success(self):
        return self.resp.status == 200


class FetchTickerResponse(NamedTuple):
    ticker: TickerItem
    resp: aiohttp.ClientResponse
    resp_data: Optional[any] = None


class FetchOrderbookResponse(NamedTuple):
    orderbook: dict[TSide, list[OrderbookItem]]
    resp: aiohttp.ClientResponse
    resp_data: Optional[any] = None


class FetchOrdersResponse(NamedTuple):
    orders: list[OrderItem]
    resp: aiohttp.ClientResponse
    resp_data: Optional[any] = None


class FetchPositionsResponse(NamedTuple):
    positions: list[PositionItem]
    resp: aiohttp.ClientResponse
    resp_data: Optional[any] = None


class APIClient:
    def __init__(
        self,
        client: pybotters.Client,
        verbose: bool = False,
        *,
        exchange_property: ExchangeProperty,
    ):
        self._client = client
        self._verbose = verbose
        self._eprop = exchange_property
        self._validate()

    async def request(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> ClientResponse:
        url = self._attach_base_url(url)
        if method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return await self._client.request(method, url, **kwargs)

    async def get(
        self, url: str, *, params: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("GET", url, params_or_data=params, **kwargs)

    async def post(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("POST", url, params_or_data=data, **kwargs)

    async def put(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("PUT", url, params_or_data=data, **kwargs)

    async def delete(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("DELETE", url, params_or_data=data, **kwargs)

    def srequest(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> Response:
        # TODO: 網羅的なテスト
        # aiohttp.ClientSession._requestをpybotters.Clientから呼び出した時の処理を抜き出している
        sess: aiohttp.ClientSession = self._client._session

        if method == "GET":
            params = params_or_data
            data = None
        else:
            params = None
            data = params_or_data

        req = sess._request_class(
            method,
            sess._build_url(self._attach_base_url(url)),
            params=params,
            data=data,
            headers=sess._prepare_headers([]),
            session=sess,
            auth=pybotters.auth.Auth,
        )
        headers = {str(k): str(v) for (k, v) in dict(req.headers).items()}
        if isinstance(req.body, aiohttp.payload.BytesPayload):
            data = req.body._value
        else:
            data = req.body
        # paramsはurlに埋め込まれている
        return requests.request(
            method=req.method, url=str(req.url), data=data, headers=headers, **kwargs
        )

    def sget(self, url: str, *, params: dict | None = None, **kwargs) -> Response:
        return self.srequest("GET", url, params_or_data=params, **kwargs)

    def spost(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("POST", url, params_or_data=data, **kwargs)

    def sput(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("PUT", url, params_or_data=data, **kwargs)

    def sdelete(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("DELETE", url, params_or_data=data, **kwargs)

    def _attach_base_url(self, url: str) -> str:
        return self._eprop.base_url + url

    def _validate(self):
        if self._client._base_url != "":
            raise ValueError("Client should not have base_url")
