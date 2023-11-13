import pandas as pd
import pybotters
from pybotters import CoincheckDataStore

from ..core import (
    CancelOrderAPI,
    CancelOrderAPIBuilder,
    LimitOrderAPI,
    LimitOrderAPIBuilder,
    MarketOrderAPI,
    MarketOrderAPIBuilder,
    MarketOrderAPITranslateParametersParameters,
    OrderbookFetchAPI,
    OrderbookFetchAPIBuilder,
    OrderbookItem,
    OrdersFetchAPI,
    OrdersFetchAPIBuilder,
    PositionsFetchAPI,
    PositionsFetchAPIBuilder,
    StopMarketOrderAPI,
    StopMarketOrderAPIBuilder,
    StopMarketOrderAPITranslateParametersParameters,
    TickerFetchAPI,
    TickerFetchAPIBuilder,
    WrapperFactory,
)
from .normalized_store_builder import CoincheckNormalizedStoreBuilder
from .websocket_channels import CoincheckWebsocketChannels


class CoincheckWrapperFactory(WrapperFactory):
    __BASE_URL = "https://coincheck.com"
    _EXCHANGE_PROPERTIES = {
        "base_url": __BASE_URL,
        "exchange": "coincheck",
    }
    _DATASTORE_MANAGER = CoincheckDataStore
    _WEBSOCKET_CHANNELS = CoincheckWebsocketChannels
    _NORMALIZED_STORE_BUILDER = CoincheckNormalizedStoreBuilder

    __ORDER_ID_KEY = "id"

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        return (
            LimitOrderAPIBuilder()
            .set_api_client(cls.create_api_client(client, verbose))
            .set_method("POST")
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator("/api/exchange/orders")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "order_type": params["side"].lower(),
                    "rate": params["price"],
                    "amount": params["size"],
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("rate")
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
            .set_endpoint_generator("/api/exchange/orders")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "order_type": "market_" + params["side"].lower(),
                    **cls._amount_parameter(params),
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("rate")
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
            .set_method("DELETE")
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator(
                lambda params: f"/api/exchange/orders/{params['order_id']}"
            )
            .set_parameter_translater(lambda params: {})
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
            .set_order_id_key(cls.__ORDER_ID_KEY)
            .set_endpoint_generator("/api/exchange/orders")
            .set_parameter_translater(
                lambda params: {
                    "pair": params["symbol"],
                    "order_type": "market_" + params["side"].lower(),
                    "stop_loss_rate": params["trigger"],
                    **cls._amount_parameter(params),
                }
            )
            .set_price_size_formatter(cls.create_price_size_formatter())
            .set_price_format_keys("rate")
            .set_size_format_keys("amount")
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
            .set_endpoint_generator("/api/ticker")
            .set_parameter_translater(lambda params: {"pair": params["symbol"]})
            .set_response_itemizer(
                lambda resp, data: {
                    "symbol": resp.url.query["pair"],
                    "price": float(data["last"]),
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
            .set_endpoint_generator(lambda params: "/api/order_books")
            .set_parameter_translater(lambda params: {"pair": params["symbol"]})
            .set_response_itemizer(
                lambda resp, data: {
                    "SELL": [
                        OrderbookItem(
                            symbol=resp.url.query["pair"],
                            side="SELL",
                            price=float(d[0]),
                            size=float(d[1]),
                        )
                        for d in data["asks"]
                    ],
                    "BUY": [
                        OrderbookItem(
                            symbol=resp.url.query["pair"],
                            side="BUY",
                            price=float(d[0]),
                            size=float(d[1]),
                        )
                        for d in data["bids"]
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
            .set_endpoint_generator("/api/exchange/orders/opens")
            .set_parameter_translater(lambda params: {})
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "id": str(d["id"]),
                        "symbol": d["pair"],
                        "side": d["order_type"].upper(),
                        "price": float(d["rate"])
                        if d["rate"]
                        else float(d["stop_loss_rate"]),
                        "size": float(d["pending_amount"])
                        if d["pending_amount"]
                        else float(d["pending_market_buy_amount"]),
                        "type": "limit" if d["rate"] else "stop_market",
                        "timestamp": pd.to_datetime(d["created_at"]),
                    }
                    for d in data.get("orders", [])  # success: Falseの場合は空
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
            .set_endpoint_generator("/api/accounts/balance")
            .set_parameter_translater(lambda params: {})
            .set_response_itemizer(
                lambda resp, data: [
                    {
                        "symbol": k,
                        "price": 0.0,
                        "size": float(v),
                        "side": "BUY",
                    }
                    for k, v in data.items()
                    if k not in ["success"] and "_" not in k
                ]
            )
            .get()
        )

    @classmethod
    def _amount_parameter(
        cls,
        params: MarketOrderAPITranslateParametersParameters
        | StopMarketOrderAPITranslateParametersParameters,
    ) -> dict:
        return (
            {"market_buy_amount": params["size"]}
            if params["side"] == "BUY"
            else {"amount": params["size"]}
        )
