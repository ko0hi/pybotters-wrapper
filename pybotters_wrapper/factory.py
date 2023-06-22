from typing import Any, Literal, Type

import pybotters

from pybotters_wrapper.core.typedefs.typing import TDataStoreManager
from .binance.binancecoinm import BinanceCOINMWrapperFactory
from .binance.binanceusdsm import BinanceUSDSMWrapperFactory
from .bitbank import bitbankWrapperFactory
from .bitflyer import bitFlyerWrapperFactory
from .bybit import BybitInverseWrapperFactory, BybitUSDTWrapperFactory
from .coincheck import CoincheckWrapperFactory
from .core import (
    APIWrapper,
    DataStoreWrapper,
    StoreInitializer,
    TWsHandler,
    TWebsocketOnReconnectionCallback,
    WebSocketConnection,
    WebSocketRequestBuilder,
    WrapperFactory,
)
from .gmocoin import GMOCoinWrapperFactory
from .kucoin import KuCoinFuturesWrapperFactory, KuCoinSpotWrapperFactory
from .phemex import PhemexWrapperFactory

_EXCHANGE2FACTORY: dict[str, Type[WrapperFactory]] = {
    "binancecoinm": BinanceCOINMWrapperFactory,
    "binanceusdsm": BinanceUSDSMWrapperFactory,
    "bitbank": bitbankWrapperFactory,
    "bitflyer": bitFlyerWrapperFactory,
    "bybitinverse": BybitInverseWrapperFactory,
    "bybitusdt": BybitUSDTWrapperFactory,
    "coincheck": CoincheckWrapperFactory,
    "gmocoin": GMOCoinWrapperFactory,
    "kucoinfutures": KuCoinFuturesWrapperFactory,
    "kucoinspot": KuCoinSpotWrapperFactory,
    "phemex": PhemexWrapperFactory,
}


def create_factory(exchange: str) -> Type[WrapperFactory]:
    return _EXCHANGE2FACTORY[exchange]


def create_client(
    apis: dict[str, list[str]] | str | None = None,
    base_url: str = "",
    **kwargs: Any,
) -> pybotters.Client:
    return pybotters.Client(apis, base_url, **kwargs)


def create_api(
    exchange: str, client: pybotters.Client, verbose: bool = False
) -> APIWrapper:
    return _EXCHANGE2FACTORY[exchange].create_api(client, verbose)


def create_store(
    exchange: str, store: TDataStoreManager | None = None
) -> DataStoreWrapper:
    return _EXCHANGE2FACTORY[exchange].create_store(store)


def create_store_and_api(
    exchange: str,
    client: pybotters.Client,
    *,
    store: TDataStoreManager | None = None,
    verbose: bool = False,
) -> tuple[DataStoreWrapper, APIWrapper]:
    return create_store(exchange, store), create_api(exchange, client, verbose)


def create_store_initializer(
    exchange: str, store: TDataStoreManager
) -> StoreInitializer:
    return _EXCHANGE2FACTORY[exchange].create_store_initializer(store)


def create_websocket_request_builder(exchange: str) -> WebSocketRequestBuilder:
    return _EXCHANGE2FACTORY[exchange].create_websocket_request_builder()


def create_websocket_connection(
    endpoint: str,
    send: dict | list[dict] | str,
    hdlr: TWsHandler | list[TWsHandler],
    send_type: Literal["json", "str", "byte"] | None = None,
    hdlr_type: Literal["json", "str", "byte"] | None = None,
) -> WebSocketConnection:
    return WebSocketConnection(endpoint, send, hdlr, send_type, hdlr_type)


async def create_and_connect_websocket_connection(
    client: pybotters.Client,
    endpoint: str,
    send: dict | list[dict] | str,
    hdlr: TWsHandler | list[TWsHandler],
    send_type: Literal["json", "str", "byte"] | None = None,
    hdlr_type: Literal["json", "str", "byte"] | None = None,
    auto_reconnect: bool = False,
    on_reconnection: TWebsocketOnReconnectionCallback | None = None,
    **kwargs,
) -> WebSocketConnection:
    conn = create_websocket_connection(endpoint, send, hdlr, send_type, hdlr_type)
    return await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
