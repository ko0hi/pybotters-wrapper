from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TPrice, TSide, TSize, TSymbol


class PositionItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize


class PositionStore(NormalizedDataStore[PositionItem]):
    _NAME = "position"
    _KEYS = ["symbol"]

    def size(self, symbol: str, side: str = None) -> float:
        query = {"symbol": symbol}
        if side is None:
            items = self.find(query)
            return sum([x["size"] if x["side"] == "BUY" else -x["size"] for x in items])
        else:
            query["side"] = side
            return sum([x["size"] for x in self.find(query)])

    def price(self, symbol: str, side: str) -> float:
        query = {"symbol": symbol}
        positions = self.find(query)
        size = self.size(symbol, side)
        if size > 0:
            return sum([p["price"] * p["size"] for p in positions]) / size
        else:
            return 0

    def summary(self, symbol: str) -> dict:
        rtn = {}
        for s in ["BUY", "SELL"]:
            rtn[f"{s}_size"] = self.size(symbol, s)
            rtn[f"{s}_price"] = self.price(symbol, s)

        rtn["size"] = self.size(symbol)

        if rtn["size"] > 0:
            rtn["side"] = "BUY"
        elif rtn["size"] < 0:
            rtn["side"] = "SELL"
        else:
            rtn["side"] = "NO"

        return rtn
