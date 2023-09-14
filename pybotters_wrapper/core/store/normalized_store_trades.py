from ..typedefs import TradesItem
from .normalized_store import NormalizedDataStore


class TradesStore(NormalizedDataStore[TradesItem]):
    _NAME = "trades"
    _KEYS = ["id", "symbol"]
    _NORMALIZED_ITEM_CLASS = TradesItem
