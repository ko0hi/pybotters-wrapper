import pybotters
from pybotters import BybitUSDTDataStore

from .websocket_channels import BybitUSDTWebSocketChannels
from ..normalized_store_builder import BybitNormalizedStoreBuilder
from ..price_size_precision_fetcher import BybitPriceSizePrecisionFetcher
from ...core import (
    WrapperFactory,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
)


class BybitUSDTWrapperFactory(WrapperFactory):
    __BASE_URL = "https://api.bybit.com"
    _EXCHANGE_PROPERTIES = {
        "exchange": "bybitinverse",
        "base_url": __BASE_URL,
    }
    _DATASTORE_MANAGER = BybitUSDTDataStore
    _WEBSOCKET_CHANNELS = BybitUSDTWebSocketChannels
    _NORMALIZED_STORE_BUILDER = BybitNormalizedStoreBuilder
    _PRICE_SIZE_PRECISION_FETCHER = BybitPriceSizePrecisionFetcher
    _INITIALIZER_CONFIG = {
        "order": ("GET", f"{__BASE_URL}/private/linear/order/search", {"symbol"}),
        "position": ("GET", f"{__BASE_URL}/private/linear/position/list", None),
    }

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key("result.order_id")
            .set_endpoint_generator("/private/linear/order/create")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"].capitalize(),
                    "order_type": "Limit",
                    "price": params["price"],
                    "qty": params["size"],
                    "time_in_force": "GoodTillCancel",
                    "reduce_only": False,
                    "close_on_trigger": False,
                    "position_idx": 0,
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("qty")
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
            .set_order_id_key("result.order_id")
            .set_endpoint_generator("/private/linear/order/create")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "side": params["side"].capitalize(),
                    "order_type": "Market",
                    "qty": params["size"],
                    "time_in_force": "GoodTillCancel",
                    "reduce_only": False,
                    "close_on_trigger": False,
                    "position_idx": 0,
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("qty")
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
            .set_order_id_key("result.order_id")
            .set_endpoint_generator("/private/linear/order/cancel")
            .set_parameter_translater(
                lambda params: {
                    "symbol": params["symbol"],
                    "order_id": params["order_id"],
                }
            )
            .get()
        )
