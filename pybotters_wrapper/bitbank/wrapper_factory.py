from typing import Callable

import pybotters
from pybotters import bitbankDataStore

from .base_url_attacher import bitbankBaseUrlAttacher
from .normalized_store_builder import bitbankNormalizedStoreBuilder
from .websocket_channels import bitbankWebsocketChannels
from ..core import (
    WrapperFactory,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    APIClient,
    APIClientBuilder,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    CancelOrderAPI,
    CancelOrderAPIBuilder,
)


class bitbankWrapperFactory(WrapperFactory):
    __BASE_URL = "https://public.bitbank.cc"
    _EXCHANGE_PROPERTIES = {
        "base_url": __BASE_URL,
        "exchange": "bitbank",
    }
    _DATASTORE_MANAGER = bitbankDataStore
    _WEBSOCKET_CHANNELS = bitbankWebsocketChannels
    _NORMALIZED_STORE_BUILDER = bitbankNormalizedStoreBuilder

    __ORDER_ID_KEY = "data.order_id"

    @classmethod
    def create_api_client(
        cls,
        client: pybotters.Client,
        verbose: bool = False,
        *,
        base_url_attacher: Callable[[str], str] | None = None
    ) -> APIClient:
        return (
            APIClientBuilder()
            .set_client(client)
            .set_verbose(verbose)
            .set_exchange_property(cls.create_exchange_property())
            # bitbankはprivateとpublicでbase_urlが異なる
            .set_base_url_attacher(bitbankBaseUrlAttacher())
            .get()
        )

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator("/user/spot/order")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "side": params["side"].lower(),
                    "price": params["price"],
                    "amount": params["size"],
                    "type": "limit",
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("amount")
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
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator("/user/spot/order")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "side": params["side"].lower(),
                    "amount": params["size"],
                    "type": "market",
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("price")
            .set_size_format_keys("amount")
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
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator("/user/spot/cancel_order")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "order_id": params["order_id"],
                }
            )
            .get()
        )
