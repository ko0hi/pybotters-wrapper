from typing import Type

import pybotters
from pybotters.store import DataStoreManager

import pybotters_wrapper as pbw

from pybotters_wrapper.common import DataStoreManagerWrapper, API
from pybotters_wrapper import plugins

EXCHANGE2STORE = {
    "binance": pbw.binance.BinanceDataStoreManagerWrapper,
    "bitbank": pbw.bitbank.BitbankDataStoreManagerWrapper,
    "bitflyer": pbw.bitflyer.bitFlyerDataStoreManagerWrapper,
    "bitget": pbw.bitget.BitgetDataStoreManagerWrapper,
    "bybit": pbw.bybit.BybitUSDTDataStoreManagerWrapper,
    "coincheck": pbw.coincheck.CoincheckDataStoreManagerWrapper,
    "ftx": pbw.ftx.FTXDataStoreManagerWrapper,
    "gmocoin": pbw.gmocoin.GMOCoinDataStoreManagerWrapper,
    "okx": pbw.okx.OKXDataStoreManagerWrapper,
    "phemex": pbw.phemex.PhemexDataStoreManagerWrapper,
}

EXCHANGE2API: dict[str, Type[API]] = {
    "ftx": pbw.ftx.FTXAPI
}


def create_store(
    exchange: str, *, store: DataStoreManager = None, **kwargs
) -> DataStoreManagerWrapper:
    return EXCHANGE2STORE[exchange](store, **kwargs)


def create_api(exchange: str, client: pybotters.Client, **kwargs) -> API:
    return EXCHANGE2API[exchange](client, **kwargs)


def create_plugin(
        store: DataStoreManagerWrapper, name: str, **kwargs
):
    try:
        factory_fn = getattr(plugins, name)
    except AttributeError:
        raise RuntimeError(f"Unsupported plugin: {name}")
    return factory_fn(store, **kwargs)


def get_base_url(exchange: str) -> str:
    return EXCHANGE2API[exchange].BASE_URL
