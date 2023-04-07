from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import Side


class OrderItem(TypedDict):
    id: str
    symbol: str
    side: Side
    price: float
    size: float
    type: str


class OrderStore(NormalizedDataStore):
    _NAME = "order"
    _KEYS = ["id", "symbol"]
