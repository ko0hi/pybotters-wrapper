from .normalized_store import NormalizedDataStore
from ..typedefs import ExecutionItem


class ExecutionStore(NormalizedDataStore[ExecutionItem]):
    _NAME = "execution"
    _KEYS = ["id"]
    _NORMALIZED_ITEM_CLASS = ExecutionItem
