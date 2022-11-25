from __future__ import annotations

import importlib
from typing import Callable

import pandas as pd

from pybotters_wrapper.common import DataStoreWrapper
from .market import (
    TimeBarStreamDataFrame,
    VolumeBarStreamDataFrame,
    BinningBook,
    BookTicker,
)
from .watcher import ExecutionWatcher
from .writer import DataStoreWatchCSVWriter, DataStoreWaitCSVWriter, BarCSVWriter
from .market.bar import BarStreamDataFrame

import_cache = {}


def _import_module(store):
    try:
        module_path = f"pybotters_wrapper.{store.exchange}.plugins"
        if module_path in import_cache:
            return import_cache[module_path]
        modu = importlib.import_module(module_path)
        import_cache[module_path] = modu
        return modu
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
        store: DataStoreWrapper,
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
        message_delay=message_delay,
    )


def volumebar(
        store: DataStoreWrapper,
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
        callback=callback,
    )


def binningbook(
        store: DataStoreWrapper,
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
        precision=precision,
    )


def bookticker(store: DataStoreWrapper) -> BookTicker:
    return _import_and_build_plugin(store, "bookticker", default_cls=BookTicker)


def execution_watcher(store: DataStoreWrapper) -> ExecutionWatcher:
    return _import_and_build_plugin(store, "execution", default_cls=ExecutionWatcher)


def watch_csvwriter(
        store: DataStoreWrapper,
        store_name: str,
        path: str,
        *,
        per_day: bool = False,
        columns: list[str] = None,
        operations: list[str] = None,
):
    return _import_and_build_plugin(
        store,
        "datastorewatch_csvwriter",
        default_cls=DataStoreWatchCSVWriter,
        store_name=store_name,
        path=path,
        per_day=per_day,
        columns=columns,
        operations=operations,
    )


def wait_csvwriter(
        store: DataStoreWrapper,
        store_name: str,
        path: str,
        *,
        per_day: bool = False,
        columns: list[str] = None,
):
    return _import_and_build_plugin(
        store,
        "datastorewait_csvwriter",
        default_cls=DataStoreWaitCSVWriter,
        store_name=store_name,
        path=path,
        per_day=per_day,
        columns=columns,
    )


def bar_csvwriter(
        bar: BarStreamDataFrame,
        path: str,
        per_day: bool = False,
):
    # pluginの上のpluginなので取引所別のオーバーライド必要なし
    return BarCSVWriter(bar, path=path, per_day=per_day)
