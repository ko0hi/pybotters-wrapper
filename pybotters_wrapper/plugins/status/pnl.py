import copy
from collections import deque
from typing import TypedDict

import numpy as np
import pandas as pd

from ...core import DataStoreWrapper
from .._base import Plugin
from ..mixins import WatchStoreMixin


class PnLItem(TypedDict):
    symbol: str
    pnl: float
    realized_pnl: float
    unrealized_pnl: float
    fee: float
    timestamp: pd.Timestamp

class PnL(WatchStoreMixin, Plugin):
    def __init__(
        self, store: DataStoreWrapper, symbol: str, *, fee: float = 0, snapshot_length=9999
    ):
        self._status = PnLItem(
            symbol=symbol,
            pnl=0.0,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            fee=0.0,
            timestamp=pd.Timestamp.now(tz="UTC")
        )
        self._symbol = symbol
        self._fee = fee
        self._snapshots = deque(maxlen=snapshot_length)
        self._buy_size = 0
        self._buy_volume = 0
        self._sell_size = 0
        self._sell_volume = 0
        self._unrealized_volume = 0
        self._last_position = 0
        self.init_watch_store(store.execution)

    def _on_watch(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        if operation == "insert" and data["symbol"] == self._symbol:
            self._snapshots.append(copy.deepcopy(self._status))
            self._update_status(data["side"], data["price"], data["size"], data["timestamp"])


    def status(self, side: str = None) -> PnLItem:
        return self._status

    def _update_status(self, side: str, price: float, size: float, timestamp: pd.Timestamp):
        if side == "BUY":
            self._buy_size += size
            self._buy_volume += price * size
        else:
            self._sell_size += size
            self._sell_volume += price * size

        # 手数料
        fee = self._volume * self._fee

        # 総損益
        realized = self._sell_volume - self._buy_volume
        unrealized = (self._buy_size - self._sell_size) * price
        pnl = realized + unrealized - fee

        # 未実現損益
        # ポジションが0になった or 反転した時点から約定金額を累積する
        if self._position == 0:
            self._unrealized_volume = 0
            unrealized_pnl = 0.0
        else:
            if self._position * self._last_position < 0:  # ポジション反転
                self._unrealized_volume = self._position * price
            else:
                self._unrealized_volume += size * price * (1 if side == "BUY" else -1)
            avg_price = self._unrealized_volume / self._position
            unrealized_pnl = (price - avg_price) * self._position

        # 実現損益
        realized_pnl = pnl + fee - unrealized_pnl

        self._status = PnLItem(
            symbol=self._symbol,
            pnl=pnl,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            fee=fee,
            timestamp=timestamp
        )

        self._last_position = self._position

    @property
    def pnl(self):
        return self._status["pnl"]

    @property
    def _volume(self):
        return self._buy_volume + self._sell_volume

    @property
    def _position(self):
        return self._buy_size - self._sell_size
