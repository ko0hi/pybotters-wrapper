from abc import ABCMeta, abstractmethod
from typing import Callable, Literal, Type

import pybotters
from pybotters.store import DataStoreManager

from . import (
    APIWrapperBuilder,
    DataStoreWrapperBuilder,
    TSymbol,
    WebSocketChannels,
    WebSocketDefaultRequestCustomizer,
)
from .api import (
    APIClient,
    APIClientBuilder,
    CancelOrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    TickerFetchAPI,
)
from .api_wrapper import APIWrapper
from .exchange_property import ExchangeProperties, ExchangeProperty
from .fetcher import PriceSizePrecisionFetcher
from .formatter import PriceSizePrecisionFormatter
from .store import NormalizedStoreBuilder, StoreInitializer
from .store.store_initializer import TInitializerConfig
from .store_wrapper import DataStoreWrapper
from .typedefs import TDataStoreManager
from .websocket import WebSocketRequestBuilder, WebSocketRequestCustomizer


class WrapperFactory(metaclass=ABCMeta):
    _EXCHANGE_PROPERTIES: ExchangeProperties
    _DATASTORE_MANAGER: Type[DataStoreManager]
    _WEBSOCKET_CHANNELS: Type[WebSocketChannels]
    _NORMALIZED_STORE_BUILDER: Type[NormalizedStoreBuilder]

    _EXCHANGE_PROPERTY: Type[ExchangeProperty] = ExchangeProperty
    _STORE_INITIALIZER: Type[StoreInitializer] = StoreInitializer
    _INITIALIZER_CONFIG: TInitializerConfig | None = None
    _WEBSOCKET_REQUEST_BUILDER: Type[WebSocketRequestBuilder] = WebSocketRequestBuilder
    _WEBSOCKET_REQUEST_CUSTOMIZER: Type[
        WebSocketRequestCustomizer
    ] = WebSocketDefaultRequestCustomizer
    _PRICE_SIZE_PRECISION_FETCHER: Type[PriceSizePrecisionFetcher] | None = None

    @classmethod
    @abstractmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> MarketOrderAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        raise NotImplementedError

    @classmethod
    def create_stop_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopLimitOrderAPI | None:
        return None

    @classmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI | None:
        return None

    @classmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI | None:
        return None

    @classmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI | None:
        return None

    @classmethod
    def create_orders_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrdersFetchAPI | None:
        return None

    @classmethod
    def create_positions_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> PositionsFetchAPI | None:
        return None

    @classmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        return cls._EXCHANGE_PROPERTY(cls._EXCHANGE_PROPERTIES)

    @classmethod
    def create_store_initializer(cls, store: TDataStoreManager) -> StoreInitializer:
        return cls._STORE_INITIALIZER(store, cls._INITIALIZER_CONFIG)

    @classmethod
    def create_normalized_store_builder(
        cls, store: TDataStoreManager | None = None
    ) -> NormalizedStoreBuilder:
        assert cls._NORMALIZED_STORE_BUILDER is not None
        return cls._NORMALIZED_STORE_BUILDER(store or cls.create_datastore_manager())

    @classmethod
    def create_websocket_channels(cls) -> WebSocketChannels:
        assert cls._WEBSOCKET_CHANNELS is not None
        return cls._WEBSOCKET_CHANNELS()

    @classmethod
    def create_datastore_manager(cls) -> DataStoreManager:
        assert cls._DATASTORE_MANAGER is not None
        return cls._DATASTORE_MANAGER()

    @classmethod
    def create_store(cls, store: TDataStoreManager | None = None) -> DataStoreWrapper:
        store = store or cls.create_datastore_manager()
        return (
            DataStoreWrapperBuilder()
            .set_store(store)
            .set_exchange_property(cls.create_exchange_property())
            .set_store_initializer(cls.create_store_initializer(store))
            .set_normalized_store_builder(cls.create_normalized_store_builder(store))
            .set_websocket_request_builder(cls.create_websocket_request_builder())
            .set_websocket_request_customizer(cls.create_websocket_request_customizer())
            .get()
        )

    @classmethod
    def create_websocket_request_builder(cls) -> WebSocketRequestBuilder:
        assert cls._WEBSOCKET_REQUEST_BUILDER is not None
        return cls._WEBSOCKET_REQUEST_BUILDER(cls.create_websocket_channels())

    @classmethod
    def create_websocket_request_customizer(
        cls, client: pybotters.Client | None = None
    ) -> WebSocketRequestCustomizer:
        assert cls._WEBSOCKET_REQUEST_CUSTOMIZER is not None
        return cls._WEBSOCKET_REQUEST_CUSTOMIZER(client)

    @classmethod
    def create_price_size_precisions_fetcher(cls) -> PriceSizePrecisionFetcher:
        if cls._PRICE_SIZE_PRECISION_FETCHER is None:

            class DummyPriceSizePrecisionFetcher(PriceSizePrecisionFetcher):
                """No format"""

                def fetch_precisions(
                    self,
                ) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
                    return {"price": {}, "size": {}}

            return DummyPriceSizePrecisionFetcher()
        else:
            return cls._PRICE_SIZE_PRECISION_FETCHER()

    @classmethod
    def create_price_size_formatter(cls) -> PriceSizePrecisionFormatter:
        precisions = cls.create_price_size_precisions_fetcher().fetch_precisions()
        return PriceSizePrecisionFormatter(precisions["price"], precisions["size"])

    @classmethod
    def create_api_client(
        cls,
        client: pybotters.Client,
        verbose: bool = False,
        *,
        base_url_attacher: Callable[[str], str] | None = None
    ) -> APIClient:
        return (
            APIClientBuilder()
            .set_client(client)
            .set_verbose(verbose)
            .set_exchange_property(cls.create_exchange_property())
            .get()
        )

    @classmethod
    def create_api(cls, client: pybotters.Client, verbose: bool = False) -> APIWrapper:
        builder = (
            APIWrapperBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_limit_order_api(cls.create_limit_order_api(client, verbose))
            .set_market_order_api(cls.create_market_order_api(client, verbose))
            .set_cancel_order_api(cls.create_cancel_order_api(client, verbose))
        )

        stop_limit_order_api = cls.create_stop_limit_order_api(client, verbose)
        if stop_limit_order_api:
            builder.set_stop_limit_order_api(stop_limit_order_api)

        stop_market_order_api = cls.create_stop_market_order_api(client, verbose)
        if stop_market_order_api:
            builder.set_stop_market_order_api(stop_market_order_api)

        ticker_fetch_api = cls.create_ticker_fetch_api(client, verbose)
        if ticker_fetch_api:
            builder.set_ticker_fetch_api(ticker_fetch_api)

        orderbook_fetch_api = cls.create_orderbook_fetch_api(client, verbose)
        if orderbook_fetch_api:
            builder.set_orderbook_fetch_api(orderbook_fetch_api)

        orders_fetch_api = cls.create_orders_fetch_api(client, verbose)
        if orders_fetch_api:
            builder.set_orders_fetch_api(orders_fetch_api)

        positions_fetch_api = cls.create_positions_fetch_api(client, verbose)
        if positions_fetch_api:
            builder.set_positions_fetch_api(positions_fetch_api)

        return builder.get()
