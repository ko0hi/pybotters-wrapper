import aiohttp
import pybotters
from pybotters.models.binance import BinanceCOINMDataStore

from ..._typedefs import TSide
from ...core import (
    APIClient,
    APIClientBuilder,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
    CancelOrderAPITranslateParametersParameters,
    DataStoreWrapperBuilder,
    ExchangeProperty,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    LimitOrderAPITranslateParametersParameters,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    MarketOrderAPITranslateParametersParameters,
    PriceSizeFormatter,
    StopLimitOrderAPI,
    StopLimitOrderAPIBuilder,
    StopLimitOrderAPITranslateParametersParameters,
    StopMarketOrderAPI,
    StopMarketOrderAPIBuilder,
    StopMarketOrderAPITranslateParametersParameters,
    StoreInitializer,
    WebSocketRequestBuilder,
    TickerFetchAPI,
    TickerFetchAPIBuilder,
    TickerFetchAPITranslateParametersParameters,
    TickerItem,
    OrderbookFetchAPI,
    OrderbookFetchAPIBuilder,
    OrderbookFetchAPITranslateParametersParameters,
    OrderbookItem,
    OrdersFetchAPI,
    OrdersFetchAPIBuilder,
    OrdersFetchAPITranslateParametersParameters,
    OrderItem,
    PositionsFetchAPI,
    PositionsFetchAPIBuilder,
    PositionsFetchAPITranslateParametersParameters,
    PositionItem,
)
from ..common import (
    BinanceNormalizedStoreBuilder,
    BinancePriceSizePrecisionsFetcher,
    BinanceWebSocketRequestCustomizer,
)
from .websocket_channels_binancecoinm import BinanceCOINMWebsocketChannels


def create_binancecoinm_exchange_property() -> ExchangeProperty:
    return ExchangeProperty(
        {
            "base_url": "https://dapi.binance.com",
            "exchange": "binancecoinm",
        }
    )


def create_binancecoinm_store_initializer(
    store: BinanceCOINMDataStore | None = None,
) -> StoreInitializer:
    base_url = create_binancecoinm_exchange_property().base_url
    return StoreInitializer(
        store or BinanceCOINMDataStore(),
        {
            "token": ("POST", f"{base_url}/dapi/v1/listenKey"),
            "token_private": ("POST", f"{base_url}/dapi/v1/listenKey"),
            "orderbook": ("GET", f"{base_url}/dapi/v1/depth", {"symbol"}),
            "order": ("GET", f"{base_url}/dapi/v1/openOrders"),
            "position": ("GET", f"{base_url}/dapi/v1/positionRisk"),
        },
    )


def create_binancecoinm_normalized_store_builder(
    store: BinanceCOINMDataStore | None = None,
) -> BinanceNormalizedStoreBuilder:
    return BinanceNormalizedStoreBuilder(store or BinanceCOINMDataStore())


def create_binancecoinm_websocket_request_builder() -> WebSocketRequestBuilder:
    return WebSocketRequestBuilder(BinanceCOINMWebsocketChannels())


def create_binancecoinm_websocket_request_customizer() -> BinanceWebSocketRequestCustomizer:
    return BinanceWebSocketRequestCustomizer(
        create_binancecoinm_exchange_property().exchange
    )


def create_binancecoinm_price_size_formater() -> PriceSizeFormatter:
    precisions = BinancePriceSizePrecisionsFetcher(
        create_binancecoinm_exchange_property().exchange
    ).fetch_precisions()
    return PriceSizeFormatter(precisions["price"], precisions["size"])


def create_binancecoinm_store(store: BinanceCOINMDataStore | None = None):
    store = store or BinanceCOINMDataStore()
    return (
        DataStoreWrapperBuilder()
        .set_store(store)
        .set_exchange_property(create_binancecoinm_exchange_property())
        .set_store_initializer(create_binancecoinm_store_initializer(store))
        .set_normalized_store_builder(
            create_binancecoinm_normalized_store_builder(store)
        )
        .set_websocket_request_builder(create_binancecoinm_websocket_request_builder())
        .set_websocket_request_customizer(
            create_binancecoinm_websocket_request_customizer()
        )
        .get()
    )


def create_binancecoinm_apiclient(
    client: pybotters.Client, verbose: bool = False
) -> APIClient:
    return (
        APIClientBuilder()
        .set_client(client)
        .set_verbose(verbose)
        .set_exchange_property(create_binancecoinm_exchange_property())
        .get()
    )


def create_binancecoinm_limit_order_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/dapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binancecoinm_price_size_formater())
        .set_price_format_keys("price")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binancecoinm_market_order_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/dapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binancecoinm_price_size_formater())
        .set_size_format_keys("quantity")
        .get()
    )


def create_binancecoinm_cancel_order_api(
    client: pybotters.Client, verbose: bool = False
) -> CancelOrderAPI:
    def parameter_translater(
        params: CancelOrderAPITranslateParametersParameters,
    ) -> dict:
        return {"symbol": params["symbol"].upper(), "orderId": params["order_id"]}

    return (
        CancelOrderAPIBuilder()
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("DELETE")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/dapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .get()
    )


def create_binancecoinm_stop_limit_order_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/dapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binancecoinm_price_size_formater())
        .set_price_format_keys("price", "stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binancecoinm_stop_market_order_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/dapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binancecoinm_price_size_formater())
        .set_price_format_keys("stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binancecoinm_fetch_ticker_api(
    client: pybotters.Client, verbose: bool = False
) -> TickerFetchAPI:
    def parameter_translater(
        params: TickerFetchAPITranslateParametersParameters,
    ) -> dict:
        return {"symbol": params["symbol"].upper()}

    def response_itemizer(resp: aiohttp.ClientResponse, resp_data: dict) -> TickerItem:
        return {"symbol": resp_data["symbol"], "price": float(resp_data["price"])}

    return (
        TickerFetchAPIBuilder()
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("GET")
        .set_endpoint_generator("/dapi/v1/ticker/price")
        .set_parameter_translater(parameter_translater)
        .set_response_itemizer(response_itemizer)
        .get()
    )


def create_binancecoinm_fetch_orderbook_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("GET")
        .set_endpoint_generator("/dapi/v1/depth")
        .set_parameter_translater(parameter_translater)
        .set_response_itemizer(response_itemizer)
        .get()
    )


def create_binancecoinm_fetch_orders_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("GET")
        .set_endpoint_generator("/dapi/v1/openOrders")
        .set_parameter_translater(parameter_translater)
        .set_response_itemizer(response_itemizer)
        .get()
    )


def create_binancecoinm_fetch_positions_api(
    client: pybotters.Client, verbose: bool = False
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
        .set_api_client(create_binancecoinm_apiclient(client, verbose))
        .set_method("GET")
        .set_endpoint_generator("/dapi/v1/positionRisk")
        .set_parameter_translater(parameter_translater)
        .set_response_itemizer(response_itemizer)
        .get()
    )
