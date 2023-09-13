from typing import Callable

import aiohttp
import pybotters
from pybotters import BinanceUSDSMDataStore

from ...core import (
    APIClient,
    APIClientBuilder,
    APIWrapper,
    APIWrapperBuilder,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
    CancelOrderAPITranslateParametersParameters,
    DataStoreWrapper,
    DataStoreWrapperBuilder,
    ExchangeProperty,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    LimitOrderAPITranslateParametersParameters,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    MarketOrderAPITranslateParametersParameters,
    OrderbookFetchAPI,
    OrderbookFetchAPIBuilder,
    OrderbookFetchAPITranslateParametersParameters,
    OrderbookItem,
    OrderItem,
    OrdersFetchAPI,
    OrdersFetchAPIBuilder,
    OrdersFetchAPITranslateParametersParameters,
    PositionItem,
    PositionsFetchAPI,
    PositionsFetchAPIBuilder,
    PositionsFetchAPITranslateParametersParameters,
    PriceSizePrecisionFormatter,
    StopLimitOrderAPI,
    StopLimitOrderAPIBuilder,
    StopLimitOrderAPITranslateParametersParameters,
    StopMarketOrderAPI,
    StopMarketOrderAPIBuilder,
    StopMarketOrderAPITranslateParametersParameters,
    StoreInitializer,
    TDataStoreManager,
    TickerFetchAPI,
    TickerFetchAPIBuilder,
    TickerFetchAPITranslateParametersParameters,
    TickerItem,
    TSide,
    WebSocketRequestBuilder,
    WebSocketRequestCustomizer,
    WrapperFactory,
)
from ..normalized_store_builder import BinanceNormalizedStoreBuilder
from ..price_size_precision_fetcher import BinancePriceSizePrecisionFetcher
from ..websocket_request_customizer import BinanceWebSocketRequestCustomizer
from . import BinanceUSDSMWebsocketChannels


class BinanceUSDSMWrapperFactory(WrapperFactory):
    _CACHE_PRICE_SIZE_FORMATTER = None

    @classmethod
    def create_exchange_property(cls) -> ExchangeProperty:
        return ExchangeProperty(
            {
                "base_url": "https://fapi.binance.com",
                "exchange": "binanceusdsm",
            }
        )

    @classmethod
    def create_store_initializer(
        cls, store: BinanceUSDSMDataStore = None
    ) -> StoreInitializer:
        base_url = cls.create_exchange_property().base_url
        return StoreInitializer(
            store,
            {
                "token": ("POST", f"{base_url}/fapi/v1/listenKey", None),
                "token_private": ("POST", f"{base_url}/fapi/v1/listenKey", None),
                "orderbook": ("GET", f"{base_url}/fapi/v1/depth", {"symbol"}),
                "order": ("GET", f"{base_url}/fapi/v1/openOrders", None),
                "position": ("GET", f"{base_url}/fapi/v2/positionRisk", None),
            },
        )

    @classmethod
    def create_normalized_store_builder(
        cls, store: TDataStoreManager | None = None
    ) -> BinanceNormalizedStoreBuilder:
        return BinanceNormalizedStoreBuilder(store or BinanceUSDSMDataStore())

    @classmethod
    def create_websocket_request_builder(cls) -> WebSocketRequestBuilder:
        return WebSocketRequestBuilder(BinanceUSDSMWebsocketChannels())

    @classmethod
    def create_websocket_request_customizer(
        cls, client: pybotters.Client | None = None
    ) -> WebSocketRequestCustomizer:
        return BinanceWebSocketRequestCustomizer(
            cls.create_exchange_property().exchange
        )

    @classmethod
    def create_price_size_formatter(cls) -> PriceSizePrecisionFormatter:
        if cls._CACHE_PRICE_SIZE_FORMATTER is not None:
            return cls._CACHE_PRICE_SIZE_FORMATTER
        precisions = BinancePriceSizePrecisionFetcher(
            cls.create_exchange_property().exchange
        ).fetch_precisions()
        cls._CACHE_PRICE_SIZE_FORMATTER = PriceSizePrecisionFormatter(
            precisions["price"], precisions["size"]
        )
        return cls._CACHE_PRICE_SIZE_FORMATTER

    @classmethod
    def create_store(cls, store: TDataStoreManager | None = None) -> DataStoreWrapper:
        store = store or BinanceUSDSMDataStore()
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
        return (
            APIWrapperBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_limit_order_api(cls.create_limit_order_api(client, verbose))
            .set_market_order_api(cls.create_market_order_api(client, verbose))
            .set_cancel_order_api(cls.create_cancel_order_api(client, verbose))
            .set_stop_limit_order_api(cls.create_stop_limit_order_api(client, verbose))
            .set_stop_market_order_api(
                cls.create_stop_market_order_api(client, verbose)
            )
            .set_ticker_fetch_api(cls.create_ticker_fetch_api(client, verbose))
            .set_orderbook_fetch_api(cls.create_orderbook_fetch_api(client, verbose))
            .set_orders_fetch_api(cls.create_orders_fetch_api(client, verbose))
            .set_positions_fetch_api(cls.create_positions_fetch_api(client, verbose))
            .get()
        )

    @classmethod
    def create_api_client(
        cls,
        client: pybotters.Client,
        verbose: bool = False,
        *,
        base_url_attacher: Callable[[str], str] | None = None,
    ) -> APIClient:
        return (
            APIClientBuilder()
            .set_client(client)
            .set_verbose(verbose)
            .set_exchange_property(cls.create_exchange_property())
            .get()
        )

    @classmethod
    def create_limit_order_api(
        cls,
        client: pybotters.Client,
        verbose: bool = False,
    ) -> LimitOrderAPI:
        def parameter_translater(
            params: LimitOrderAPITranslateParametersParameters,
        ) -> dict:
            return {
                "symbol": params["symbol"].upper(),
                "side": params["side"].upper(),
                "type": "LIMIT",
                "price": params["price"],
                "quantity": params["size"],
                "timeInForce": "GTC",
            }

        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("orderId")
            .set_endpoint_generator("/fapi/v1/order")
            .set_parameter_translater(parameter_translater)
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("quantity")
            .get()
        )

    @classmethod
    def create_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> MarketOrderAPI:
        def parameter_translater(
            params: MarketOrderAPITranslateParametersParameters,
        ) -> dict:
            return {
                "symbol": params["symbol"].upper(),
                "side": params["side"].upper(),
                "type": "MARKET",
                "quantity": params["size"],
            }

        return (
            MarketOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("orderId")
            .set_endpoint_generator("/fapi/v1/order")
            .set_parameter_translater(parameter_translater)
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_size_format_keys("quantity")
            .get()
        )

    @classmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        def parameter_translater(
            params: CancelOrderAPITranslateParametersParameters,
        ) -> dict:
            return {"symbol": params["symbol"].upper(), "orderId": params["order_id"]}

        return (
            CancelOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("DELETE")
            .set_order_id_key("orderId")
            .set_endpoint_generator("/fapi/v1/order")
            .set_parameter_translater(parameter_translater)
            .get()
        )

    @classmethod
    def create_stop_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopLimitOrderAPI:
        def parameter_translater(
            params: StopLimitOrderAPITranslateParametersParameters,
        ) -> dict:
            return {
                "symbol": params["symbol"].upper(),
                "side": params["side"].upper(),
                "type": "STOP",
                "price": params["price"],
                "quantity": params["size"],
                "stopPrice": params["trigger"],
                "timeInForce": "GTC",
            }

        return (
            StopLimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("orderId")
            .set_endpoint_generator("/fapi/v1/order")
            .set_parameter_translater(parameter_translater)
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price", "stopPrice")
            .set_size_format_keys("quantity")
            .get()
        )

    @classmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI:
        def parameter_translater(
            params: StopMarketOrderAPITranslateParametersParameters,
        ) -> dict:
            return {
                "symbol": params["symbol"].upper(),
                "side": params["side"].upper(),
                "type": "STOP_MARKET",
                "quantity": params["size"],
                "stopPrice": params["trigger"],
            }

        return (
            StopMarketOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("orderId")
            .set_endpoint_generator("/fapi/v1/order")
            .set_parameter_translater(parameter_translater)
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("stopPrice")
            .set_size_format_keys("quantity")
            .get()
        )

    @classmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI:
        def parameter_translater(
            params: TickerFetchAPITranslateParametersParameters,
        ) -> dict:
            return {"symbol": params["symbol"].upper()}

        def response_itemizer(
            resp: aiohttp.ClientResponse, resp_data: dict
        ) -> TickerItem:
            return {"symbol": resp_data["symbol"], "price": float(resp_data["price"])}

        return (
            TickerFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/fapi/v1/ticker/price")
            .set_parameter_translater(parameter_translater)
            .set_response_itemizer(response_itemizer)
            .get()
        )

    @classmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI:
        def parameter_translater(
            params: OrderbookFetchAPITranslateParametersParameters,
        ) -> dict:
            return {"symbol": params["symbol"].upper()}

        def response_itemizer(
            resp: aiohttp.ClientResponse, resp_data: dict
        ) -> dict[TSide, list[OrderbookItem]]:
            symbol = resp.request_info.url.query["symbol"]
            asks = [
                OrderbookItem(
                    symbol=symbol, side="SELL", price=float(i[0]), size=float(i[1])
                )
                for i in resp_data["asks"]
            ]
            bids = [
                OrderbookItem(
                    symbol=symbol, side="BUY", price=float(i[0]), size=float(i[1])
                )
                for i in resp_data["bids"]
            ]
            return {"SELL": asks, "BUY": bids}

        return (
            OrderbookFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/fapi/v1/depth")
            .set_parameter_translater(parameter_translater)
            .set_response_itemizer(response_itemizer)
            .get()
        )

    @classmethod
    def create_orders_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrdersFetchAPI:
        def parameter_translater(
            params: OrdersFetchAPITranslateParametersParameters,
        ) -> dict:
            return {"symbol": params["symbol"].upper()}

        def response_itemizer(
            resp: aiohttp.ClientResponse, resp_data: dict
        ) -> list[OrderItem]:
            return [
                OrderItem(
                    id=str(i["orderId"]),
                    symbol=i["symbol"],
                    side=i["side"],
                    price=float(i["price"]),
                    size=float(i["origQty"]) - float(i["executedQty"]),
                    type=i["type"],
                    info=i,  # noqa
                )
                for i in resp_data
            ]

        return (
            OrdersFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/fapi/v1/openOrders")
            .set_parameter_translater(parameter_translater)
            .set_response_itemizer(response_itemizer)
            .get()
        )

    @classmethod
    def create_positions_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> PositionsFetchAPI:
        def parameter_translater(
            params: PositionsFetchAPITranslateParametersParameters,
        ) -> dict:
            return {"symbol": params["symbol"].upper()}

        def response_itemizer(
            resp: aiohttp.ClientResponse, resp_data: dict
        ) -> list[PositionItem]:
            return [
                PositionItem(
                    symbol=i["symbol"],
                    side=("BUY" if float(i["positionAmt"]) > 0 else "SELL"),
                    price=float(i["entryPrice"]),
                    size=float(i["positionAmt"]),
                    info=i,  # noqa
                )
                for i in resp_data
            ]

        return (
            PositionsFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator("/fapi/v2/positionRisk")
            .set_parameter_translater(parameter_translater)
            .set_response_itemizer(response_itemizer)
            .get()
        )
