from typing import Any, Literal, Type

import pybotters

from pybotters_wrapper.core.typedefs.typing import TDataStoreManager

from .binance.binancecoinm import BinanceCOINMWrapperFactory
from .binance.binanceusdsm import BinanceUSDSMWrapperFactory
from .bitbank import bitbankWrapperFactory
from .bitflyer import bitFlyerWrapperFactory
from .bitget import BitgetWrapperFactory
from .bybit import BybitInverseWrapperFactory, BybitUSDTWrapperFactory
from .coincheck import CoincheckWrapperFactory
from .core import (
    APIWrapper,
    DataStoreWrapper,
    StoreInitializer,
    TWebsocketOnReconnectionCallback,
    TWsHandler,
    WebSocketConnection,
    WebSocketRequestBuilder,
    WrapperFactory,
)
from .gmocoin import GMOCoinWrapperFactory
from .kucoin import KuCoinFuturesWrapperFactory, KuCoinSpotWrapperFactory
from .okx import OKXWrapperFactory
from .phemex import PhemexWrapperFactory
from .sandbox import SandboxAPIWrapper, SandboxDataStoreWrapper, SandboxEngine

_EXCHANGE2FACTORY: dict[str, Type[WrapperFactory]] = {
    "binancecoinm": BinanceCOINMWrapperFactory,
    "binanceusdsm": BinanceUSDSMWrapperFactory,
    "bitbank": bitbankWrapperFactory,
    "bitflyer": bitFlyerWrapperFactory,
    "bitget": BitgetWrapperFactory,
    "bybitinverse": BybitInverseWrapperFactory,
    "bybitusdt": BybitUSDTWrapperFactory,
    "coincheck": CoincheckWrapperFactory,
    "gmocoin": GMOCoinWrapperFactory,
    "kucoinfutures": KuCoinFuturesWrapperFactory,
    "kucoinspot": KuCoinSpotWrapperFactory,
    "okx": OKXWrapperFactory,
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
    sandbox: bool = False,
) -> (
    tuple[DataStoreWrapper, APIWrapper]
    | tuple[SandboxDataStoreWrapper, SandboxAPIWrapper]
):
    if sandbox:
        return create_sandbox(exchange, client, store=store, verbose=verbose)
    else:
        return create_store(exchange, store), create_api(exchange, client, verbose)


def create_sandbox(
    exchange: str,
    client: pybotters.Client,
    *,
    store: TDataStoreManager | None = None,
    verbose: bool = False,
) -> tuple[SandboxDataStoreWrapper, SandboxAPIWrapper]:
    _store, _api = create_store_and_api(exchange, client, store=store, verbose=verbose)
    assert isinstance(_store, DataStoreWrapper)
    assert isinstance(_api, APIWrapper)
    return SandboxEngine.register(_store, _api)


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
