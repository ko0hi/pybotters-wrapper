import pybotters

from ..core import (
    APIClient,
    APIWrapper,
    CancelOrderAPI,
    DataStoreWrapper,
    ExchangeProperty,
    LimitOrderAPI,
    MarketOrderAPI,
    NormalizedStoreBuilder,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
    PriceSizePrecisionFormatter,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    StoreInitializer,
    TDataStoreManager,
    TickerFetchAPI,
    WebSocketRequestBuilder,
    WebSocketRequestCustomizer,
    WrapperFactory,
)
from .websocket_channels import PhemexWebsocketChannels


class PhemexWrapperFactory(WrapperFactory):
    @classmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        pass

    @classmethod
    def create_store_initializer(
        cls, store: TDataStoreManager | None = None
    ) -> StoreInitializer:
        pass

    @classmethod
    def create_normalized_store_builder(
        cls, store: TDataStoreManager | None = None
    ) -> NormalizedStoreBuilder:
        pass

    @classmethod
    def create_websocket_request_builder(cls) -> WebSocketRequestBuilder:
        return WebSocketRequestBuilder(PhemexWebsocketChannels())

    @classmethod
    def create_websocket_request_customizer(cls) -> WebSocketRequestCustomizer:
        pass

    @classmethod
    def create_price_size_formatter(cls) -> PriceSizePrecisionFormatter:
        pass

    @classmethod
    def create_store(cls, store: TDataStoreManager | None = None) -> DataStoreWrapper:
        pass

    @classmethod
    def create_api(cls, client: pybotters.Client, verbose: bool = False) -> APIWrapper:
        pass

    @classmethod
    def create_api_client(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> APIClient:
        pass

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        pass

    @classmethod
    def create_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> MarketOrderAPI:
        pass

    @classmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        pass

    @classmethod
    def create_stop_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopLimitOrderAPI:
        pass

    @classmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI:
        pass

    @classmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI:
        pass

    @classmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI:
        pass

    @classmethod
    def create_orders_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrdersFetchAPI:
        pass

    @classmethod
    def create_positions_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> PositionsFetchAPI:
        pass
