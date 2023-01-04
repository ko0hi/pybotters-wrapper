from __future__ import annotations

import traceback
from typing import Callable, Type

import pybotters
from pybotters.store import DataStoreManager

import pybotters_wrapper as pbw
from pybotters_wrapper import plugins
from pybotters_wrapper.core import API, DataStoreWrapper
from pybotters_wrapper.core.socket import (
    WebsocketChannels,
    WebsocketConnection,
    WsHandler,
)
from pybotters_wrapper.plugins._base import Plugin

EXCHANGE2BASEURL = {
    "binancespot": pbw.binance.BinanceSpotAPI.BASE_URL,
    "binanceusdsm": pbw.binance.BinanceUSDSMAPI.BASE_URL,
    "binanceusdsm_test": pbw.binance.BinanceUSDSMTESTAPI.BASE_URL,
    "binancecoinm": pbw.binance.BinanceCOINMAPI.BASE_URL,
    "binancecoinm_test": pbw.binance.BinanceCOINMTESTAPI.BASE_URL,
    "bitbank": pbw.bitbank.bitbankAPI.BASE_URL,
    "bitflyer": pbw.bitflyer.bitFlyerAPI.BASE_URL,
    "bitget": pbw.bitget.BitgetAPI.BASE_URL,
    "bybitusdt": pbw.bybit.BybitUSDTAPI.BASE_URL,
    "bybitinverse": pbw.bybit.BybitInverseAPI.BASE_URL,
    "coincheck": pbw.coincheck.CoincheckAPI.BASE_URL,
    "gmocoin": pbw.gmocoin.GMOCoinAPI.BASE_URL,
    "kucoinspot": pbw.kucoin.KuCoinSpotAPI.BASE_URL,
    "kucoinfutures": pbw.kucoin.KuCoinFuturesAPI.BASE_URL,
    "okx": pbw.okx.OKXAPI.BASE_URL,
    "phemex": pbw.phemex.PhemexAPI.BASE_URL,
}

EXCHANGE2STORE = {
    "binancespot": pbw.binance.BinanceSpotDataStoreWrapper,
    "binanceusdsm": pbw.binance.BinanceUSDSMDataStoreWrapper,
    "binanceusdsm_test": pbw.binance.BinanceUSDSMTESTDataStoreWrapper,
    "binancecoinm": pbw.binance.BinanceCOINMDataStoreWrapper,
    "binancecoinm_test": pbw.binance.BinanceCOINMTESTDataStoreWrapper,
    "bitbank": pbw.bitbank.bitbankDataStoreWrapper,
    "bitflyer": pbw.bitflyer.bitFlyerDataStoreWrapper,
    "bitget": pbw.bitget.BitgetDataStoreWrapper,
    "bybitusdt": pbw.bybit.BybitUSDTDataStoreWrapper,
    "bybitinverse": pbw.bybit.BybitInverseDataStoreWrapper,
    "coincheck": pbw.coincheck.CoincheckDataStoreWrapper,
    "ftx": pbw.ftx.FTXDataStoreWrapper,
    "gmocoin": pbw.gmocoin.GMOCoinDataStoreWrapper,
    "kucoinspot": pbw.kucoin.KuCoinSpotDataStoreWrapper,
    "kucoinfutures": pbw.kucoin.KuCoinFuturesDataStoreWrapper,
    "okx": pbw.okx.OKXDataStoreWrapper,
    "phemex": pbw.phemex.PhemexDataStoreWrapper,
}

EXCHANGE2API: dict[str, Type[API]] = {
    "binancespot": pbw.binance.BinanceSpotAPI,
    "binanceusdsm": pbw.binance.BinanceUSDSMAPI,
    "binanceusdsm_test": pbw.binance.BinanceUSDSMTESTAPI,
    "binancecoinm": pbw.binance.BinanceCOINMAPI,
    "binancecoinm_test": pbw.binance.BinanceCOINMTESTAPI,
    "bitbank": pbw.bitbank.bitbankAPI,
    "bitget": pbw.bitget.BitgetAPI,
    "bitflyer": pbw.bitflyer.bitFlyerAPI,
    "bybitusdt": pbw.bybit.BybitUSDTAPI,
    "bybitinverse": pbw.bybit.BybitInverseAPI,
    "coincheck": pbw.coincheck.CoincheckAPI,
    "ftx": pbw.ftx.FTXAPI,
    "gmocoin": pbw.gmocoin.GMOCoinAPI,
    "kucoinspot": pbw.kucoin.KuCoinSpotAPI,
    "kucoinfutures": pbw.kucoin.KuCoinFuturesAPI,
    "okx": pbw.okx.OKXAPI,
    "phemex": pbw.phemex.PhemexAPI,
}


def _get_value(exchange, dic):
    if exchange not in dic:
        f = [t for t in traceback.extract_stack() if t.filename.endswith("_apis.py")][0]
        raise RuntimeError(f"Unsupported exchange: {exchange} (`{f.name}()`)")
    return dic[exchange]


def create_client(**kwargs) -> pybotters.Client:
    return pybotters.Client(**kwargs)


def create_store(exchange: str, *, store: DataStoreManager = None) -> DataStoreWrapper:
    return _get_value(exchange, EXCHANGE2STORE)(store)


def create_api(exchange: str, client: pybotters.Client, **kwargs) -> API:
    return _get_value(exchange, EXCHANGE2API)(client, **kwargs)


def create_plugin(store: DataStoreWrapper, name: str, **kwargs) -> Plugin:
    try:
        factory_fn = getattr(plugins, name)
    except AttributeError:
        raise RuntimeError(f"Unsupported plugin: {name}")
    return factory_fn(store, **kwargs)


def create_socket_channels(exchange: str) -> WebsocketChannels:
    return EXCHANGE2STORE[exchange]._WEBSOCKET_CHANNELS()


async def create_ws_connect(
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
) -> WebsocketConnection | list[WebsocketConnection]:
    if endpoint is not None and send is not None:
        return await WebsocketConnection(
            endpoint, send, hdlr=hdlr, send_type=send_type, hdlr_type=hdlr_type
        ).connect(client, auto_reconnect, on_reconnection)
    elif subscribe_list is not None:
        conns = []
        for endpoint, send in subscribe_list.items():
            conn = await create_ws_connect(
                client,
                endpoint=endpoint,
                send=send,
                hdlr=hdlr,
                send_type=send_type,
                hdlr_type=hdlr_type,
                auto_reconnect=auto_reconnect,
                on_reconnection=on_reconnection,
            )
            conns.append(conn)
        return conns
    else:
        raise RuntimeError("Need either of `endpoint` and `send` or `subscribe_list`")


def get_base_url(exchange: str) -> str:
    return EXCHANGE2API[exchange].BASE_URL


def create_binancespot_store(**kwargs) -> pbw.binance.BinanceSpotDataStoreWrapper:
    return create_store("binancespot", **kwargs)


def create_binanceusdsm_store(**kwargs) -> pbw.binance.BinanceUSDSMDataStoreWrapper:
    return create_store("binanceusdsm", **kwargs)


def create_binanceusdsm_test_store(**kwargs) -> pbw.binance.BinanceUSDSMTESTDataStoreWrapper:
    return create_store("binanceusdsm_test", **kwargs)


def create_binancecoinm_store(**kwargs) -> pbw.binance.BinanceCOINMDataStoreWrapper:
    return create_store("binancecoinm", **kwargs)


def create_binancecoinm_test_store(**kwargs) -> pbw.binance.BinanceCOINMTESTDataStoreWrapper:
    return create_store("binancecoinm_test", **kwargs)


def create_bitbank_store(**kwargs) -> pbw.bitbank.bitbankDataStoreWrapper:
    return create_store("bitbank", **kwargs)


def create_bitflyer_store(**kwargs) -> pbw.bitflyer.bitFlyerDataStoreWrapper:
    return create_store("bitflyer", **kwargs)


def create_bitget_store(**kwargs) -> pbw.bitget.BitgetDataStoreWrapper:
    return create_store("bitget", **kwargs)


def create_bybitusdt_store(**kwargs) -> pbw.bybit.BybitUSDTDataStoreWrapper:
    return create_store("bybitusdt", **kwargs)


def create_bybitinverse_store(**kwargs) -> pbw.bybit.BybitInverseDataStoreWrapper:
    return create_store("bybitinverse", **kwargs)


def create_coincheck_store(**kwargs) -> pbw.coincheck.CoincheckDataStoreWrapper:
    return create_store("coincheck", **kwargs)


def create_gmocoin_store(**kwargs) -> pbw.gmocoin.GMOCoinDataStoreWrapper:
    return create_store("gmocoin", **kwargs)


def create_kucoinspot_store(**kwargs) -> pbw.kucoin.KuCoinSpotDataStoreWrapper:
    return create_store("kucoinspot", **kwargs)


def create_kucoinfutures_store(**kwargs) -> pbw.kucoin.KuCoinFuturesDataStoreWrapper:
    return create_store("kucoinfutures", **kwargs)


def create_okx_store(**kwargs) -> pbw.okx.OKXDataStoreWrapper:
    return create_store("okx", **kwargs)


def create_phemex_store(**kwargs) -> pbw.phemex.PhemexDataStoreWrapper:
    return create_store("phemex", **kwargs)


def create_binancespot_api(
    client: pybotters.Client, **kwargs
) -> pbw.binance.BinanceSpotAPI:
    return create_api("binancespot", client, **kwargs)


def create_binanceusdsm_api(
    client: pybotters.Client, **kwargs
) -> pbw.binance.BinanceUSDSMAPI:
    return create_api("binanceusdsm", client, **kwargs)

def create_binanceusdsm_test_api(
    client: pybotters.Client, **kwargs
) -> pbw.binance.BinanceUSDSMTESTAPI:
    return create_api("binanceusdsm_test", client, **kwargs)


def create_binancecoinm_api(
    client: pybotters.Client, **kwargs
) -> pbw.binance.BinanceCOINMAPI:
    return create_api("binancecoinm", client, **kwargs)


def create_binancecoinm_test_api(
    client: pybotters.Client, **kwargs
) -> pbw.binance.BinanceCOINMTESTAPI:
    return create_api("binancecoinm_test", client, **kwargs)


def create_bitbank_api(client: pybotters.Client, **kwargs) -> pbw.bitbank.bitbankAPI:
    return create_api("bitbank", client, **kwargs)


def create_bitflyer_api(client: pybotters.Client, **kwargs) -> pbw.bitflyer.bitFlyerAPI:
    return create_api("bitflyer", client, **kwargs)


def create_bitget_api(client: pybotters.Client, **kwargs) -> pbw.bitget.BitgetAPI:
    return create_api("bitget", client, **kwargs)


def create_bybitusdt_api(client: pybotters.Client, **kwargs) -> pbw.bybit.BybitUSDTAPI:
    return create_api("bybitusdt", client, **kwargs)


def create_bybitinverse_api(
    client: pybotters.Client, **kwargs
) -> pbw.bybit.BybitInverseAPI:
    return create_api("bybitinverse", client, **kwargs)


def create_coincheck_api(
    client: pybotters.Client, **kwargs
) -> pbw.coincheck.CoincheckAPI:
    return create_api("coincheck", client, **kwargs)


def create_gmocoin_api(client: pybotters.Client, **kwargs) -> pbw.gmocoin.GMOCoinAPI:
    return create_api("gmocoin", client, **kwargs)


def create_kucoinspot_api(
    client: pybotters.Client, **kwargs
) -> pbw.kucoin.KuCoinSpotAPI:
    return create_api("kucoinspot", client, **kwargs)


def create_kucoinfutures_api(
    client: pybotters.Client, **kwargs
) -> pbw.kucoin.KuCoinFuturesAPI:
    return create_api("kucoinfutures", client, **kwargs)


def create_okx_api(client: pybotters.Client, **kwargs) -> pbw.okx.OKXAPI:
    return create_api("okx", client, **kwargs)


def create_phemex_api(client: pybotters.Client, **kwargs) -> pbw.phemex.PhemexAPI:
    return create_api("phemex", client, **kwargs)
