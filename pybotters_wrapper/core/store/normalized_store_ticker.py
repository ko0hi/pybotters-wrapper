from .normalized_store import NormalizedDataStore
from ..typedefs import TickerItem


class TickerStore(NormalizedDataStore[TickerItem]):
    _NAME = "ticker"
    _KEYS = ["symbol"]
    _NORMALIZED_ITEM_CLASS = TickerItem
