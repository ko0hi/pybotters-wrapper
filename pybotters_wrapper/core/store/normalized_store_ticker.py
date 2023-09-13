from ..typedefs import TickerItem
from .normalized_store import NormalizedDataStore


class TickerStore(NormalizedDataStore[TickerItem]):
    _NAME = "ticker"
    _KEYS = ["symbol"]
    _NORMALIZED_ITEM_CLASS = TickerItem
