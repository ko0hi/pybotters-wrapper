import pybotters
from pybotters import GMOCoinDataStore

from .normalized_store_builder import GMOCoinNormalizedStoreBuilder
from .price_size_precision_fetcher import GMOCoinPriceSizePrecisionFetcher
from .websocket_channels import GMOCoinWebsocketChannels
from .websocket_request_customizer import GMOCoinWebsocketRequestCustomizer
from ..core import (
    WrapperFactory,
    StopMarketOrderAPI,
    CancelOrderAPI,
    MarketOrderAPI,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    MarketOrderAPIBuilder,
    CancelOrderAPIBuilder,
    StopMarketOrderAPIBuilder,
)


class GMOCoinWrapperFactory(WrapperFactory):
    __BASE_URL = "https://api.coin.z.com"
    _EXCHANGE_PROPERTIES = {
        "base_url": __BASE_URL,
        "exchange": "gmocoin",
    }
    _INITIALIZER_CONFIG = {
        "token": ("POST", f"{__BASE_URL}/private/v1/ws-auth", None),
        "token_private": ("POST", f"{__BASE_URL}/private/v1/ws-auth", None),
        "order": ("GET", f"{__BASE_URL}/private/v1/activeOrders", {"symbol"}),
        "position": ("GET", f"{__BASE_URL}/private/v1/openPositions", {"symbol"}),
    }
    _DATASTORE_MANAGER = GMOCoinDataStore
    _NORMALIZED_STORE_BUILDER = GMOCoinNormalizedStoreBuilder
    _WEBSOCKET_CHANNELS = GMOCoinWebsocketChannels
    _WEBSOCKET_REQUEST_CUSTOMIZER = GMOCoinWebsocketRequestCustomizer
    _PRICE_SIZE_PRECISION_FETCHER = GMOCoinPriceSizePrecisionFetcher

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("data")
            .set_endpoint_generator("/private/v1/order")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"],
                    "price": params["price"],
                    "size": params["size"],
                    "executionType": "LIMIT",
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
            .set_order_id_key("data")
            .set_endpoint_generator("/private/v1/order")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"],
                    "size": params["size"],
                    "executionType": "MARKET",
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
            .set_endpoint_generator("/private/v1/cancelOrder")
            .set_parameter_translater(
                lambda params: {
                    "order_id": int(params["order_id"]),
                }
            )
            .get()
        )

    @classmethod
    def create_stop_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> StopMarketOrderAPI:
        return (
            StopMarketOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("data")
            .set_endpoint_generator("/private/v1/order")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"],
                    "price": params["trigger"],
                    "size": params["size"],
                    "executionType": "STOP",
                    "timeInForce": "FAK",
                }
            )
            .get()
        )

