from typing import TypedDict

from pybotters.typedefs import Item

from .normalized_store import NormalizedDataStore
from .._typedefs import Side


class OrderbookItem(TypedDict):
    symbol: str
    side: Side
    price: float
    size: float


class OrderbookStore(NormalizedDataStore):
    _NAME = "orderbook"
    _KEYS = ["symbol", "side", "price"]

    def __init__(self, *args, **kwargs):
        super(OrderbookStore, self).__init__(*args, **kwargs)
        self._mid = None

    def _itemize(
        self, symbol: str, side: Side, price: float, size: float, **extra
    ) -> OrderbookItem:
        return OrderbookItem(
            symbol=symbol, side=side, price=price, size=size, **extra  # noqa
        )

    def _on_wait(self):
        sells, buys = self.sorted().values()
        if len(sells) != 0 and len(buys) != 0:
            ba = sells[0]["price"]
            bb = buys[0]["price"]
            self._mid = (ba + bb) / 2

    def sorted(self, query: Item = None) -> dict[Side, list[Item]]:
        if query is None:
            query = {}
        result: dict[Side, list[Item]] = {"SELL": [], "BUY": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["SELL"].sort(key=lambda x: x["price"])
        result["BUY"].sort(key=lambda x: x["price"], reverse=True)
        return result

    @property
    def mid(self):
        return self._mid
