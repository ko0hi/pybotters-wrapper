from ..typedefs import OrderItem
from .normalized_store import NormalizedDataStore


class OrderStore(NormalizedDataStore[OrderItem]):
    _NAME = "order"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = OrderItem
