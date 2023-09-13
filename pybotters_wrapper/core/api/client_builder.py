from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from ..exchange_property import ExchangeProperty

import pybotters

from .client import APIClient

TAPIClientBuilder = TypeVar("TAPIClientBuilder", bound="APIClientBuilder")


class APIClientBuilder:
    def __init__(self):
        self._client: pybotters.Client | None = None
        self._exchange_property: ExchangeProperty | None = None
        self._base_url_attacher: Callable[[str], str] | None = None
        self._verbose: bool = False

    def set_client(
        self: TAPIClientBuilder, client: pybotters.Client
    ) -> TAPIClientBuilder:
        self._client = client
        return self

    def set_exchange_property(
        self: TAPIClientBuilder, exchange_property: ExchangeProperty
    ) -> TAPIClientBuilder:
        self._exchange_property = exchange_property
        return self

    def set_verbose(self: TAPIClientBuilder, verbose: bool = True) -> TAPIClientBuilder:
        self._verbose = verbose
        return self

    def set_base_url_attacher(
        self: TAPIClientBuilder, base_url_attacher: Callable[[str], str]
    ) -> TAPIClientBuilder:
        self._base_url_attacher = base_url_attacher
        return self

    def get(self) -> APIClient:
        assert self._client is not None
        assert self._exchange_property is not None
        return APIClient(
            self._client,
            self._verbose,
            exchange_property=self._exchange_property,
            base_url_attacher=self._base_url_attacher,
        )
