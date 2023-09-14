import asyncio
import copy
from collections import deque
from typing import TypedDict

import pandas as pd
from pybotters.store import DataStore

from ...core import DataStoreWrapper
from ..base_plugin import Plugin
from ..mixins import WatchStoreMixin


class PnLItem(TypedDict):
    symbol: str
    pnl: float
    realized_pnl: float
    unrealized_pnl: float
    fee: float
    timestamp: pd.Timestamp


class PnL(WatchStoreMixin, Plugin):
    _POSITION_PRECISION = 14

    def __init__(
        self,
        store: DataStoreWrapper,
        symbol: str,
        *,
        fee: float = 0,
        snapshot_length=9999,
        interval=10
    ) -> None:
        self._symbol = symbol
        self._fee = fee
        self._snapshots: deque = deque(maxlen=snapshot_length)
        self._buy_size = 0.0
        self._buy_volume = 0.0
        self._sell_size = 0.0
        self._sell_volume = 0.0
        self.init_watch_store(store.execution)

        # 未実現損益計算用
        self._unrealized_volume = 0.0
        self._last_position = 0.0

        # ltp更新用
        self._ltp = 0.0
        self._timestamp = pd.Timestamp.now(tz="UTC")
        self._store = store
        self._ltp_update_task = asyncio.create_task(self._auto_ltp_update(interval))

    async def _auto_ltp_update(self, interval: int = 10) -> None:
        while True:
            trades = self._store.trades.find()
            if trades:
                t = trades[-1]
                if t["timestamp"] > self._timestamp:
                    self._update_unrealized_pnl(t["price"], t["timestamp"])
            await asyncio.sleep(interval)

    def _on_watch(
        self, store: DataStore, operation: str, source: dict, data: dict
    ) -> None:
        if operation == "insert" and data["symbol"] == self._symbol:
            self._snapshots.append(copy.deepcopy(self.status()))
            self._update_pnl(
                data["side"], data["price"], data["size"], data["timestamp"]
            )

    def status(self) -> PnLItem:
        # 手数料
        fee = self._volume * self._fee

        # 総損益
        realized = self._sell_volume - self._buy_volume
        unrealized = (self._buy_size - self._sell_size) * self._ltp
        pnl = realized + unrealized - fee

        # 未実現損益
        unrealized_pnl = self._unrealized_pnl

        # 実現損益
        realized_pnl = pnl + fee - unrealized_pnl

        return PnLItem(
            symbol=self._symbol,
            pnl=pnl,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            fee=fee,
            timestamp=self._timestamp,
        )

    def _update_unrealized_pnl(self, price: float, timestamp: pd.Timestamp) -> None:
        self._ltp = price
        self._timestamp = timestamp

    def _update_pnl(
        self, side: str, price: float, size: float, timestamp: pd.Timestamp
    ) -> None:
        if side == "BUY":
            self._buy_size += size
            self._buy_volume += price * size
        else:
            self._sell_size += size
            self._sell_volume += price * size

        # ポジションが0になった時点から未実現分の約定金額を累積する
        position_delta = size * (1 if side == "BUY" else -1)
        if abs(self._position) == 0:  # ポジションなし
            self._unrealized_volume = 0
        elif self._last_position * self._position < 0:  # ポジション反転
            self._unrealized_volume = self._position * price
        elif self._last_position * position_delta < 0:  # ポジション一部決済
            self._unrealized_volume = (
                self._unrealized_volume * self._position / self._last_position
            )
        else:  # ポジション積み増し
            self._unrealized_volume += position_delta * price

        self._ltp = price
        self._timestamp = timestamp
        self._last_position = self._position

    @property
    def pnl(self) -> float:
        return self.status()["pnl"]

    @property
    def _volume(self) -> float:
        return self._buy_volume + self._sell_volume

    @property
    def _position(self) -> float:
        return round(self._buy_size - self._sell_size, self._POSITION_PRECISION)

    @property
    def _avg_price(self) -> float:
        if abs(self._position) == 0:
            return 0.0
        else:
            return self._unrealized_volume / self._position

    @property
    def _unrealized_pnl(self) -> float:
        return (self._ltp - self._avg_price) * self._position
