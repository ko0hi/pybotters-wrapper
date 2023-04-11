import pybotters
from pybotters.models.binance import BinanceUSDSMDataStore

from .websocket_channels_binanceusdsm import BinanceUSDSMWebsocketChannels
from ..common import (
    BinanceNormalizedStoreBuilder,
    BinanceWebSocketRequestCustomizer,
    BinancePriceSizePrecisionsFetcher,
)
from core import (
    DataStoreWrapperBuilder,
    StoreInitializer,
    ExchangeProperty,
    WebSocketRequestBuilder,
    APIClient,
    APIClientBuilder,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    LimitOrderAPITranslateParametersParameters,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    MarketOrderAPITranslateParametersParameters,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
    CancelOrderAPITranslateParametersParameters,
    StopLimitOrderAPI,
    StopLimitOrderAPIBuilder,
    StopLimitOrderAPITranslateParametersParameters,
    StopMarketOrderAPI,
    StopMarketOrderAPIBuilder,
    StopMarketOrderAPITranslateParametersParameters,
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
    price_precisions, size_precisions = BinancePriceSizePrecisionsFetcher(
        _EXCHANGE_PROPERTIES_BINANCEUSDSM["exchange"]
    ).fetch_precisions()
    return PriceSizeFormatter(price_precisions, size_precisions)


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
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/fapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("price")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_market_order_api(
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
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/fapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_cancel_order_api(
    client: pybotters.Client, verbose: bool = False
) -> CancelOrderAPI:
    def parameter_translater(
        params: CancelOrderAPITranslateParametersParameters,
    ) -> dict:
        return {"symbol": params["symbol"].upper(), "orderId": params["order_id"]}

    return (
        CancelOrderAPIBuilder()
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("DELETE")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/fapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .get()
    )


def create_binanceusdsm_stop_limit_order_api(
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
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/fapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("price", "stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )


def create_binanceusdsm_stop_market_order_api(
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
        .set_api_client(create_binanceusdsm_apiclient(client, verbose))
        .set_method("POST")
        .set_order_id_key("orderId")
        .set_endpoint_generator("/fapi/v1/order")
        .set_parameter_translater(parameter_translater)
        .set_price_size_formatter(create_binanceusdsm_price_size_formater())
        .set_price_format_keys("stopPrice")
        .set_size_format_keys("quantity")
        .get()
    )
