from abc import ABCMeta, abstractmethod

import pybotters

from .api_wrapper import APIWrapper
from .api import (
    APIClient,
    APIClientBuilder,
    CancelOrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    TickerFetchAPI,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
)
from .exchange_property import ExchangeProperty
from .fetcher import PriceSizePrecisionFetcher
from .formatter import PriceSizePrecisionFormatter
from .store import NormalizedStoreBuilder, StoreInitializer
from .store_wrapper import DataStoreWrapper
from .typedefs import TDataStoreManager
from .websocket import WebSocketRequestBuilder, WebSocketRequestCustomizer


class WrapperFactory(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_store_initializer(cls, store: TDataStoreManager) -> StoreInitializer:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_normalized_store_builder(
        cls,
        store: TDataStoreManager | None = None,
    ) -> NormalizedStoreBuilder:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_websocket_request_builder(cls) -> WebSocketRequestBuilder:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_websocket_request_customizer(cls) -> WebSocketRequestCustomizer:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_price_size_precisions_fetcher(cls) -> PriceSizePrecisionFetcher:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_price_size_formatter(cls) -> PriceSizePrecisionFormatter:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_store(cls, store: TDataStoreManager | None = None) -> DataStoreWrapper:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_api(cls, client: pybotters.Client, verbose: bool = False) -> APIWrapper:
        raise NotImplementedError

    @classmethod
    def create_api_client(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> APIClient:
        return (
            APIClientBuilder()
            .set_client(client)
            .set_verbose(verbose)
            .set_exchange_property(cls.create_exchange_property())
            .get()
        )

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
    @abstractmethod
    def create_stop_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopLimitOrderAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_orders_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrdersFetchAPI:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_positions_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> PositionsFetchAPI:
        raise NotImplementedError
