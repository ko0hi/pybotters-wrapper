from typing import Callable

import importlib

import pandas as pd

from ._base import DataStorePlugin, MultipleDataStoresPlugin
from .bar import TimeBarStreamDataFrame, VolumeBarStreamDataFrame
from .binning_book import BinningBook
from .book_ticker import BookTicker
from .execution_watcher import ExecutionWatcher

from pybotters_wrapper.common import DataStoreManagerWrapper


def _import_module(store):
    try:
        module_path = f"pybotters_wrapper.{store.exchange}.plugins"
        return importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise RuntimeError(f"no plugins module for {store.exchange}")


def _build_plugin(store, module, name, **kwargs):

    try:
        return getattr(module, name)(store, **kwargs)
    except AttributeError:
        raise RuntimeError(
            f"'{name}' plugin has not been supported yet for {store.exchange}"
        )


def _import_and_build_plugin(store, name, *, default_cls=None, **kwargs):
    try:
        # 取引所別のfactory methodがあればそちらを呼び出す
        module = _import_module(store)
        return _build_plugin(store, module, name, **kwargs)
    except RuntimeError as e:
        if default_cls is not None:
            return default_cls(store, **kwargs)
        else:
            raise e


def timebar(
    store: DataStoreManagerWrapper,
    *,
    seconds: int,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] = None,
    message_delay: int = 2,
) -> TimeBarStreamDataFrame:
    return _import_and_build_plugin(
        store,
        "timebar",
        default_cls=TimeBarStreamDataFrame,
        seconds=seconds,
        maxlen=maxlen,
        df=df,
        callback=callback,
        message_delay=message_delay
    )


def volumebar(
    store: DataStoreManagerWrapper,
    *,
    volume_unit: float,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] = None,
):
    return _import_and_build_plugin(
        store,
        "volumebar",
        default_cls=VolumeBarStreamDataFrame,
        volume_unit=volume_unit,
        maxlen=maxlen,
        df=df,
        callback=callback
    )


def binningbook(
    store: DataStoreManagerWrapper,
    *,
    min_bin: int = 0,
    max_bin: int = 10000000,
    pips: int = 1,
    precision: int = 10,
) -> BinningBook:
    return _import_and_build_plugin(
        store,
        "binningbook",
        default_cls=BinningBook,
        min_bin=min_bin,
        max_bin=max_bin,
        pips=pips,
        precision=precision
    )


def bookticker(store: DataStoreManagerWrapper) -> BookTicker:
    return _import_and_build_plugin(store, "bookticker", default_cls=BookTicker)


def execution_watcher(store: DataStoreManagerWrapper) -> ExecutionWatcher:
    return _import_and_build_plugin(store, "execution", default_cls=ExecutionWatcher)
