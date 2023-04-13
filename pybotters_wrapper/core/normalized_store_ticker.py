from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TPrice, TSymbol


class TickerItem(TypedDict):
    symbol: TSymbol
    price: TPrice


class TickerStore(NormalizedDataStore[TickerItem]):
    _NAME = "ticker"
    _KEYS = ["symbol"]
    _NORMALIZED_ITEM_CLASS = TickerItem