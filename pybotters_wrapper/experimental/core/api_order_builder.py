from __future__ import annotations

from typing import Callable, Awaitable, Literal, Generic, TypeVar, NamedTuple, Type

from aiohttp import ClientResponse
from . import (
    OrderAPI,
    APIClient,
    LimitOrderAPI,
    MarketOrderAPI,
    CancelOrderAPI,
    StopMarketOrderAPI,
    StopLimitOrderAPI,
    PriceSizeFormatter,
)
from .api_order import (
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from .._typedefs import TRequsetMethod, TEndpoint, TSymbol, TOrderId


T = TypeVar("T", bound=OrderAPI)


class OrderAPIBuilder(
    Generic[
        T,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ]
):
    _ORDER_API_CLASSES = {
        "limit": LimitOrderAPI,
        "market": MarketOrderAPI,
        "stop_limit": StopLimitOrderAPI,
        "stop_market": StopMarketOrderAPI,
        "cancel": CancelOrderAPI,
    }

    def __init__(
        self,
        order_api_class: Type[T],
        order_api_response_wrapper_class: Type[NamedTuple],
    ):
        self._order_api_class: Type[T] = order_api_class
        self._response_wrapper_cls: Type[NamedTuple] = order_api_response_wrapper_class

        self._api_client: APIClient | None = None
        self._method: TRequsetMethod | None = None
        self._order_id_key: str | None = None
        self._order_id_extractor: Callable[
            [ClientResponse, dict, str], str | None
        ] | None = None
        self._endpoint_generator: TEndpoint | Callable[
            [TGenerateEndpointParameters], str
        ] | None = None
        self._parameter_translater: Callable[
            [TTranslateParametersParameters], dict
        ] | None = None
        self._response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ] | None = None
        self._price_size_formatter: PriceSizeFormatter | None = None
        self._price_format_keys: list[str] | None = None
        self._size_format_keys: list[str] | None = None

    def set_type(
        self, type: Literal["limit", "market", "stop_limit", "stop_market", "cancel"]
    ) -> OrderAPIBuilder:
        self._type = type
        return self

    def set_api_client(self, api_client: APIClient) -> OrderAPIBuilder:
        self._api_client = api_client
        return self

    def set_method(self, method: TRequsetMethod) -> OrderAPIBuilder:
        self._method = method
        return self

    def set_order_id_key(self, order_id_key: str) -> OrderAPIBuilder:
        self._order_id_key = order_id_key
        return self

    def set_endpoint_generator(self, endpoint_generator: TEndpoint) -> OrderAPIBuilder:
        self._endpoint_generator = endpoint_generator
        return self

    def set_parameter_translater(
        self, parameter_translater: Callable[[TEndpoint, TSymbol, TOrderId, dict], dict]
    ) -> OrderAPIBuilder:
        self._parameter_translater = parameter_translater
        return self

    def set_response_wrapper_cls(
        self, response_wrapper_cls: Type[NamedTuple]
    ) -> OrderAPIBuilder:
        self._response_wrapper_cls = response_wrapper_cls
        return self

    def set_response_decoder(
        self,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ],
    ) -> OrderAPIBuilder:
        self._response_decoder = response_decoder
        return self

    def set_order_id_extractor(
        self,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None],
    ) -> OrderAPIBuilder:
        self._order_id_extractor = order_id_extractor
        return self

    def set_price_size_formatter(
        self,
        price_size_formatter: PriceSizeFormatter,
    ) -> OrderAPIBuilder:
        self._price_size_formatter = price_size_formatter
        return self

    def set_price_format_keys(self, *price_format_keys: str) -> OrderAPIBuilder:
        self._price_format_keys = price_format_keys
        return self

    def set_size_format_keys(self, *size_format_keys: str) -> OrderAPIBuilder:
        self._size_format_keys = size_format_keys
        return self

    def get(self) -> T:
        self.validate()
        return self._order_api_class(
            api_client=self._api_client,
            method=self._method,
            order_id_key=self._order_id_key,
            order_id_extractor=self._order_id_extractor,
            endpoint_generator=self._endpoint_generator,
            response_wrapper_cls=self._response_wrapper_cls,
            response_decoder=self._response_decoder,
            price_size_formatter=self._price_size_formatter,
            price_format_keys=self._price_format_keys,
            size_format_keys=self._size_format_keys,
        )

    def validate(self) -> None:
        required_fields = [
            "api_client",
            "method",
            "order_id_key",
            "endpoint_generator",
            "parameter_translater",
            "response_wrapper_cls",
        ]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
