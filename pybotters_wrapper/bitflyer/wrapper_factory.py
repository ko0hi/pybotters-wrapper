import aiohttp
import pybotters
from pybotters import bitFlyerDataStore

from ..core import (
    APIWrapper,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
    DataStoreWrapper,
    DataStoreWrapperBuilder,
    ExchangeProperty,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    OrderbookFetchAPI,
    OrderbookFetchAPIBuilder,
    OrderbookItem,
    OrdersFetchAPI,
    OrdersFetchAPIBuilder,
    PositionsFetchAPI,
    PositionsFetchAPIBuilder,
    PriceSizePrecisionFetcher,
    PriceSizePrecisionFormatter,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    StoreInitializer,
    TDataStoreManager,
    TickerFetchAPI,
    TickerFetchAPIBuilder,
    TOrderbook,
    WebSocketDefaultRequestCustomizer,
    WebSocketRequestBuilder,
    WebSocketRequestCustomizer,
    WrapperFactory,
)
from .normalized_store_builder import bitFlyerNormalizedStoreBuilder
from .price_size_precision_fetcher import bitFlyerPriceSizePrecisionFetcher
from .websocket_channels import bitFlyerWebsocketChannels


class bitFlyerWrapperFactory(WrapperFactory):
    _ORDER_ID_KEY = "child_order_acceptance_id"

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
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key(cls._ORDER_ID_KEY)
            .set_endpoint_generator("/v1/me/sendchildorder")
            .set_parameter_translater(
                lambda params: {
                    "product_code": params["symbol"],
                    "side": params["side"],
                    "price": params["price"],
                    "size": params["size"],
                    "child_order_type": "LIMIT",
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("size")
            .get()
        )

    @classmethod
    def create_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> MarketOrderAPI:
        return (
            MarketOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key(cls._ORDER_ID_KEY)
            .set_endpoint_generator("/v1/me/sendchildorder")
            .set_parameter_translater(
                lambda params: {
                    "product_code": params["symbol"],
                    "side": params["side"],
                    "size": params["size"],
                    "child_order_type": "MARKET",
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("size")
            .get()
        )

    @classmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        return (
            CancelOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key(cls._ORDER_ID_KEY)
            .set_endpoint_generator("/v1/me/cancelchildorder")
            .set_parameter_translater(
                lambda params: {
                    "product_code": params["symbol"],
                    "child_order_acceptance_id": params["order_id"],
                }
            )
            .get()
        )

    @classmethod
    def create_stop_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopLimitOrderAPI:
        raise NotImplementedError

    @classmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI:
        raise NotImplementedError

    @classmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI:
        return (
            TickerFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/v1/getticker")
            .set_parameter_translater(lambda params: {"product_code": params["symbol"]})
            .set_response_itemizer(
                lambda resp, data: {
                    "symbol": data["product_code"],
                    "price": data["ltp"],
                }
            )
            .get()
        )

    @classmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI:
        def _response_itemizer(resp: aiohttp.ClientResponse, data: dict) -> TOrderbook:
            symbol = resp.request_info.url.query["product_code"]
            asks = [
                OrderbookItem(
                    symbol=symbol, side="SELL", price=i["price"], size=i["size"]
                )
                for i in data["asks"]
            ]
            bids = [
                OrderbookItem(
                    symbol=symbol, side="BUY", price=i["price"], size=i["size"]
                )
                for i in data["bids"]
            ]
            return {"SELL": asks, "BUY": bids}

        return (
            OrderbookFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/v1/getboard")
            .set_parameter_translater(lambda params: {"product_code": params["symbol"]})
            .set_response_itemizer(_response_itemizer)
            .get()
        )

    @classmethod
    def create_orders_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrdersFetchAPI:
        return (
            OrdersFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/v1/me/getchildorders")
            .set_parameter_translater(
                lambda params: {
                    "product_code": params["symbol"],
                    "child_order_state": "ACTIVE",
                }
            )
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "id": d["child_order_acceptance_id"],
                        "symbol": d["product_code"],
                        "side": d["side"],
                        "price": float(d["price"]),
                        "size": float(d["size"]),
                        "type": d["child_order_type"],
                    }
                    for d in data
                ]
            )
            .get()
        )

    @classmethod
    def create_positions_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> PositionsFetchAPI:
        return (
            PositionsFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/v1/me/getpositions")
            .set_parameter_translater(lambda params: {"product_code": params["symbol"]})
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "symbol": d["product_code"],
                        "side": d["side"],
                        "price": float(d["price"]),
                        "size": float(d["size"]),
                    }
                    for d in data
                ]
            )
            .get()
        )
