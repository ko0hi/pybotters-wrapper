from ..typedefs import ExecutionItem
from .normalized_store import NormalizedDataStore


class ExecutionStore(NormalizedDataStore[ExecutionItem]):
    _NAME = "execution"
    _KEYS = ["id"]
    _NORMALIZED_ITEM_CLASS = ExecutionItem
