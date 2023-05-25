from .normalized_store import NormalizedDataStore
from ..typedefs import TradesItem


class TradesStore(NormalizedDataStore[TradesItem]):
    _NAME = "trades"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = TradesItem
