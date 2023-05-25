from pybotters.typedefs import Item

from .normalized_store import NormalizedDataStore
from ..typedefs import OrderbookItem, TSide


class OrderbookStore(NormalizedDataStore[OrderbookItem]):
    _NAME = "orderbook"
    _KEYS = ["symbol", "side", "price"]
    _NORMALIZED_ITEM_CLASS = OrderbookItem

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
