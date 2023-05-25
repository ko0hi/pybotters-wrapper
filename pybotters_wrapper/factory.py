from typing import Literal

import pybotters

from pybotters_wrapper.core.typedefs.typing import TDataStoreManager
from .binance.binancecoinm import BinanceCOINMWrapperFactory
from .binance.binanceusdsm import BinanceUSDSMWrapperFactory
from .bitflyer import bitFlyerWrapperFactory
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
from .phemex import PhemexWrapperFactory

_EXCHANGE2FACTORY: dict[str, WrapperFactory] = {
    "binancecoinm": BinanceCOINMWrapperFactory,
    "binanceusdsm": BinanceUSDSMWrapperFactory,
    "bitflyer": bitFlyerWrapperFactory,
    "phemex": PhemexWrapperFactory,
}


def create_factory(exchange: str) -> WrapperFactory:
    return _EXCHANGE2FACTORY[exchange]


def create_client(
    apis: dict[str, list[str]] | str | None = None,
    base_url: str = "",
    **kwargs: any,
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
    send_type: Literal["json", "str", "byte"] = "json",
    hdlr_type: Literal["json", "str", "byte"] = "json",
) -> WebSocketConnection:
    return WebSocketConnection(endpoint, send, hdlr, send_type, hdlr_type)


async def create_and_connect_websocket_connection(
    client: pybotters.Client,
    endpoint: str,
    send: dict | list[dict] | str,
    hdlr: TWsHandler | list[TWsHandler],
    send_type: Literal["json", "str", "byte"] = "json",
    hdlr_type: Literal["json", "str", "byte"] = "json",
    auto_reconnect: bool = False,
    on_reconnection: TWebsocketOnReconnectionCallback | None = None,
    **kwargs,
) -> WebSocketConnection:
    conn = create_websocket_connection(endpoint, send, hdlr, send_type, hdlr_type)
    return await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
