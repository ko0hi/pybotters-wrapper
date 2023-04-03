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
from pybotters_wrapper.sandbox import SandboxAPI, SandboxDataStoreWrapper, SandboxEngine

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


def create_store_and_api(
    exchange: str,
    client: pybotters.Client,
    *,
    sandbox: bool = False,
    store_kwargs=None,
    api_kwargs=None,
) -> tuple[DataStoreWrapper, API]:
    if sandbox:
        return create_sandbox(exchange, client, store_kwargs, api_kwargs)
    store_kwargs = store_kwargs or {}
    api_kwargs = api_kwargs or {}
    store = create_store(exchange, **store_kwargs)
    api = create_api(exchange, client, **api_kwargs)
    return store, api


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


def create_sandbox(
    exchange: str, client: pybotters.Client, store_kwargs=None, api_kwargs=None
) -> tuple[SandboxDataStoreWrapper, SandboxAPI]:
    store, api = create_store_and_api(
        exchange, client, store_kwargs=store_kwargs, api_kwargs=api_kwargs
    )
    return SandboxEngine.register(store, api)


def get_base_url(exchange: str) -> str:
    return EXCHANGE2API[exchange].BASE_URL


def create_binancespot_store(**kwargs) -> pbw.binance.BinanceSpotDataStoreWrapper:
    return create_store("binancespot", **kwargs)


def create_binanceusdsm_store(**kwargs) -> pbw.binance.BinanceUSDSMDataStoreWrapper:
    return create_store("binanceusdsm", **kwargs)


def create_binanceusdsm_test_store(
    **kwargs,
) -> pbw.binance.BinanceUSDSMTESTDataStoreWrapper:
    return create_store("binanceusdsm_test", **kwargs)


def create_binancecoinm_store(**kwargs) -> pbw.binance.BinanceCOINMDataStoreWrapper:
    return create_store("binancecoinm", **kwargs)


def create_binancecoinm_test_store(
    **kwargs,
) -> pbw.binance.BinanceCOINMTESTDataStoreWrapper:
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


def create_binancespot_store_and_api(
    client: pybotters.Client, *, sandbox: bool = False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.binance.BinanceSpotDataStoreWrapper, pbw.binance.BinanceSpotAPI]:
    return create_store_and_api("binancespot", client, sandbox=sandbox, store_kwargs=store_kwargs, api_kwargs=api_kwargs)


def create_binanceusdsm_store_and_api(
    client: pybotters.Client,  *, sandbox: bool = False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.binance.BinanceUSDSMDataStoreWrapper, pbw.binance.BinanceUSDSMAPI]:
    return create_store_and_api("binanceusdsm", client, sandbox=sandbox, store_kwargs=store_kwargs, api_kwargs=api_kwargs)


def create_binanceusdsm_test_store_and_api(
    client: pybotters.Client,  *, sandbox: bool = False, store_kwargs=None, api_kwargs=None
) -> tuple[
    pbw.binance.BinanceUSDSMTestDataStoreWrapper, pbw.binance.BinanceUSDSMTESTAPI
]:
    return create_store_and_api("binanceusdsm_test", client, sandbox=sandbox, store_kwargs=store_kwargs, api_kwargs=api_kwargs)


def create_binancecoinm_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.binance.BinanceCoinMDataStoreWrapper, pbw.binance.BinanceCOINMAPI]:
    return create_store_and_api("binancecoinm", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_binancecoinm_test_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[
    pbw.binance.BinanceCoinMTESTDataStoreWrapper, pbw.binance.BinanceCOINMTESTAPI
]:
    return create_store_and_api("binancecoinm_test", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_bitbank_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.bitbank.bitbankDataStoreWrapper, pbw.bitbank.bitbankAPI]:
    return create_store_and_api("bitbank", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_bitflyer_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.bitflyer.bitFlyerDataStoreWrapper, pbw.bitflyer.bitFlyerAPI]:
    return create_store_and_api("bitflyer", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_bitget_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.bitget.BitgetDataStoreWrapper, pbw.bitget.BitgetAPI]:
    return create_store_and_api("bitget", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_bybitusdt_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.bybit.BybitUSDTDataStoreWrapper, pbw.bybit.BybitUSDTAPI]:
    return create_store_and_api("bybitusdt", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_bybitinverse_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.bybit.BybitInverseDataStoreWrapper, pbw.bybit.BybitInverseAPI]:
    return create_store_and_api("bybitinverse", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_coincheck_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.coincheck.CoincheckDataStoreWrapper, pbw.coincheck.CoincheckAPI]:
    return create_store_and_api("coincheck", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_gmocoin_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.gmocoin.GMOCoinDataStoreWrapper, pbw.gmocoin.GMOCoinAPI]:
    return create_store_and_api("gmocoin", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_kucoinspot_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.kucoin.KuCoinSpotDataStoreWrapper, pbw.kucoin.KuCoinSpotAPI]:
    return create_store_and_api("kucoinspot", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_kucoinfutures_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.kucoin.KuCoinFuturesDataStoreWrapper, pbw.kucoin.KuCoinFuturesAPI]:
    return create_store_and_api("kucoinfutures", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_okx_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.okx.OKXDataStoreWrapper, pbw.okx.OKXAPI]:
    return create_store_and_api("okx", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)


def create_phemex_store_and_api(
    client: pybotters.Client, *, sandbox=False, store_kwargs=None, api_kwargs=None
) -> tuple[pbw.phemex.PhemexDataStoreWrapper, pbw.phemex.PhemexAPI]:
    return create_store_and_api("phemex", client, sandbox=sandbox, store_kwargs=None, api_kwargs=None)
