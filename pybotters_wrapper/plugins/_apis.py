from __future__ import annotations

import importlib
import types
from typing import Callable, Type

import pandas as pd
from pybotters_wrapper.core import DataStoreWrapper

from ._base import Plugin
from .market import (
    BinningBook,
    BookTicker,
    TimeBarStreamDataFrame,
    VolumeBarStreamDataFrame,
)
from .market.bar import BarStreamDataFrame
from .status import PnL
from .watcher import ExecutionWatcher
from .writer import BarCSVWriter, DataStoreWaitCSVWriter, DataStoreWatchCSVWriter

import_cache = {}


def _import_module(store: DataStoreWrapper) -> types.ModuleType:
    """取引所固有のプラグインのmoduleを読み込む。読み込んだものはキャッシュする。"""
    try:
        module_path = f"pybotters_wrapper.{store.package}.plugins.{store.exchange}"
        if module_path in import_cache:
            return import_cache[module_path]
        module = importlib.import_module(module_path)
        import_cache[module_path] = module
        return module
    except ModuleNotFoundError:
        raise RuntimeError(f"no plugins module for {store.exchange}")


def _build_plugin(
    store: DataStoreWrapper, module: types.ModuleType, name: str, **kwargs
) -> Plugin:
    """取引所固有のプラグイン実装をインスタンス化する"""
    try:
        return getattr(module, name)(store, **kwargs)
    except AttributeError:
        raise RuntimeError(
            f"'{name}' plugin has not been supported yet for {store.exchange}"
        )


def _maybe_override_by_exchange(
    store: DataStoreWrapper, plugin_class: Type[Plugin], **kwargs
) -> Plugin:
    """取引所別の実装クラスがあればそちらを呼び出す。取引所別の実装は同名クラスが
    "pybotters_wrapper/${package}/plugins/${exchange}/__init__.pyで定義されている想定
    """
    try:
        module = _import_module(store)
        return _build_plugin(store, module, plugin_class.__name__, **kwargs)
    except RuntimeError:
        return plugin_class(store, **kwargs)  # noqa


# pluginのファクトリーメソッド
def timebar(
    store: DataStoreWrapper,
    *,
    seconds: int,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] = None,
    message_delay: int = 2,
) -> TimeBarStreamDataFrame:
    return _maybe_override_by_exchange(
        store,
        TimeBarStreamDataFrame,
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
) -> VolumeBarStreamDataFrame:
    return _maybe_override_by_exchange(
        store,
        VolumeBarStreamDataFrame,
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
    return _maybe_override_by_exchange(
        store,
        BinningBook,
        min_bin=min_bin,
        max_bin=max_bin,
        pips=pips,
        precision=precision,
    )


def bookticker(store: DataStoreWrapper) -> BookTicker:
    return _maybe_override_by_exchange(store, BookTicker)


def execution_watcher(
    store: DataStoreWrapper,
    *,
    store_name: str = None,
    is_target: Callable[["DataStore", str, dict, dict], bool] = None,
) -> ExecutionWatcher:
    return _maybe_override_by_exchange(
        store, ExecutionWatcher, store_name=store_name, is_target=is_target
    )


def pnl(store: DataStoreWrapper, symbol: str) -> PnL:
    return _maybe_override_by_exchange(store, PnL, symbol=symbol)


def watch_csvwriter(
    store: DataStoreWrapper,
    store_name: str,
    path: str,
    *,
    per_day: bool = False,
    columns: list[str] = None,
    flush: bool = False,
    operations: list[str] = None,
) -> DataStoreWatchCSVWriter:
    return _maybe_override_by_exchange(
        store,
        DataStoreWatchCSVWriter,
        store_name=store_name,
        path=path,
        per_day=per_day,
        columns=columns,
        flush=flush,
        operations=operations,
    )


def wait_csvwriter(
    store: DataStoreWrapper,
    store_name: str,
    path: str,
    *,
    per_day: bool = False,
    columns: list[str] = None,
    flush: bool = False,
) -> DataStoreWaitCSVWriter:
    return _maybe_override_by_exchange(
        store,
        DataStoreWaitCSVWriter,
        store_name=store_name,
        path=path,
        per_day=per_day,
        columns=columns,
        flush=flush,
    )


def bar_csvwriter(
    bar: BarStreamDataFrame, path: str, per_day: bool = False, flush: bool = False
) -> BarCSVWriter:
    # pluginの上のpluginなので取引所別のオーバーライド必要なし
    return BarCSVWriter(bar, path=path, per_day=per_day, flush=flush)
