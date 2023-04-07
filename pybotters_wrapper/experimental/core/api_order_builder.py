from __future__ import annotations

from typing import Callable, Awaitable, Literal, Generic, TypeVar

from aiohttp import ClientResponse
from . import (
    OrderAPI,
    APIClient,
    LimitOrderAPI,
    MarketOrderAPI,
    CancelOrderAPI,
    StopMarketOrderAPI,
    StopLimitOrderAPI,
)
from .._typedefs import TRequsetMethod, TEndpoint, TSymbol, TOrderId


T = TypeVar("T", bound=OrderAPI)


class OrderAPIBuilder(Generic[T]):
    _ORDER_API_CLASSES = {
        "limit": LimitOrderAPI,
        "market": MarketOrderAPI,
        "stop_limit": StopLimitOrderAPI,
        "stop_market": StopMarketOrderAPI,
        "cancel": CancelOrderAPI,
    }

    def __init__(self):
        self._type: Literal[
            "limit", "market", "stop_limit", "stop_market", "cancel"
        ] | None = None
        self._api_client: APIClient | None = None
        self._method: TRequsetMethod | None = None
        self._order_id_key: str | None = None
        self._endpoint: TEndpoint | Callable[
            [TSymbol, TOrderId, dict], str
        ] | None = None
        self._parameter_translater: Callable[
            [TEndpoint, TSymbol, TOrderId, dict], dict
        ] | None = None
        self._response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ] | None = None
        self._order_id_extractor: Callable[
            [ClientResponse, dict, str], str | None
        ] | None = None

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

    def set_endpoint(self, endpoint: TEndpoint) -> OrderAPIBuilder:
        self._endpoint = endpoint
        return self

    def set_parameter_translater(
        self, parameter_translater: Callable[[TEndpoint, TSymbol, TOrderId, dict], dict]
    ) -> OrderAPIBuilder:
        self._parameter_translater = parameter_translater
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

    def get(self) -> T:
        self.validate()
        return self._ORDER_API_CLASSES[self._type](
            self._api_client,
            self._method,
            self._order_id_key,
            self._endpoint,
            self._parameter_translater,
            self._response_decoder,
        )

    def validate(self) -> None:
        required_fields = [
            "type",
            "api_client",
            "method",
            "order_id_key",
            "endpoint",
            "parameter_mapper",
        ]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
