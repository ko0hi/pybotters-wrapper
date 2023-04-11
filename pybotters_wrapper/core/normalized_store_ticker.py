from typing import TypedDict
from .normalized_store import NormalizedDataStore


class TickerItem(TypedDict):
    symbol: str
    price: float


class TickerStore(NormalizedDataStore[TickerItem]):
    _NAME = "ticker"
    _KEYS = ["symbol"]

    def _itemize(self, symbol: str, price: float, **extra) -> TickerItem:
        return TickerItem(symbol=symbol, price=price, **extra)  # noqa
