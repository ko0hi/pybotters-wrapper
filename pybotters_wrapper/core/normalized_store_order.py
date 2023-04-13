from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TOrderId, TPrice, TSide, TSize, TSymbol, TTimestamp


class OrderItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    type: str


class OrderStore(NormalizedDataStore[OrderItem]):
    _NAME = "order"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = OrderItem
