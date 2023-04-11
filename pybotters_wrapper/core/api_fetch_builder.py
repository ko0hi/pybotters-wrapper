from __future__ import annotations

from typing import NamedTuple, Type

from . import FetchAPI
from .api_exchange_builder import ExchangeAPIBuilder


class FetchAPIBuilder(ExchangeAPIBuilder):
    def __init__(
        self,
        fetch_api_class: Type[FetchAPI],
        fetch_api_response_wrapper_class: Type[NamedTuple],
    ):
        super(FetchAPIBuilder, self).__init__(
            fetch_api_class, fetch_api_response_wrapper_class
        )

    def get(self) -> FetchAPI:
        self.validate()
        return self._exchange_api_class(
            api_client=self._api_client,
            method=self._method,
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
        ]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
