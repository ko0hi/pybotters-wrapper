from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pybotters.store import DataStore

from ...core import DataStoreWrapper, OrderbookItem
from ..base_plugin import Plugin
from ..mixins import WaitStoreMixin, WatchStoreMixin


class BookTicker(WatchStoreMixin, WaitStoreMixin, Plugin):
    class Item(NamedTuple):
        asks: list[OrderbookItem] | None
        bids: list[OrderbookItem] | None
        price: float | None

        @property
        def best_ask(self) -> float | None:
            return None if self.asks is None else self.asks[0]["price"]

        @property
        def best_bid(self) -> float | None:
            return None if self.bids is None else self.bids[0]["price"]

        @property
        def best_ask_size(self) -> float | None:
            return None if self.asks is None else self.asks[0]["size"]

        @property
        def best_bid_size(self) -> float | None:
            return None if self.bids is None else self.bids[0]["size"]

        @property
        def mid(self) -> float | None:
            ba = self.best_ask
            bb = self.best_bid
            return None if ba is None or bb is None else (ba + bb) / 2

    def __init__(self, store: DataStoreWrapper, symbol: str):
        self._tick = self.Item(None, None, None)
        self._store = store
        self._symbol = symbol
        self.init_watch_store(store.trades)
        self.init_wait_store(store.orderbook)

    def _on_wait(self):
        asks, bids = self.wait_store.sorted({"symbol": self._symbol}).values()
        if len(asks) and len(bids):
            self._update(asks=asks, bids=bids)

    def _on_watch(self, store: DataStore, operation: str, source: dict, data: dict):
        if data["symbol"] == self._symbol:
            self._update(price=data["price"])

    def _update(
        self,
        *,
        asks: list[OrderbookItem] | None = None,
        bids: list[OrderbookItem] | None = None,
        price: float | None = None,
    ):
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
