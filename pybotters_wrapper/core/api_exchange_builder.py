from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Type, TypeVar, Generic, Callable, Awaitable

from aiohttp import ClientResponse

from . import APIClient
from .api_exchange import (
    TGenerateEndpointParameters,
    TTranslateParametersParameters,
    TWrapResponseParameters,
)
from _typedefs import TRequsetMethod, TEndpoint

TExchangeAPI = TypeVar("TExchangeAPI")


class ExchangeAPIBuilder(
    Generic[
        TExchangeAPI,
        TGenerateEndpointParameters,
        TTranslateParametersParameters,
        TWrapResponseParameters,
    ],
    metaclass=ABCMeta,
):
    ...

    def __init__(
        self,
        exchange_api_class: Type[TExchangeAPI],
        exchange_api_response_wrapper_class: Type[NamedTuple],
    ):
        self._exchange_api_class: Type[TExchangeAPI] = exchange_api_class
        self._response_wrapper_cls: Type[
            NamedTuple
        ] = exchange_api_response_wrapper_class

        self._api_client: APIClient | None = None
        self._method: TRequsetMethod | None = None
        self._endpoint_generator: TEndpoint | Callable[
            [TGenerateEndpointParameters], str
        ] | None = None
        self._parameter_translater: Callable[
            [TTranslateParametersParameters], dict
        ] | None = None
        self._response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ] | None = None

    def set_api_client(self, api_client: APIClient) -> ExchangeAPIBuilder:
        self._api_client = api_client
        return self

    def set_method(self, method: TRequsetMethod) -> ExchangeAPIBuilder:
        self._method = method
        return self

    def set_endpoint_generator(
        self, endpoint_generator: str | Callable[[TGenerateEndpointParameters], str]
    ) -> ExchangeAPIBuilder:
        self._endpoint_generator = endpoint_generator
        return self

    def set_parameter_translater(
        self, parameter_translater: Callable[[TTranslateParametersParameters], dict]
    ) -> ExchangeAPIBuilder:
        self._parameter_translater = parameter_translater
        return self

    def set_response_wrapper_cls(
        self, response_wrapper_cls: Type[NamedTuple]
    ) -> ExchangeAPIBuilder:
        self._response_wrapper_cls = response_wrapper_cls
        return self

    def set_response_decoder(
        self,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ],
    ) -> ExchangeAPIBuilder:
        self._response_decoder = response_decoder
        return self

    @abstractmethod
    def get(self) -> TExchangeAPI:
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> None:
        raise NotImplementedError
