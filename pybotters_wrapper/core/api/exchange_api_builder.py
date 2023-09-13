from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Awaitable, Callable, Generic, NamedTuple, Type, TypeVar

from aiohttp import ClientResponse

from ..typedefs import TEndpoint, TRequestMethod
from .client import APIClient
from .exchange_api import (
    ExchangeAPI,
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)

TExchangeAPI = TypeVar("TExchangeAPI", bound=ExchangeAPI)
TExchangeAPIBuilder = TypeVar("TExchangeAPIBuilder", bound="ExchangeAPIBuilder")


class ExchangeAPIBuilder(
    Generic[
        TExchangeAPI,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ],
    metaclass=ABCMeta,
):
    def __init__(
        self,
        exchange_api_class: Type[TExchangeAPI],
        exchange_api_response_wrapper_class: Type[NamedTuple],
    ):
        self._exchange_api_class = exchange_api_class
        self._response_wrapper_cls = exchange_api_response_wrapper_class

        self._api_client: APIClient | None = None
        self._method: TRequestMethod | None = None
        self._endpoint_generator: TEndpoint | Callable[
            [TGenerateEndpointParameters], str
        ] | None = None
        self._parameter_translater: Callable[
            [TTranslateParametersParameters], dict
        ] | None = None
        self._response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ] | None = None

    def set_api_client(
        self: TExchangeAPIBuilder, api_client: APIClient
    ) -> TExchangeAPIBuilder:
        self._api_client = api_client
        return self

    def set_method(
        self: TExchangeAPIBuilder, method: TRequestMethod
    ) -> TExchangeAPIBuilder:
        self._method = method
        return self

    def set_endpoint_generator(
        self: TExchangeAPIBuilder,
        endpoint_generator: str | Callable[[TGenerateEndpointParameters], str],
    ) -> TExchangeAPIBuilder:
        self._endpoint_generator = endpoint_generator
        return self

    def set_parameter_translater(
        self: TExchangeAPIBuilder,
        parameter_translater: Callable[[TTranslateParametersParameters], dict],
    ) -> TExchangeAPIBuilder:
        self._parameter_translater = parameter_translater
        return self

    def set_response_wrapper_cls(
        self: TExchangeAPIBuilder, response_wrapper_cls: Type[NamedTuple]
    ) -> TExchangeAPIBuilder:
        self._response_wrapper_cls = response_wrapper_cls
        return self

    def set_response_decoder(
        self: TExchangeAPIBuilder,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ],
    ) -> TExchangeAPIBuilder:
        self._response_decoder = response_decoder
        return self

    @abstractmethod
    def get(self) -> TExchangeAPI:
        raise NotImplementedError

    def validate(self) -> None:
        raise NotImplementedError

    def _null_check(self, *non_null_fields: str) -> None:
        missing_fields = [
            field for field in non_null_fields if getattr(self, f"{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
