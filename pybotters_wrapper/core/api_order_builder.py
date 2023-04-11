from __future__ import annotations

from typing import Callable, NamedTuple, Type

from aiohttp import ClientResponse

from . import (
    OrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    CancelOrderAPI,
    StopMarketOrderAPI,
    StopLimitOrderAPI,
    PriceSizeFormatter,
)
from .api_exchange_builder import ExchangeAPIBuilder


class OrderAPIBuilder(ExchangeAPIBuilder):
    _ORDER_API_CLASSES = {
        "limit": LimitOrderAPI,
        "market": MarketOrderAPI,
        "stop_limit": StopLimitOrderAPI,
        "stop_market": StopMarketOrderAPI,
        "cancel": CancelOrderAPI,
    }

    def __init__(
        self,
        order_api_class: Type[OrderAPI],
        order_api_response_wrapper_class: Type[NamedTuple],
    ):
        super(OrderAPIBuilder, self).__init__(
            order_api_class,
            order_api_response_wrapper_class,
        )

        self._order_id_key: str | None = None
        self._order_id_extractor: Callable[
            [ClientResponse, dict, str], str | None
        ] | None = None
        self._price_size_formatter: PriceSizeFormatter | None = None
        self._price_format_keys: list[str] | None = None
        self._size_format_keys: list[str] | None = None

    def set_order_id_key(self, order_id_key: str) -> OrderAPIBuilder:
        self._order_id_key = order_id_key
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

    def get(self) -> OrderAPI:
        self.validate()
        return self._exchange_api_class(
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
