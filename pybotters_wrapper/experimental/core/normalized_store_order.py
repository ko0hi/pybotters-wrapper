from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TSide


class OrderItem(TypedDict):
    id: str
    symbol: str
    side: TSide
    price: float
    size: float
    type: str


class OrderStore(NormalizedDataStore):
    _NAME = "order"
    _KEYS = ["id", "symbol"]
