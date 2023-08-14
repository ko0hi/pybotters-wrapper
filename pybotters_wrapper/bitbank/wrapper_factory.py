from typing import Callable

import pandas as pd
import pybotters
from aiohttp import ClientResponse
from pybotters import bitbankDataStore

from .base_url_attacher import bitbankBaseUrlAttacher
from .normalized_store_builder import bitbankNormalizedStoreBuilder
from .websocket_channels import bitbankWebsocketChannels
from .price_size_precision_fetcher import bitbankPriceSizePrecisionFetcher
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
    TickerFetchAPIBuilder,
    TickerFetchAPI,
    OrderbookFetchAPI,
    OrderbookFetchAPIBuilder,
    OrderbookItem,
    OrdersFetchAPI,
    OrdersFetchAPIBuilder,
    PositionsFetchAPIBuilder,
    PositionsFetchAPI,
    OrderAPI,
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
    _PRICE_SIZE_PRECISION_FETCHER = bitbankPriceSizePrecisionFetcher

    __ORDER_ID_KEY = "data.order_id"

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
            .set_order_id_extractor(cls._order_id_extractor)
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
            .set_order_id_extractor(cls._order_id_extractor)
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

    @classmethod
    def create_ticker_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> TickerFetchAPI:
        return (
            TickerFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator(lambda params: f"/{params['symbol']}/ticker")
            .set_parameter_translater(lambda params: {})
            .set_response_itemizer(
                lambda resp, data: {
                    "symbol": resp.url.raw_parts[1],
                    "price": float(data["data"]["last"]),
                }
            )
            .get()
        )

    @classmethod
    def create_orderbook_fetch_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> OrderbookFetchAPI:
        return (
            OrderbookFetchAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("GET")
            .set_endpoint_generator(lambda params: f"/{params['symbol']}/depth")
            .set_parameter_translater(lambda params: {})
            .set_response_itemizer(
                lambda resp, data: {
                    "SELL": [
                        OrderbookItem(
                            symbol=resp.url.raw_parts[1],
                            side="SELL",
                            price=float(d[0]),
                            size=float(d[1]),
                        )
                        for d in data["data"]["asks"]
                    ],
                    "BUY": [
                        OrderbookItem(
                            symbol=resp.url.raw_parts[1],
                            side="BUY",
                            price=float(d[0]),
                            size=float(d[1]),
                        )
                        for d in data["data"]["bids"]
                    ],
                }
            )
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
            .set_endpoint_generator("/user/spot/active_orders")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                }
            )
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "id": str(d["order_id"]),
                        "symbol": d["pair"],
                        "side": d["side"].upper(),
                        "price": float(d["price"]),
                        "size": float(d["remaining_amount"]),
                        "type": d["type"],
                        "timestamp": pd.to_datetime(
                            d["ordered_at"], utc=True, unit="ms"
                        ),
                    }
                    for d in data["data"]["orders"]
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
            .set_endpoint_generator("/user/assets")
            .set_parameter_translater(lambda params: {})
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "symbol": d["asset"],
                        "price": 0.0,
                        "size": float(d["free_amount"]),
                        "side": "BUY",
                    }
                    for d in data["data"]["assets"]
                    if float(d["onhand_amount"]) > 0
                ]
            )
            .get()
        )

    @classmethod
    def _order_id_extractor(
        cls, resp: ClientResponse, data: dict, order_id_key: str
    ) -> str | None:
        # bitbankはstatus_codeではなくbodyのsuccess fieldで成功の可否を判定する
        if data["success"] == 0:
            return None
        else:
            return OrderAPI._default_order_id_extractor(  # noqa
                resp, data, order_id_key
            )
