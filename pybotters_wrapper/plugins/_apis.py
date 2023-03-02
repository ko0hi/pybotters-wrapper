from __future__ import annotations

from typing import Callable

import pandas as pd
import pybotters

from pybotters_wrapper.core import API, DataStoreWrapper
from .influxdb import InfluxDB
from .market import (
    BinningBook,
    BookTicker,
    TimeBarStreamDataFrame,
    VolumeBarStreamDataFrame,
)
from .market.bar import BarStreamDataFrame
from .periodic import Poller
from .status import PnL
from .watcher import ExecutionWatcher
from .writer import (
    BarCSVWriter,
    DataStoreWaitCSVWriter,
    DataStoreWatchCSVWriter,
)


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
    return TimeBarStreamDataFrame(
        store,
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
    return VolumeBarStreamDataFrame(
        store,
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
    return BinningBook(
        store,
        min_bin=min_bin,
        max_bin=max_bin,
        pips=pips,
        precision=precision,
    )


def bookticker(store: DataStoreWrapper) -> BookTicker:
    return BookTicker(store)


def poller(
    api_or_client: pybotters.Client | API,
    *,
    url: str,
    interval: int,
    params: dict | Callable = None,
    handler: Callable = None,
    history: int = 999,
    method: str = "GET",
) -> Poller:
    return Poller(
        api_or_client, url, interval, params, handler, history, method
    )


def execution_watcher(
    store: DataStoreWrapper,
    *,
    store_name: str = None,
    is_target: Callable[["DataStore", str, dict, dict], bool] = None,
) -> ExecutionWatcher:
    return ExecutionWatcher(store, store_name=store_name, is_target=is_target)


def pnl(store: DataStoreWrapper, symbol: str, fee: float = 0.0) -> PnL:
    return PnL(store, symbol=symbol, fee=fee)


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


def bar_csvwriter(
    bar: BarStreamDataFrame,
    path: str,
    per_day: bool = False,
    flush: bool = False,
) -> BarCSVWriter:
    # pluginの上のpluginなので取引所別のオーバーライド必要なし
    return BarCSVWriter(bar, path=path, per_day=per_day, flush=flush)


def influxdb(token: str, org: str, bucket: str, **kwargs) -> InfluxDB:
    return InfluxDB(token, org, bucket, **kwargs)
