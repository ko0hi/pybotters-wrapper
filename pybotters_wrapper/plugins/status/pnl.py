import copy
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING

from ...core import DataStoreWrapper
from .._base import DataStorePlugin


def compute_pnl(
    buy_avg_price: float, buy_size: float, sell_avg_price: float, sell_size: float
) -> float:
    # 実現損益のみ
    size = min(buy_size, sell_size)
    return sell_avg_price * size - buy_avg_price * size


class PnL(DataStorePlugin):
    def __init__(self, store: DataStoreWrapper, symbol: str, *, snapshot_length=9999):
        super(PnL, self).__init__(store.execution)
        self._status = {
            "symbol": symbol,
            "BUY_price": 0,
            "BUY_size": 0,
            "SELL_price": 0,
            "SELL_size": 0,
            "pnl": 0.0,
            "updated_at": str(datetime.utcnow()),
        }
        self._symbol = symbol
        self._snapshots = deque(maxlen=snapshot_length)

    def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        if operation == "insert" and data["symbol"] == self._symbol:
            self._snapshots.append(copy.deepcopy(self._status))
            self._update_status(data["side"], data["price"], data["size"])

    def status(self, side: str = None) -> dict:
        return self._status if side is None else self._status[side]

    def _update_status(self, side: str, price: float, size: float):
        old_price = self._status[f"{side}_price"]
        old_size = self._status[f"{side}_size"]
        new_size = old_size + size
        new_price = (old_price * old_size + price * size) / new_size
        self._status[f"{side}_price"] = new_price
        self._status[f"{side}_size"] = new_size
        self._status["pnl"] = compute_pnl(
            self._status["BUY_price"],
            self._status["BUY_size"],
            self._status["SELL_price"],
            self._status["SELL_size"],
        )
        self._status["updated_at"] = str(datetime.utcnow())

    @property
    def pnl(self):
        return self._status["pnl"]
