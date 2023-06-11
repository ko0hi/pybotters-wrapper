import pybotters
from pybotters import bitFlyerDataStore

from .normalized_store_builder import bitFlyerNormalizedStoreBuilder
from .price_size_precision_fetcher import bitFlyerPriceSizePrecisionFetcher
from .websocket_channels import bitFlyerWebsocketChannels
from ..core import (
    WrapperFactory,
    PositionsFetchAPI,
    OrdersFetchAPI,
    OrderbookFetchAPI,
    TickerFetchAPI,
    StopMarketOrderAPI,
    StopLimitOrderAPI,
    CancelOrderAPI,
    MarketOrderAPI,
    LimitOrderAPI,
    APIWrapper,
    PriceSizePrecisionFetcher,
    DataStoreWrapper,
    PriceSizePrecisionFormatter,
    WebSocketRequestCustomizer,
    WebSocketRequestBuilder,
    NormalizedStoreBuilder,
    StoreInitializer,
    ExchangeProperty,
    TDataStoreManager,
    WebSocketDefaultRequestCustomizer,
    DataStoreWrapperBuilder,
)


class bitFlyerWrapperFactory(WrapperFactory):
    @classmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        return ExchangeProperty(
            {"base_url": "https://api.bitflyer.com", "exchange": "bitflyer"}
        )

    @classmethod
    def create_store_initializer(cls, store: TDataStoreManager) -> StoreInitializer:
        base_url = cls.create_exchange_property().base_url
        return StoreInitializer(
            store or bitFlyerDataStore(),
            {
                "order": ("GET", f"{base_url}/v1/me/getchildorders", {"product_code"}),
                "position": ("GET", f"{base_url}/v1/me/getpositions", {"product_code"}),
            },
        )

    @classmethod
    def create_normalized_store_builder(
        cls, store: bitFlyerDataStore | None = None
    ) -> bitFlyerNormalizedStoreBuilder:
        return bitFlyerNormalizedStoreBuilder(store or bitFlyerDataStore())

    @classmethod
    def create_websocket_request_builder(cls) -> WebSocketRequestBuilder:
        return WebSocketRequestBuilder(bitFlyerWebsocketChannels())

    @classmethod
    def create_websocket_request_customizer(cls) -> WebSocketRequestCustomizer:
        return WebSocketDefaultRequestCustomizer()

    @classmethod
    def create_price_size_precisions_fetcher(cls) -> PriceSizePrecisionFetcher:
        return bitFlyerPriceSizePrecisionFetcher()

    @classmethod
    def create_price_size_formatter(cls) -> PriceSizePrecisionFormatter:
        precisions = cls.create_price_size_precisions_fetcher().fetch_precisions()
        return PriceSizePrecisionFormatter(precisions["price"], precisions["size"])

    @classmethod
    def create_store(cls, store: bitFlyerDataStore | None = None) -> DataStoreWrapper:
        store = store or bitFlyerDataStore()
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
    def create_api(cls, client: pybotters.Client, verbose: bool = False) -> APIWrapper:
        ...

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
