import asyncio
from typing import Callable, Type, TypeVar

import pybotters
from pybotters.store import DataStoreManager

import pybotters_wrapper as pbw

from pybotters_wrapper.common import DataStoreWrapper, API
from pybotters_wrapper.common.socket import WsHandler, WebsocketChannels
from pybotters_wrapper import plugins


TWebsocketChannels = TypeVar("TWebsocketChannels", bound=WebsocketChannels)


EXCHANGE2STORE = {
    "binancespot": pbw.binance.BinanceSpotDataStoreWrapper,
    "binanceusdsm": pbw.binance.BinanceUSDSMDataStoreWrapper,
    "bianancecoinm": pbw.binance.BinanceCOINMDataStoreWrapper,
    "bitbank": pbw.bitbank.BitbankDataStoreWrapper,
    "bitflyer": pbw.bitflyer.bitFlyerDataStoreWrapper,
    "bitget": pbw.bitget.BitgetDataStoreWrapper,
    "bybit": pbw.bybit.BybitUSDTDataStoreWrapper,
    "coincheck": pbw.coincheck.CoincheckDataStoreWrapper,
    "ftx": pbw.ftx.FTXDataStoreWrapper,
    "gmocoin": pbw.gmocoin.GMOCoinDataStoreWrapper,
    "okx": pbw.okx.OKXDataStoreWrapper,
    "phemex": pbw.phemex.PhemexDataStoreWrapper,
}


EXCHANGE2API: dict[str, Type[API]] = {"ftx": pbw.ftx.FTXAPI}


def create_store(
    exchange: str, *, store: DataStoreManager = None, **kwargs
) -> DataStoreWrapper:
    return EXCHANGE2STORE[exchange](store, **kwargs)


def create_api(exchange: str, client: pybotters.Client, **kwargs) -> API:
    return EXCHANGE2API[exchange](client, **kwargs)


def create_plugin(store: DataStoreWrapper, name: str, **kwargs):
    try:
        factory_fn = getattr(plugins, name)
    except AttributeError:
        raise RuntimeError(f"Unsupported plugin: {name}")
    return factory_fn(store, **kwargs)


def create_socket_channels(exchange: str) -> TWebsocketChannels:
    return EXCHANGE2STORE[exchange]._SOCKET_CHANNELS_CLS()


def create_ws_connect(
    client: pybotters.Client,
    *,
    endpoint: str = None,
    send: any = None,
    hdlr: WsHandler = None,
    subscribe_list: dict[str, list[str]] = None,
    send_type: str = "json",
    hdlr_type: str = "json",
    auto_reconnect: bool = False,
    on_reconnection: Callable = None,
):
    if endpoint is not None and send is not None:
        return pbw.common.WebsocketConnection(
            endpoint, send, hdlr=hdlr, send_type=send_type, hdlr_type=hdlr_type
        ).connect(client, auto_reconnect, on_reconnection)
    elif subscribe_list is not None:
        conns = []
        for endpoint, send in subscribe_list.items():
            conn = create_ws_connect(
                client,
                endpoint=endpoint,
                send=send,
                hdlr=hdlr,
                send_type=send_type,
                hdlr_type=hdlr_type,
                auto_reconnect=auto_reconnect,
                on_reconnection=on_reconnection
            )
            conns.append(asyncio.create_task(conn))
        return conns
    else:
        raise RuntimeError(f"Need either of `endpoint` and `send` or `subscribe_list`")


def get_base_url(exchange: str) -> str:
    return EXCHANGE2API[exchange].BASE_URL
