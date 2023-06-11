from __future__ import annotations

from typing import TypeVar

from .exchange_property import ExchangeProperty
from .store import StoreInitializer, NormalizedStoreBuilder
from .store_wrapper import DataStoreWrapper
from .typedefs import TDataStoreManager
from .websocket import (
    WebSocketDefaultRequestCustomizer,
    WebSocketRequestBuilder,
    WebSocketRequestCustomizer,
)

TDataStoreWrapperBuilder = TypeVar(
    "TDataStoreWrapperBuilder", bound="DataStoreWrapperBuilder"
)


class DataStoreWrapperBuilder:
    def __init__(self):
        self._store = None
        self._exchange_property = None
        self._store_initializer = None
        self._normalized_store_builder = None
        self._websocket_request_builder = None
        self._websocket_request_customizer = WebSocketDefaultRequestCustomizer()

    def set_store(
        self: TDataStoreWrapperBuilder, store: TDataStoreManager
    ) -> TDataStoreWrapperBuilder:
        self._store = store
        return self

    def set_exchange_property(
        self: TDataStoreWrapperBuilder, exchange_property: ExchangeProperty
    ) -> TDataStoreWrapperBuilder:
        self._exchange_property = exchange_property
        return self

    def set_store_initializer(
        self: TDataStoreWrapperBuilder, store_initializer: StoreInitializer
    ) -> TDataStoreWrapperBuilder:
        self._store_initializer = store_initializer
        return self

    def set_normalized_store_builder(
        self: TDataStoreWrapperBuilder, normalized_store_builder: NormalizedStoreBuilder
    ) -> TDataStoreWrapperBuilder:
        self._normalized_store_builder = normalized_store_builder
        return self

    def set_websocket_request_builder(
        self: TDataStoreWrapperBuilder,
        websocket_request_builder: WebSocketRequestBuilder,
    ) -> TDataStoreWrapperBuilder:
        self._websocket_request_builder = websocket_request_builder
        return self

    def set_websocket_request_customizer(
        self: TDataStoreWrapperBuilder,
        websocket_request_customizer: WebSocketRequestCustomizer,
    ) -> TDataStoreWrapperBuilder:
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
