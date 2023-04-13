from __future__ import annotations

from typing import Any, Callable, NamedTuple, Type

from aiohttp import ClientResponse

from .api_exchange import (
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from .api_exchange_builder import ExchangeAPIBuilder, TExchangeAPI
from .api_fetch import FetchAPI


class FetchAPIBuilder(
    ExchangeAPIBuilder[
        TExchangeAPI,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ]
):
    def __init__(
        self,
        fetch_api_class: Type[FetchAPI],
        fetch_api_response_wrapper_class: Type[NamedTuple],
    ):
        super(FetchAPIBuilder, self).__init__(
            fetch_api_class, fetch_api_response_wrapper_class
        )
        self._response_itemizer: Callable[[ClientResponse, any], Any] | None = None

    def set_response_itemizer(
        self,
        response_itemizer: Callable[[ClientResponse, any], Any],
    ) -> FetchAPIBuilder:
        self._response_itemizer = response_itemizer
        return self

    def get(self) -> TExchangeAPI:
        self.validate()
        return self._exchange_api_class(
            api_client=self._api_client,
            method=self._method,
            response_itemizer=self._response_itemizer,
            endpoint_generator=self._endpoint_generator,
            parameter_translater=self._parameter_translater,
            response_wrapper_cls=self._response_wrapper_cls,
            response_decoder=self._response_decoder,
        )

    def validate(self) -> None:
        required_fields = [
            "api_client",
            "method",
            "endpoint_generator",
            "parameter_translater",
            "response_wrapper_cls",
            "response_itemizer",
        ]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
