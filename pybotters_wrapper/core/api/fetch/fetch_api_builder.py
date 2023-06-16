from __future__ import annotations

from typing import Any, Callable, NamedTuple, Type, TypeVar

from aiohttp import ClientResponse

from .fetch_api import FetchAPI
from ..exchange_api import (
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from ..exchange_api_builder import ExchangeAPIBuilder

TFetchAPI = TypeVar("TFetchAPI", bound=FetchAPI)
TFetchAPIBuilder = TypeVar("TFetchAPIBuilder", bound="FetchAPIBuilder")


class FetchAPIBuilder(
    ExchangeAPIBuilder[
        TFetchAPI,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ]
):
    def __init__(
        self,
        fetch_api_class: Type[TFetchAPI],
        fetch_api_response_wrapper_class: Type[NamedTuple],
    ):
        super(FetchAPIBuilder, self).__init__(
            fetch_api_class, fetch_api_response_wrapper_class
        )
        self._response_itemizer: Callable[[ClientResponse, Any], Any] | None = None

    def set_response_itemizer(
        self: TFetchAPIBuilder,
        response_itemizer: Callable[[ClientResponse, Any], Any],
    ) -> TFetchAPIBuilder:
        self._response_itemizer = response_itemizer
        return self

    def get(self) -> TFetchAPI:
        self._null_check(
            "_api_client",
            "_method",
            "_response_itemizer",
            "_endpoint_generator",
            "_parameter_translater",
            "_response_wrapper_cls",
        )
        return self._exchange_api_class(
            api_client=self._api_client,
            method=self._method,
            response_itemizer=self._response_itemizer,
            endpoint_generator=self._endpoint_generator,
            parameter_translater=self._parameter_translater,
            response_wrapper_cls=self._response_wrapper_cls,
            response_decoder=self._response_decoder,
        )
