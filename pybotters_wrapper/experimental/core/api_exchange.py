import asyncio
from typing import Callable, Awaitable

from aiohttp.client import ClientResponse
from requests import Response

from . import APIClient
from .._typedefs import TRequsetMethod


class ExchangeAPI:
    """取引所API実装用のベースクラス。APIClientの合成クラスで、request/srequestの
    ラッパーメソッドとresponseのdecodeメソッドを提供する。以下のようの実装になる。

    - ExchangeAPI: APIClientのラッパーメソッド＋httpリクエストの汎用helper関数を提供
        - FetchAPI: Fetchリクエストの汎用helper関数を提供
            - OrderFetchAPI: 注文Fetch用のinterface（例：引数の定義とエンドポイント取得・パラメーター変換・レスポンス解析のテンプレート）を提供
                - BinanceUSDSMFetchOrderAPI
                - bitflyerFetchOrderAPI
                - ...
            - PositionFetchAPI
                - ...
        - OrderAPI: 注文リクエストの汎用helper関数を提供
            - LimitOrderAPI: 指値注文用のinterfaceを提供
                - BinanceUSDSMLimitOrderAPI
                - bitflyerLimitOrderAPI
                - ...
            - MarketOrderAPI
                - ...

    """

    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        self._api_client = api_client
        self._method = method
        self._response_decoder = response_decoder

    async def request(
        self, url: str, params_or_data: dict = None, **kwargs
    ) -> ClientResponse:
        if self._method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return await self._api_client.request(self._method, url, **kwargs)

    def srequest(self, url: str, params_or_data: dict = None, **kwargs) -> Response:
        if self._method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return self._api_client.srequest(self._method, url, **kwargs)

    async def _decode_response(self, resp: ClientResponse) -> dict | list:
        if self._response_decoder is None:
            return await resp.json()
        else:
            if asyncio.iscoroutinefunction(self._response_decoder):
                return await self._response_decoder(resp)
            else:
                return self._response_decoder(resp)
