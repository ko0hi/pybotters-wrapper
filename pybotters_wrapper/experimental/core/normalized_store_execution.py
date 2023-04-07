from typing import TypedDict

import pandas as pd

from .normalized_store import NormalizedDataStore
from .._typedefs import TSide


class ExecutionItem(TypedDict):
    id: str
    symbol: str
    side: TSide
    price: float
    size: float
    timestamp: pd.Timestamp


class ExecutionStore(NormalizedDataStore):
    _NAME = "execution"
    _KEYS = []
