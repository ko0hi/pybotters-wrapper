from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pybotters.store import DataStore

import pandas as pd
import pybotters

from ..core import APIWrapper, DataStoreWrapper
from .market import (
    BinningBook,
    BookTicker,
    TimeBarStreamDataFrame,
    VolumeBarStreamDataFrame,
)
from .periodic import Poller
from .status import PnL
from .watcher import ExecutionWatcher
from .writer import DataStoreWaitCSVWriter, DataStoreWatchCSVWriter


def timebar(
    store: DataStoreWrapper,
    symbol: str,
    *,
    seconds: int,
    maxlen: int = 9999,
    df: pd.DataFrame = None,
    callback: Callable[[pd.DataFrame], dict] | None = None,
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
    callback: Callable[[pd.DataFrame], dict] | None = None,
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
    client_or_api: pybotters.Client | APIWrapper,
    *,
    url: str,
    interval: int | float,
    params: dict | Callable | None = None,
    handler: Callable | None = None,
    history: int = 999,
    method: str = "GET",
) -> Poller:
    return Poller(client_or_api, url, interval, params, handler, history, method)


def pnl(store: DataStoreWrapper, symbol: str, fee: float = 0.0, interval=10) -> PnL:
    return PnL(store, symbol=symbol, fee=fee, interval=interval)


def execution_watcher(
    store: DataStoreWrapper,
    *,
    store_name: str | None = None,
    is_target: Callable[[DataStore, str, dict, dict], bool] | None = None,
) -> ExecutionWatcher:
    return ExecutionWatcher(store, store_name=store_name, is_target=is_target)


def watch_csvwriter(
    store: DataStoreWrapper,
    store_name: str,
    path: str,
    *,
    per_day: bool = False,
    columns: list[str] | None = None,
    flush: bool = False,
    operations: list[str] | None = None,
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
    columns: list[str] | None = None,
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
