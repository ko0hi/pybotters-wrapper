from typing import Generic, TypeVar

import asyncio
import numpy as np

import pybotters

from pybotters_wrapper import Bucket
from pybotters_wrapper.common import DataStoreWrapper


T = TypeVar('T', bound=DataStoreWrapper)


class PybottersBook(Generic[T]):
    SOCKET_ENDPOINT = None

    def __init__(
        self,
        store: T,
        min_key: int,
        max_key: int,
        pips: int = 1,
        precision: int = 10,
    ):
        self._buckets: dict[Bucket] = {
            "ask": Bucket(min_key, max_key, pips, precision),
            "bid": Bucket(min_key, max_key, pips, precision),
        }
        self._store = store
        self._mid = None
        self._ws = None
        self._auto_update_task = None

    def update(self, op, side, price, size):
        if op == "insert":
            self._insert(side, price, size)
        elif op == "delete":
            self._delete(side, price, size)
        elif op == "update":
            self._update(side, price, size)

    def _insert(self, side: str, price, size):
        self._buckets[side].insert(price, size)

    def _delete(self, side, price, size):
        self._buckets[side].delete(price, size)

    def _update(self, side, price, size):
        self._buckets[side].insert(price, size)

    def asks(self, n=100, *, lower=None, upper=None, non_zero_only=True):
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
        self._mid = mid

    def reset(self):
        self.ask_bucket.reset()
        self.bid_bucket.reset()

    def _find_best_ask(self):
        start = self.ask_bucket.bucketize(self._mid) if self._mid else 0
        for i in range(start, self.ask_bucket.size()):
            if self.ask_bucket.get(i) > 0:
                return i

    def _find_best_bid(self):
        start = (
            self.bid_bucket.bucketize(self._mid)
            if self._mid
            else self.bid_bucket.size() - 1
        )
        for i in range(start, 0, -1):
            if self.bid_bucket.get(i) > 0:
                return i

    def bucket(self, side):
        return self._buckets[side]

    @property
    def store(self) -> T:
        return self._store

    @property
    def mid(self):
        return self._mid

    @property
    def mid_bucket(self):
        return self.ask_bucket.bucketize(self.mid)

    @property
    def ask_bucket(self):
        return self._buckets["ask"]

    @property
    def bid_bucket(self):
        return self._buckets["bid"]

    @classmethod
    def _make_returns(cls, bucket: Bucket, lhs, rhs, non_zero_only=True, is_bid=False):
        prices = bucket.keys()[lhs:rhs]
        sizes = bucket.values()[lhs:rhs]
        if non_zero_only:
            indices = np.where(sizes > 0)
            prices, sizes = prices[indices], sizes[indices]

        if is_bid:
            prices, sizes = prices[::-1], sizes[::-1]

        return prices, sizes

    async def _auto_update_impl(self):
        raise NotImplementedError

    async def _initialize_impl(self, client: pybotters.Client, **kwargs):
        raise NotImplementedError

    async def _ws_connect_impl(
        self, client: pybotters.Client, **kwargs
    ) -> "pybotters.ws.WebSocketRunner":
        raise NotImplementedError

    async def _auto_update(self):
        self._auto_update_task = asyncio.create_task(self._auto_update_impl())

    async def initialize(self, client: pybotters.Client, **kwargs):
        await self.ws_connect(client, **kwargs)
        await self._initialize_impl(client, **kwargs)
        await self._auto_update()

    async def ws_connect(
        self, client: pybotters.Client, **kwargs
    ) -> "pybotters.ws.WebSocketRunner":
        self._ws = await self._ws_connect_impl(client, **kwargs)
        return self._ws
