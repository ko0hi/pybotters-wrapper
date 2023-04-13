from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TOrderId, TPrice, TSide, TSize, TSymbol, TTimestamp


class TradesItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp


class TradesStore(NormalizedDataStore[TradesItem]):
    _NAME = "trades"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = TradesItem
