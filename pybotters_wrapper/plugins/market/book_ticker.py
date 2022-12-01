from __future__ import annotations

from typing import NamedTuple

from pybotters_wrapper.core import DataStoreWrapper, OrderbookStore, TradesStore

from .._base import MultipleDataStoresPlugin


class BookTicker(MultipleDataStoresPlugin):
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
        super(BookTicker, self).__init__(store.trades, store.orderbook)
        self._tick = self.Item(None, None, None)

    def _on_wait(self, store: "DataStore"):
        if isinstance(store, OrderbookStore):
            asks, bids = store.sorted().values()
            self._update(asks=asks, bids=bids)

    def _on_watch(self, d: dict, op: str, store: "DataStore"):
        if isinstance(store, TradesStore):
            self._update(price=d["price"])

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
