from __future__ import annotations

from typing import NamedTuple

from pybotters_wrapper.core import DataStoreWrapper

from .._base import Plugin
from ..mixins import WatchStoreMixin, WaitStoreMixin


class BookTicker(WatchStoreMixin, WaitStoreMixin, Plugin):
    class Item(NamedTuple):
        asks: list[tuple[float, float]]
        bids: list[tuple[float, float]]
        price: float

        @property
        def best_ask(self):
            return self.asks[0]["price"]

        @property
        def best_bid(self):
            return self.bids[0]["price"]

        @property
        def best_ask_size(self):
            return self.asks[0]["size"]

        @property
        def best_bid_size(self):
            return self.bids[0]["size"]

        @property
        def mid(self):
            return (self.best_ask + self.best_bid) / 2

    def __init__(self, store: DataStoreWrapper):
        self._tick = self.Item(None, None, None)
        self._store = store
        self.init_watch_store(store.trades)
        self.init_wait_store(store.orderbook)

    def _on_wait(self):
        asks, bids = self.wait_store.sorted().values()
        self._update(asks=asks, bids=bids)

    def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        self._update(price=data["price"])

    def _update(self, *, asks=None, bids=None, price=None):
        self._tick = self.Item(
            asks or self._tick.asks, bids or self._tick.bids, price or self._tick.price
        )

    @property
    def tick(self):
        return self._tick

    @property
    def asks(self):
        return self._tick.asks

    @property
    def best_ask(self):
        return self._tick.best_ask

    @property
    def best_ask_size(self):
        return self._tick.best_ask_size

    @property
    def bids(self):
        return self._tick.bids

    @property
    def best_bid(self):
        return self._tick.best_bid

    @property
    def best_bid_size(self):
        return self._tick.best_bid_size

    @property
    def price(self):
        return self._tick.price

    @property
    def mid(self):
        return self._tick.mid

    @property
    def spread(self):
        return self.best_ask - self.best_bid

