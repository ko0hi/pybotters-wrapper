from typing import TypedDict

from pybotters.typedefs import Item

from .normalized_store import NormalizedDataStore
from .._typedefs import TPrice, TSide, TSize, TSymbol


class OrderbookItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize


class OrderbookStore(NormalizedDataStore[OrderbookItem]):
    _NAME = "orderbook"
    _KEYS = ["symbol", "side", "price"]
    _NORMALIZED_ITEM_CLASS = OrderbookItem

    def __init__(self, *args, **kwargs):
        super(OrderbookStore, self).__init__(*args, **kwargs)
        self._mid = None

    def _on_wait(self):
        sells, buys = self.sorted().values()
        if len(sells) != 0 and len(buys) != 0:
            ba = sells[0]["price"]
            bb = buys[0]["price"]
            self._mid = (ba + bb) / 2

    def sorted(self, query: Item = None) -> dict[TSide, list[Item]]:
        if query is None:
            query = {}
        result: dict[TSide, list[Item]] = {"SELL": [], "BUY": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["SELL"].sort(key=lambda x: x["price"])
        result["BUY"].sort(key=lambda x: x["price"], reverse=True)
        return result

    @property
    def mid(self):
        return self._mid
