from .normalized_store import NormalizedDataStore
from ..typedefs import OrderItem


class OrderStore(NormalizedDataStore[OrderItem]):
    _NAME = "order"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = OrderItem
