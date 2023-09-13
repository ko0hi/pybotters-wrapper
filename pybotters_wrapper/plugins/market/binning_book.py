from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters.store import DataStore

import numpy as np
import pybotters
from pybotters.store import DataStore

from ...core import DataStoreWrapper, OrderbookStore
from ...utils import BinBucket
from ..base_plugin import Plugin
from ..mixins import WatchStoreMixin


class BinningBook(WatchStoreMixin, Plugin):
    watch_store: OrderbookStore

    def __init__(
        self,
        store: DataStoreWrapper,
        symbol: str,
        *,
        min_bin: int,
        max_bin: int,
        pips: int = 1,
        precision: int = 10,
    ):
        self._symbol = symbol
        self._buckets: dict[str, BinBucket] = {
            "SELL": BinBucket(min_bin, max_bin, pips, precision),
            "BUY": BinBucket(min_bin, max_bin, pips, precision),
        }
        self._mid = None
        self.init_watch_store(store.orderbook)

    def _on_watch(self, store: DataStore, operation: str, source: dict, data: dict):
        if data["symbol"] == self._symbol:
            if operation in ("insert", "update"):
                self._insert(data["side"], data["price"], data["size"])
            elif operation == "delete":
                self._delete(data["side"], data["price"], data["size"])

    def _insert(self, side: str, price: float, size: float):
        self._buckets[side].insert(price, size)  # type: ignore

    def _delete(self, side: str, price: float, size: float):
        self._buckets[side].delete(price, size)  # type: ignore

    def asks(
        self,
        n: int = 100,
        *,
        lower: int | None = None,
        upper: int | None = None,
        non_zero_only: bool = True,
    ):
        if lower is not None:
            begin = self.ask_bucket.bucketize(lower)
        else:
            begin = self._find_best_ask()

        lhs = begin

        if upper:
            rhs = self.ask_bucket.bucketize(upper + self.ask_bucket.pips)
        else:
            rhs = lhs + n

        return self._make_returns(self.ask_bucket, lhs, rhs, non_zero_only)

    def bids(self, n=100, *, lower=None, upper=None, non_zero_only=True):
        if upper is not None:
            begin = self.bid_bucket.bucketize(upper)
        else:
            begin = self._find_best_bid()

        rhs = begin + 1
        if lower:
            lhs = self.bid_bucket.bucketize(lower)
        else:
            lhs = max(0, rhs - n)

        return self._make_returns(self.bid_bucket, lhs, rhs, non_zero_only, True)

    def set_mid(self, mid):
        if isinstance(mid, list):
            raise RuntimeError
        self._mid = mid

    def reset(self):
        self.ask_bucket.reset()
        self.bid_bucket.reset()

    def _find_best_ask(self):
        start = self.ask_bucket.bucketize(self._mid) if self._mid else 0
        n = self.ask_bucket.size()
        for i in range(start, n):
            if self.ask_bucket.get(i) > 0:
                return i
        return n - 1

    def _find_best_bid(self):
        start = (
            self.bid_bucket.bucketize(self._mid)
            if self._mid
            else self.bid_bucket.size() - 1
        )
        for i in range(start, 0, -1):
            if self.bid_bucket.get(i) > 0:
                return i
        return 0

    def bucket(self, side):
        return self._buckets[side]

    @property
    def mid(self):
        return self._mid

    @property
    def mid_bucket(self):
        return self.ask_bucket.bucketize(self.mid)

    @property
    def ask_bucket(self):
        return self._buckets["SELL"]

    @property
    def bid_bucket(self):
        return self._buckets["BUY"]

    @classmethod
    def _make_returns(
        cls,
        bucket: BinBucket,
        lhs: int,
        rhs: int,
        non_zero_only: bool = True,
        is_bid: bool = False,
    ) -> tuple[np.ndarray, np.ndarray]:
        prices = bucket.keys()[lhs:rhs]
        sizes = bucket.values()[lhs:rhs]
        if non_zero_only:
            indices = np.where(sizes > 0)
            prices, sizes = prices[indices], sizes[indices]

        if is_bid:
            prices, sizes = prices[::-1], sizes[::-1]

        return prices, sizes

    async def initialize(self, client: pybotters.Client, **kwargs):
        raise NotImplementedError
