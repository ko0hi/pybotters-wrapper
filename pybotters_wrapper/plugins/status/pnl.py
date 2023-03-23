import copy
from collections import deque

import pandas as pd

from ...core import DataStoreWrapper
from .._base import Plugin
from ..mixins import WatchStoreMixin


class PnL(WatchStoreMixin, Plugin):
    def __init__(
        self, store: DataStoreWrapper, symbol: str, *, fee: float = 0, snapshot_length=9999
    ):
        self._status = {
            "symbol": symbol,
            "pnl": 0.0,
            "timestamp": None,
        }
        self._symbol = symbol
        self._fee = fee
        self._snapshots = deque(maxlen=snapshot_length)
        self._buy_size = 0
        self._buy_volume = 0
        self._sell_size = 0
        self._sell_volume = 0
        self.init_watch_store(store.execution)

    def _on_watch(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        if operation == "insert" and data["symbol"] == self._symbol:
            self._snapshots.append(copy.deepcopy(self._status))
            self._update_status(data["side"], data["price"], data["size"], data["timestamp"])

    def status(self, side: str = None) -> dict:
        return self._status

    def _update_status(self, side: str, price: float, size: float, timestamp: pd.Timestamp):
        if side == "BUY":
            self._buy_size += size
            self._buy_volume += price * size
        else:
            self._sell_size += size
            self._sell_volume += price * size

        realized = self._sell_volume - self._buy_volume
        unrealized = (self._buy_size - self._sell_size) * price
        self._status["pnl"] = realized + unrealized - self._volume * self._fee
        self._status["timestamp"] = timestamp

    @property
    def pnl(self):
        return self._status["pnl"]

    @property
    def _volume(self):
        return self._buy_volume + self._sell_volume
