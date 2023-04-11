from __future__ import annotations

from collections import namedtuple
from typing import Generic, TypeVar

from pybotters.store import DataStoreManager

from .exchange_property import ExchangeProperty
from .normalized_store_builder import NormalizedStoreBuilder
from .store_initializer import StoreInitializer
from .store_wrapper import DataStoreWrapper
from .websocket_request_builder import WebSocketRequestBuilder
from .websocket_resquest_customizer import (
    WebSocketRequestCustomizer,
    WebSocketDefaultRequestCustomizer,
)

T = TypeVar("T", bound=DataStoreManager)
InitializeRequestConfig = namedtuple(
    "InitializeRequestConf", ("method", "url", "params")
)


class DataStoreWrapperBuilder(Generic[T]):
    def __init__(self):
        self._store: T | None = None
        self._exchange_property: ExchangeProperty | None = None
        self._store_initializer: StoreInitializer | None = None
        self._normalized_store_builder: NormalizedStoreBuilder | None = None
        self._websocket_request_builder: WebSocketRequestBuilder | None = None
        self._websocket_request_customizer: WebSocketRequestCustomizer | None = (
            WebSocketDefaultRequestCustomizer()
        )

    def set_store(self, store: T) -> DataStoreWrapperBuilder:
        self._store = store
        return self

    def set_exchange_property(
        self, exchange_property: ExchangeProperty
    ) -> DataStoreWrapperBuilder:
        self._exchange_property = exchange_property
        return self

    def set_store_initializer(
        self, store_initializer: StoreInitializer
    ) -> DataStoreWrapperBuilder:
        self._store_initializer = store_initializer
        return self

    def set_normalized_store_builder(
        self, normalized_store_builder: NormalizedStoreBuilder
    ) -> DataStoreWrapperBuilder:
        self._normalized_store_builder = normalized_store_builder
        return self

    def set_websocket_request_builder(
        self, websocket_request_builder: WebSocketRequestBuilder
    ) -> DataStoreWrapperBuilder:
        self._websocket_request_builder = websocket_request_builder
        return self

    def set_websocket_request_customizer(
        self, websocket_request_customizer: WebSocketRequestCustomizer
    ) -> DataStoreWrapperBuilder:
        self._websocket_request_customizer = websocket_request_customizer
        return self

    def get(self) -> DataStoreWrapper:
        self.validate()
        return DataStoreWrapper(
            self._store,
            exchange_property=self._exchange_property,
            normalized_store_builder=self._normalized_store_builder,
            store_initializer=self._store_initializer,
            websocket_request_builder=self._websocket_request_builder,
            websocket_request_customizer=self._websocket_request_customizer,
        )

    def validate(self) -> None:
        required_fields = [
            "store",
            "exchange_property",
            "store_initializer",
            "normalized_store_builder",
            "websocket_request_builder",
        ]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
