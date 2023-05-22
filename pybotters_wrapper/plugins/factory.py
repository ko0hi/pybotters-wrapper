from typing import Callable

import pandas as pd

from .market import (
    BinningBook,
    TimeBarStreamDataFrame,
    VolumeBarStreamDataFrame,
    BookTicker,
)
from .periodic import Poller
from .status import PnL
from .watcher import ExecutionWatcher
from .writer import DataStoreWatchCSVWriter, DataStoreWaitCSVWriter
from ..core import DataStoreWrapper, APIWrapper


def timebar(
    store: DataStoreWrapper,
    symbol: str,
    *,
    seconds: int,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] = None,
    message_delay: int = 2,
) -> TimeBarStreamDataFrame:
    return TimeBarStreamDataFrame(
        store,
        symbol,
        seconds=seconds,
        maxlen=maxlen,
        df=df,
        callback=callback,
        message_delay=message_delay,
    )


def volumebar(
    store: DataStoreWrapper,
    symbol: str,
    *,
    volume_unit: float,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] = None,
) -> VolumeBarStreamDataFrame:
    return VolumeBarStreamDataFrame(
        store,
        symbol,
        volume_unit=volume_unit,
        maxlen=maxlen,
        df=df,
        callback=callback,
    )


def binningbook(
    store: DataStoreWrapper,
    symbol: str,
    *,
    min_bin: int = 0,
    max_bin: int = 10000000,
    pips: int = 1,
    precision: int = 10,
) -> BinningBook:
    return BinningBook(
        store,
        symbol,
        min_bin=min_bin,
        max_bin=max_bin,
        pips=pips,
        precision=precision,
    )


def bookticker(store: DataStoreWrapper, symbol: str) -> BookTicker:
    return BookTicker(store, symbol)


def poller(
    api: APIWrapper,
    *,
    url: str,
    interval: int,
    params: dict | Callable = None,
    handler: Callable = None,
    history: int = 999,
    method: str = "GET",
) -> Poller:
    return Poller(api, url, interval, params, handler, history, method)


def pnl(store: DataStoreWrapper, symbol: str, fee: float = 0.0, interval=10) -> PnL:
    return PnL(store, symbol=symbol, fee=fee, interval=interval)


def execution_watcher(
    store: DataStoreWrapper,
    *,
    store_name: str = None,
    is_target: Callable[["DataStore", str, dict, dict], bool] = None,
) -> ExecutionWatcher:
    return ExecutionWatcher(store, store_name=store_name, is_target=is_target)


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
    return DataStoreWatchCSVWriter(
        store,
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
    return DataStoreWaitCSVWriter(
        store,
        store_name=store_name,
        path=path,
        per_day=per_day,
        columns=columns,
        flush=flush,
    )
