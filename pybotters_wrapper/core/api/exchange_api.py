import asyncio
from abc import ABCMeta
from typing import Any, Awaitable, Callable, Generic, Type, TypeVar

from aiohttp.client import ClientResponse
from requests import Response

from ..typedefs.typing import TEndpoint, TRequestMethod
from .client import APIClient

TGenerateEndpointParameters = TypeVar("TGenerateEndpointParameters")
TTranslateParametersParameters = TypeVar("TTranslateParametersParameters")
TWrapResponseParameters = TypeVar("TWrapResponseParameters")
TResponseWrapper = TypeVar("TResponseWrapper")


class ExchangeAPI(
    Generic[
        TResponseWrapper,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ],
    metaclass=ABCMeta,
):
    """取引所API実装用のベースクラス。APIClientの合成クラスで、request/srequestの
    ラッパーメソッドとresponseのdecodeメソッドを提供する。以下のようの実装になる。

    - ExchangeAPI: APIClientのラッパーメソッド＋httpリクエストの汎用helper関数を提供
        - FetchAPI: Fetchリクエストの汎用helper関数を提供
            - OrderFetchAPI: 注文Fetch用のinterface
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
        method: TRequestMethod,
        *,
        endpoint_generator: TEndpoint
        | Callable[[TGenerateEndpointParameters], str]
        | None = None,
        parameter_translater: Callable[[TTranslateParametersParameters], dict]
        | None = None,
        response_wrapper_cls: Type[TResponseWrapper] | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        self._api_client = api_client
        self._method = method
        self._endpoint_generator = endpoint_generator
        self._parameter_translater = parameter_translater
        self._response_wrapper_cls = response_wrapper_cls
        self._response_decoder = response_decoder

    async def request(
        self, url: str, params_or_data: dict | None = None, **kwargs: Any
    ) -> ClientResponse:
        return await self._api_client.request(
            self._method, url, params_or_data=params_or_data, **kwargs
        )

    def srequest(
        self, url: str, params_or_data: dict | None = None, **kwargs: Any
    ) -> Response:
        if self._method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return self._api_client.srequest(self._method, url, **kwargs)

    def _generate_endpoint(self, params: TGenerateEndpointParameters) -> TEndpoint:
        assert self._endpoint_generator is not None
        if isinstance(self._endpoint_generator, str):
            return self._endpoint_generator
        elif callable(self._endpoint_generator):
            return self._endpoint_generator(params)
        else:
            raise TypeError(f"Unsupported: {self._endpoint_generator}")

    def _translate_parameters(self, params: TTranslateParametersParameters) -> dict:
        assert self._parameter_translater is not None
        return self._parameter_translater(params)

    def _wrap_response(self, params: TWrapResponseParameters) -> TResponseWrapper:
        if self._response_wrapper_cls is None:
            raise ValueError("response_wrapper_cls is not set")
        return self._response_wrapper_cls(**params)

    async def _decode_response(self, resp: ClientResponse) -> dict:
        if self._response_decoder is None:
            return await resp.json()
        else:
            if asyncio.iscoroutinefunction(self._response_decoder):
                return await self._response_decoder(resp)
            else:
                return self._response_decoder(resp)  # type: ignore
