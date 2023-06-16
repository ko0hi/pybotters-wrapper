from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NamedTuple, Type, TypeVar

from aiohttp import ClientResponse

from .order_api import OrderAPI
from ..exchange_api import (
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from ..exchange_api_builder import ExchangeAPIBuilder

if TYPE_CHECKING:
    from pybotters_wrapper.core.formatter.price_size_precision import (
        PriceSizePrecisionFormatter,
    )

    from .order_api import OrderAPI

TOrderAPI = TypeVar("TOrderAPI", bound=OrderAPI)
TOrderAPIBuilder = TypeVar(
    "TOrderAPIBuilder",
    bound="OrderAPIBuilder",
)


class OrderAPIBuilder(
    ExchangeAPIBuilder[
        TOrderAPI,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ]
):
    def __init__(
        self,
        order_api_class: Type[TOrderAPI],
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
        self._price_size_formatter: PriceSizePrecisionFormatter | None = None
        self._price_format_keys: tuple[str, ...] | None = None
        self._size_format_keys: tuple[str, ...] | None = None

    def set_order_id_key(self: TOrderAPIBuilder, order_id_key: str) -> TOrderAPIBuilder:
        self._order_id_key = order_id_key
        return self

    def set_order_id_extractor(
        self: TOrderAPIBuilder,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None],
    ) -> TOrderAPIBuilder:
        self._order_id_extractor = order_id_extractor
        return self

    def set_price_size_formatter(
        self: TOrderAPIBuilder,
        price_size_formatter: PriceSizePrecisionFormatter,
    ) -> TOrderAPIBuilder:
        self._price_size_formatter = price_size_formatter
        return self

    def set_price_format_keys(
        self: TOrderAPIBuilder, *price_format_keys: str
    ) -> TOrderAPIBuilder:
        self._price_format_keys = price_format_keys
        return self

    def set_size_format_keys(
        self: TOrderAPIBuilder, *size_format_keys: str
    ) -> TOrderAPIBuilder:
        self._size_format_keys = size_format_keys
        return self

    def get(self) -> TOrderAPI:
        self._null_check(
            "_api_client",
            "_method",
            "_order_id_key",
            "_endpoint_generator",
            "_parameter_translater",
            "_response_wrapper_cls",
        )
        return self._exchange_api_class(
            api_client=self._api_client,
            method=self._method,
            order_id_key=self._order_id_key,
            order_id_extractor=self._order_id_extractor,
            endpoint_generator=self._endpoint_generator,
            parameter_translater=self._parameter_translater,
            response_wrapper_cls=self._response_wrapper_cls,
            response_decoder=self._response_decoder,
            price_size_formatter=self._price_size_formatter,
            price_format_keys=self._price_format_keys,
            size_format_keys=self._size_format_keys,
        )
