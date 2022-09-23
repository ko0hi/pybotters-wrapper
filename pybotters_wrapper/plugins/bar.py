import asyncio
import numpy as np
import pandas as pd

from pybotters.store import DataStore

from pybotters_wrapper.plugins import WatchPlugin
from pybotters_wrapper.utils import StreamDataFrame



class BarStreamDataFrame(WatchPlugin):
    COLUMNS = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "buy_volume",
        "sell_volume",
    ]

    def __init__(
        self,
        store: DataStore,
        maxlen: int,
        df=None,
        callback=None,
    ):
        super(BarStreamDataFrame, self).__init__(store)

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

        self._init_bar()


    def update(self, d: dict, op: str, **kwargs):
        if self._is_new_bar(d, op, **kwargs):
            self._next_bar(d)
        else:
            self._current_bar(d)

    def _is_new_bar(self, d: dict, op: str, **kwargs) -> bool:
        raise NotImplementedError

    def _next_bar(self, item: dict) -> None:
        self._sdf.append(self._cur_bar)
        self._init_bar(item)

    def _current_bar(self, d: dict) -> None:
        self._cur_bar["timestamp"] = d["timestamp"]
        if self._cur_bar["open"] is None:
            self._cur_bar["open"] = d["price"]
        self._cur_bar["high"] = max(d["price"], self._cur_bar["high"])
        self._cur_bar["low"] = min(d["price"], self._cur_bar["low"])
        self._cur_bar["close"] = d["price"]
        self._cur_bar["volume"] += d["volume"]
        if d["side"] == "BUY":
            self._cur_bar["buy_volume"] += d["volume"]
        elif d["side"] == "SELL":
            self._cur_bar["sell_volume"] += d["volume"]

    def _init_bar(self, d=None) -> None:
        if d is None:
            self._cur_bar = {
                "timestamp": None,
                "open": None,
                "high": -np.inf,
                "low": np.inf,
                "close": None,
                "volume": 0,
                "buy_volume": 0,
                "sell_volume": 0,
            }
        else:
            self._cur_bar = {
                "timestamp": d["timestamp"],
                "open": d["price"],
                "high": d["price"],
                "low": d["price"],
                "close": d["price"],
                "volume": d["volume"],
                "buy_volume": d["volume"] if d["side"] == "BUY" else 0,
                "sell_volume": d["volume"] if d["side"] == "SELL" else 0,
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

    @property
    def open(self):
        return self.df.open.values

    @property
    def high(self):
        return self.df.high.values

    @property
    def low(self):
        return self.df.low.values

    @property
    def close(self):
        return self.df.close.values

    @property
    def volume(self):
        return self.df.volume.values

    @property
    def buy_volume(self):
        return self.df.buy_volume.values

    @property
    def sell_volume(self):
        return self.df.sell_volume.values

    @property
    def cur_bar(self):
        return self._cur_bar

    @property
    def last_bar(self):
        return self._sdf.iloc[-1]

    @property
    def df(self):
        return self._sdf.df


class TimeBarStreamDataFrame(BarStreamDataFrame):
    def __init__(
        self,
        store,
        seconds,
        maxlen=9999,
        df=None,
        callback=None,
        message_delay=2,
    ):
        super(TimeBarStreamDataFrame, self).__init__(
            store, maxlen, df, callback
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

