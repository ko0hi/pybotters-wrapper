from typing import Type

import pybotters
from pybotters.store import DataStoreManager

import pybotters_wrapper as pbw

from pybotters_wrapper.common import DataStoreWrapper, API
from pybotters_wrapper import plugins

EXCHANGE2STORE = {
    "binance": pbw.binance.BinanceDataStoreWrapper,
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

EXCHANGE2API: dict[str, Type[API]] = {
    "ftx": pbw.ftx.FTXAPI
}


def create_store(
    exchange: str, *, store: DataStoreManager = None, **kwargs
) -> DataStoreWrapper:
    return EXCHANGE2STORE[exchange](store, **kwargs)


def create_api(exchange: str, client: pybotters.Client, **kwargs) -> API:
    return EXCHANGE2API[exchange](client, **kwargs)


def create_plugin(
        store: DataStoreWrapper, name: str, **kwargs
):
    try:
        factory_fn = getattr(plugins, name)
    except AttributeError:
        raise RuntimeError(f"Unsupported plugin: {name}")
    return factory_fn(store, **kwargs)


def get_base_url(exchange: str) -> str:
    return EXCHANGE2API[exchange].BASE_URL
