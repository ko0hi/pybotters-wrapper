from .normalized_store import NormalizedDataStore
from ..typedefs import ExecutionItem


class ExecutionStore(NormalizedDataStore[ExecutionItem]):
    _NAME = "execution"
    _KEYS = []
    _NORMALIZED_ITEM_CLASS = ExecutionItem
