from typing import TypedDict

from .normalized_store import NormalizedDataStore
from _typedefs import TSide


class PositionItem(TypedDict):
    symbol: str
    side: TSide
    price: float
    size: float


class PositionStore(NormalizedDataStore):
    _NAME = "position"
    _KEYS = ["symbol"]

    def size(self, side: str, symbol: str = None) -> float:
        query = {"side": side}
        if symbol:
            query["symbol"] = symbol
        return sum([x["size"] for x in self.find(query)])

    def price(self, side: str, symbol: str = None) -> float:
        query = {"side": side}
        if symbol:
            query["symbol"] = symbol
        positions = self.find(query)
        size = self.size(side)
        if size > 0:
            return sum([p["price"] * p["size"] for p in positions]) / size
        else:
            return 0

    def summary(self, symbol: str = None):
        rtn = {}
        for s in ["BUY", "SELL"]:
            rtn[f"{s}_size"] = self.size(s, symbol)
            rtn[f"{s}_price"] = self.price(s, symbol)

        if rtn["BUY_size"] > 0 and rtn["SELL_size"] == 0:
            rtn["side"] = "BUY"
        elif rtn["BUY_size"] == 0 and rtn["SELL_size"] > 0:
            rtn["side"] = "SELL"
        elif rtn["BUY_size"] > 0 and rtn["SELL_size"] > 0:
            rtn["side"] = "BOTH"
        else:
            rtn["side"] = None

        return rtn
