import uuid

import pybotters
from pybotters import KuCoinDataStore

from .price_size_precision_fetcher import KuCoinSpotPriceSizePrecisionFetcher
from .websocket_channels import KuCoinSpotWebSocketChannels
from ..normalized_store_builder import KuCoinNormalizedStoreBuilder
from ..websocket_request_customizer import (
    create_websocket_request_customizer,
)
from ...core import (
    WrapperFactory,
    CancelOrderAPIBuilder,
    CancelOrderAPI,
    MarketOrderAPI,
    LimitOrderAPI,
    LimitOrderAPIBuilder, MarketOrderAPIBuilder,
)


class KuCoinSpotWrapperFactory(WrapperFactory):
    __BASE_URL = "https://api.kucoin.com"
    _EXCHANGE_PROPERTIES = {
        "exchange": "kucoinspot",
        "base_url": __BASE_URL,
    }
    _DATASTORE_MANAGER = KuCoinDataStore
    _WEBSOCKET_CHANNELS = KuCoinSpotWebSocketChannels
    _WEBSOCKET_REQUEST_CUSTOMIZER = create_websocket_request_customizer("kucoinspot")
    _PRICE_SIZE_PRECISION_FETCHER = KuCoinSpotPriceSizePrecisionFetcher
    _INITIALIZER_CONFIG = {
        "token": ("POST", "/api/v1/bullet-private", None),
        "token_public": ("POST", "/api/v1/bullet-public", None),
        "token_private": ("POST", "/api/v1/bullet-private", None),
        "position": ("GET", "/api/v1/positions", None),
    }
    _NORMALIZED_STORE_BUILDER = KuCoinNormalizedStoreBuilder

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("data.orderId")
            .set_endpoint_generator("/api/v1/orders")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"].lower(),
                    "price": params["price"],
                    "size": params["size"],
                    "client0id": str(uuid.uuid4()),
                    "type": "limit",
                }
            )
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
            .set_order_id_key("data.orderId")
            .set_endpoint_generator("/api/v1/orders")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"].lower(),
                    "size": params["size"],
                    "type": "market",
                    "client0id": str(uuid.uuid4()),
                }
            )
        )

    @classmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        return (
            CancelOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("DELETE")
            .set_endpoint_generator(
                lambda params: f"/api/v1/orders/{params['order_id']}"
            )
            .set_parameter_translater({})
            .get()
        )
