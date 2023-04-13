from typing import TypedDict

from .normalized_store import NormalizedDataStore
from .._typedefs import TOrderId, TPrice, TSide, TSize, TSymbol, TTimestamp


class ExecutionItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp


class ExecutionStore(NormalizedDataStore[ExecutionItem]):
    _NAME = "execution"
    _KEYS = []
    _NORMALIZED_ITEM_CLASS = ExecutionItem
