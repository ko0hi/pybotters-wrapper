from __future__ import annotations

import asyncio
from typing import Callable

import numpy as np
import pandas as pd

from .._base import Plugin
from ..mixins import WatchStoreMixin, PublishQueueMixin
from ...utils import StreamDataFrame


class BarStreamDataFrame(WatchStoreMixin, PublishQueueMixin, Plugin):
    COLUMNS = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "size",
        "buy_size",
        "sell_size",
    ]

    def __init__(
            self,
            store: 'DataStoreManagerWrapper',
            *,
            maxlen: int = 9999,
            df: pd.DataFrame = None,
            callback: Callable[[pd.DataFrame], any] = None,
    ):
        if df is not None:
            if len(df.columns) == 7 and df.index.name == "timestamp":
                df = df.reset_index()
            assert len(df.columns) == len(self.COLUMNS)

        self._sdf = StreamDataFrame(
            maxlen,
            self.COLUMNS,
            df,
            callback,
            dtypes={c: float for c in self.COLUMNS if c != "timestamp"},
        )

        self._cur_bar = None

        self.init_watch_store(store.trades)
        self.init_publish_queue()

        self._init_bar()

    def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        if operation == "insert":
            if self._is_new_bar(data, operation):
                self._next_bar(data)
            else:
                self._current_bar(data)

    def _is_new_bar(self, d: dict, op: str, **kwargs) -> bool:
        raise NotImplementedError

    def _next_bar(self, item: dict) -> None:
        self._sdf.append(self._cur_bar)
        self._init_bar(item)
        self.put(self.df)

    def _current_bar(self, d: dict) -> None:
        self._cur_bar["timestamp"] = d["timestamp"]
        if self._cur_bar["open"] is None:
            self._cur_bar["open"] = d["price"]
        self._cur_bar["high"] = max(d["price"], self._cur_bar["high"])
        self._cur_bar["low"] = min(d["price"], self._cur_bar["low"])
        self._cur_bar["close"] = d["price"]
        self._cur_bar["size"] += d["size"]
        if d["side"] == "BUY":
            self._cur_bar["buy_size"] += d["size"]
        elif d["side"] == "SELL":
            self._cur_bar["sell_size"] += d["size"]

    def _init_bar(self, d=None) -> None:
        if d is None:
            self._cur_bar = {
                "timestamp": None,
                "open": None,
                "high": -np.inf,
                "low": np.inf,
                "close": None,
                "size": 0,
                "buy_size": 0,
                "sell_size": 0,
            }
        else:
            self._cur_bar = {
                "timestamp": d["timestamp"],
                "open": d["price"],
                "high": d["price"],
                "low": d["price"],
                "close": d["price"],
                "size": d["size"],
                "buy_size": d["size"] if d["side"] == "BUY" else 0,
                "sell_size": d["size"] if d["side"] == "SELL" else 0,
            }

    def get_full_df(self) -> pd.DataFrame:
        """未確定足込みのDataFrameを返す。TODO: copyしない。"""

        lhs = self.df
        if self._cur_bar["timestamp"] is None:
            return lhs
        else:
            rhs = pd.DataFrame(self.cur_bar, index=[-1])
            return pd.concat([lhs, rhs], ignore_index=True)

    def latest(self, col):
        value = self._cur_bar[col]
        if value is None or value == 0:
            value = self.df[col].values[-1]
        return value

    def remaining_time(self):
        raise NotImplementedError

    async def wait(self):
        return await self._queue.get()

    @property
    def open(self) -> np.ndarray:
        return self.df["open"].values

    @property
    def high(self) -> np.ndarray:
        return self.df["high"].values

    @property
    def low(self) -> np.ndarray:
        return self.df["low"].values

    @property
    def close(self) -> np.ndarray:
        return self.df["close"].values

    @property
    def size(self) -> np.ndarray:
        return self.df["size"].values

    @property
    def buy_size(self) -> np.ndarray:
        return self.df["buy_size"].values

    @property
    def sell_size(self) -> np.ndarray:
        return self.df["sell_size"].values

    @property
    def cur_bar(self):
        return self._cur_bar

    @property
    def last_bar(self):
        return self._sdf.iloc[-1]

    @property
    def df(self):
        return self._sdf.df

    @property
    def _(self):
        return self._sdf._


class TimeBarStreamDataFrame(BarStreamDataFrame):
    def __init__(
            self,
            store: 'DataStoreManagerWrapper',
            *,
            seconds: int,
            maxlen: int = 9999,
            df: pd.DataFrame = None,
            callback: Callable[[pd.DataFrame], any] = None,
            message_delay: int = 2,
    ):
        super(TimeBarStreamDataFrame, self).__init__(
            store,
            maxlen=maxlen,
            df=df,
            callback=callback,
        )
        self._seconds = seconds
        self._rule = f"{self._seconds}S"
        self._message_delay = message_delay
        self._auto_next_task = asyncio.create_task(self.__auto_next())

    def _is_new_bar(self, d: dict, op: str, **kwargs) -> bool:
        if self._cur_bar["timestamp"] is None:
            return False
        else:
            last_ts = self._cur_bar["timestamp"].floor(self._rule)
            cur_ts = d["timestamp"].floor(self._rule)
            return last_ts != cur_ts

    def _next_bar(self, item=None):
        self._cur_bar["timestamp"] = self._cur_bar["timestamp"].floor(self._rule)
        super()._next_bar(item)

    async def __auto_next(self):
        while True:
            if self._cur_bar["timestamp"] is None:
                pass
            else:
                # onmessageだけだと約定がくるまで更新されないので、最終約定から`_message_delay`秒経過した時点で
                # チェックを行う。`_message_delay`以上遅延があった場合、同時刻キャンドルが複数作られる可能性あり。
                now = pd.Timestamp.utcnow()
                delta = now - self._cur_bar["timestamp"]
                if delta.total_seconds() > self._message_delay:
                    lhs = now.floor(self._rule)
                    rhs = self._cur_bar["timestamp"].floor(self._rule)
                    if lhs != rhs:
                        self._next_bar()
            await asyncio.sleep(1)

    @property
    def remain_seconds(self):
        n = pd.Timestamp.utcnow()
        return (n.ceil(f"{self._seconds}S") - n).total_seconds()

    def remaining_time(self):
        return 1 - (self.remain_seconds / self._seconds)


class VolumeBarStreamDataFrame(BarStreamDataFrame):
    def __init__(
            self,
            store: 'DataStoreManagerWrapper',
            *,
            volume_unit: float,
            maxlen: int = 9999,
            df: pd.DataFrame = None,
            callback: Callable[[pd.DataFrame], any] = None,
    ):
        super(VolumeBarStreamDataFrame, self).__init__(
            store,
            maxlen=maxlen,
            df=df,
            callback=callback,
        )
        self._volume_unit = volume_unit

    def _is_new_bar(self, d: dict, op: str, **kwargs) -> bool:
        return self._cur_bar["size"] > self._volume_unit
