from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ExchangeProperty

import pybotters

from .api_client import APIClient


class APIClientBuilder:
    def __init__(self):
        self._client: pybotters.Client | None = None
        self._exchange_property: ExchangeProperty | None = None
        self._verbose: bool | None = False

    def set_client(self, client: pybotters.Client) -> APIClientBuilder:
        self._client = client
        return self

    def set_exchange_property(
        self, exchange_property: ExchangeProperty
    ) -> APIClientBuilder:
        self._exchange_property = exchange_property
        return self

    def set_verbose(self, verbose: bool = True) -> APIClientBuilder:
        self._verbose = verbose
        return self

    def get(self) -> APIClient:
        self.validate()
        return APIClient(
            self._client, self._verbose, exchange_property=self._exchange_property
        )

    def validate(self) -> None:
        required_fields = ["client", "exchange_property"]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
