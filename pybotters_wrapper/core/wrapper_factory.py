from abc import ABCMeta, abstractmethod

import pybotters

from .api_client import APIClient
from .api_fetch_orderbook import OrderbookFetchAPI
from .api_fetch_orders import OrdersFetchAPI
from .api_fetch_positions import PositionsFetchAPI
from .api_fetch_ticker import TickerFetchAPI
from .api_order_cancel import CancelOrderAPI
from .api_order_limit import LimitOrderAPI
from .api_order_market import MarketOrderAPI
from .api_order_stop_limit import StopLimitOrderAPI
from .api_order_stop_market import StopMarketOrderAPI
from .api_wrapper import APIWrapper
from .exchange_property import ExchangeProperty
from .formatter_precision import PriceSizeFormatter
from .normalized_store_builder import NormalizedStoreBuilder
from .store_initializer import StoreInitializer
from .store_wrapper import DataStoreWrapper
from .websocket_request_builder import WebSocketRequestBuilder
from .websocket_resquest_customizer import WebSocketRequestCustomizer
from .._typedefs import TDataStoreManager


class WrapperFactory(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_store_initializer(
            cls,
            store: TDataStoreManager | None = None,
    ) -> StoreInitializer:
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
    def create_price_size_formatter(cls) -> PriceSizeFormatter:
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
    @abstractmethod
    def create_api_client(
            cls, client: pybotters.Client, verbose: bool = False
    ) -> APIClient:
        raise NotImplementedError

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
