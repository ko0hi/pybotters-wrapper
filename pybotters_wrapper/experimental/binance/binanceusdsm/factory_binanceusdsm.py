import pybotters
from pybotters.models.binance import BinanceUSDSMDataStore

from .websocket_channels_binanceusdsm import BinanceUSDSMWebsocketChannels
from ..common.normalized_store_builder import BinanceNormalizedStoreBuilder
from ..common.websocket_request_customizer_binance import (
    BinanceWebSocketRequestCustomizer,
)
from ...core import (
    DataStoreWrapperBuilder,
    StoreInitializer,
    ExchangeProperty,
    WebSocketRequestBuilder,
    APIClient,
    APIClientBuilder,
    OrderAPIBuilder,
    LimitOrderAPI,
    MarketOrderAPI,
    CancelOrderAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    PriceSizeFormatter,
)

_EXCHANGE_PROPERTIES_BINANCEUSDSM = {
    "base_url": "https://fapi.binance.com",
    "exchange": "binanceusdsm",
}
__base = _EXCHANGE_PROPERTIES_BINANCEUSDSM["base_url"]
_STORE_INITIALIZER_CONFIG_BINANCEUSDSM = {
    "token": ("POST", f"{__base}/fapi/v1/listenKey"),
    "token_private": ("POST", f"{__base}/fapi/v1/listenKey"),
    "orderbook": ("GET", f"{__base}/fapi/v1/depth", {"symbol"}),
    "order": ("GET", f"{__base}/fapi/v1/openOrders"),
    "position": ("GET", f"{__base}/fapi/v2/positionRisk"),
}


def create_binanceusdsm_exchange_property() -> ExchangeProperty:
    return ExchangeProperty(_EXCHANGE_PROPERTIES_BINANCEUSDSM)


def create_binanceusdsm_store_initializer(
    store: BinanceUSDSMDataStore,
) -> StoreInitializer:
    return StoreInitializer(store, _STORE_INITIALIZER_CONFIG_BINANCEUSDSM)


def create_binanceusdsm_normalized_store_builder(
    store: BinanceUSDSMDataStore,
) -> BinanceNormalizedStoreBuilder:
    return BinanceNormalizedStoreBuilder(store)


def create_binanceusdsm_websocket_request_builder() -> WebSocketRequestBuilder:
    return WebSocketRequestBuilder(BinanceUSDSMWebsocketChannels())


def create_binanceusdsm_websockt_request_customizer() -> (
    BinanceWebSocketRequestCustomizer
):
    return BinanceWebSocketRequestCustomizer(
        _EXCHANGE_PROPERTIES_BINANCEUSDSM["exchange"]
    )


def create_binanceusdsm_price_size_formater() -> PriceSizeFormatter:
    raise NotImplementedError

def create_binanceusdsm_store(store: BinanceUSDSMDataStore | None = None):
    store = store or BinanceUSDSMDataStore()
    return (
        DataStoreWrapperBuilder()
        .set_store(store)
        .set_exchange_property(create_binanceusdsm_exchange_property())
        .set_store_initializer(create_binanceusdsm_store_initializer(store))
        .set_normalized_store_builder(
            create_binanceusdsm_normalized_store_builder(store)
        )
        .set_websocket_request_builder(create_binanceusdsm_websocket_request_builder())
        .set_websocket_request_customizer(
            create_binanceusdsm_websockt_request_customizer()
        )
        .get()
    )


def create_binanceusdsm_apiclient(
    client: pybotters.Client, verbose: bool = False
) -> APIClient:
    return (
        APIClientBuilder.set_client(client)
        .set_verbose(verbose)
        .set_exchange_property(create_binanceusdsm_exchange_property())
        .get()
    )


def create_binanceusdsm_limit_order_api(
    client: pybotters.Client, verbose: bool = False
) -> LimitOrderAPI:
    return (
        OrderAPIBuilder()
        .set_type("limit")
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint("/fapi/v1/order")
        .set_parameter_translater(
            lambda symbol, side, price, size, extra: {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "LIMIT",
                "price": price,
                "quantity": size,
                "timeInForce": "GTC",
            }
        )
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("price")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_market_order_api(
    client: pybotters.Client, verbose: bool = False
) -> MarketOrderAPI:
    return (
        OrderAPIBuilder()
        .set_type("limit")
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint("/fapi/v1/order")
        .set_parameter_translater(
            lambda symbol, side, size, extra: {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "MARKET",
                "quantity": size,
            }
        )
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_cancel_order_api(
    client: pybotters.Client, verbose: bool = False
) -> CancelOrderAPI:
    return (
        OrderAPIBuilder()
        .set_type("cancel")
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("DELETE")
        .set_order_id_key("orderId")
        .set_endpoint("/fapi/v1/order")
        .set_parameter_translater(
            lambda symbol, order_id, extra: {
                "symbol": symbol.upper(),
                "orderId": order_id,
            }
        )
        .get()
    )


def create_binanceusdsm_stop_limit_order_api(
    client: pybotters.Client, verbose: bool = False
) -> StopLimitOrderAPI:
    return (
        OrderAPIBuilder()
        .set_type("stop_limit")
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint("/fapi/v1/order")
        .set_parameter_translater(
            lambda symbol, side, price, size, trigger, extra: {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "STOP",
                "price": price,
                "quantity": size,
                "stopPrice": trigger,
                "timeInForce": "GTC",
            }
        )
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("price", "stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_stop_market_order_api(
    client: pybotters.Client, verbose: bool = False
) -> StopMarketOrderAPI:
    return (
        OrderAPIBuilder()
        .set_type("stop_limit")
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint("/fapi/v1/order")
        .set_parameter_translater(
            lambda symbol, side, size, trigger, extra: {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "STOP_MARKET",
                "quantity": size,
                "stopPrice": trigger,
                "timeInForce": "GTC",
            }
        )
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )
