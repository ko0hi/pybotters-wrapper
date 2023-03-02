import copy
from collections import deque
from datetime import datetime

from ...core import DataStoreWrapper
from .._base import Plugin
from ..mixins import WatchStoreMixin


def compute_pnl(
    buy_avg_price: float,
    buy_size: float,
    sell_avg_price: float,
    sell_size: float,
) -> float:
    # 実現損益のみ
    size = min(buy_size, sell_size)
    return sell_avg_price * size - buy_avg_price * size


class PnL(WatchStoreMixin, Plugin):
    def __init__(
        self, store: DataStoreWrapper, symbol: str, *, fee: float = 0, snapshot_length=9999
    ):
        self._status = {
            "symbol": symbol,
            "pnl": 0.0,
            "updated_at": str(datetime.utcnow()),
        }
        self._symbol = symbol
        self._fee = fee
        self._snapshots = deque(maxlen=snapshot_length)
        self._buy_price = 0
        self._buy_size = 0
        self._buy_volume = 0
        self._sell_price = 0
        self._sell_size = 0
        self._sell_volume = 0
        self.init_watch_store(store.execution)

    def _on_watch(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        if operation == "insert" and data["symbol"] == self._symbol:
            self._snapshots.append(copy.deepcopy(self._status))
            self._update_status(data["side"], data["price"], data["size"])

    def status(self, side: str = None) -> dict:
        return self._status

    def _update_status(self, side: str, price: float, size: float):
        if side == "BUY":
            self._buy_price += price
            self._buy_size += size
            self._buy_volume += price * size
        else:
            self._sell_price += price
            self._sell_size += size
            self._sell_volume += price * size

        realized = self._sell_volume - self._buy_volume
        unrealized = (self._buy_size - self._sell_size) * price
        self._status["pnl"] = realized + unrealized - self._volume * self._fee
        self._status["updated_at"] = str(datetime.utcnow())

    @property
    def pnl(self):
        return self._status["pnl"]

    @property
    def _volume(self):
        return self._buy_volume + self._sell_volume

