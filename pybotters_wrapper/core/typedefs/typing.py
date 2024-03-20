from __future__ import annotations

from typing import Literal, TypeVar

import pandas as pd
from pybotters.store import DataStoreCollection

TEndpoint = str
TOrderId = str
TSymbol = str
TSide = Literal["BUY", "SELL"] | str
TPrice = float
TSize = float
TTrigger = float
TTimestamp = pd.Timestamp
TRequestMethod = Literal["GET", "POST", "PUT", "DELETE"] | str
TDataStoreManager = TypeVar("TDataStoreManager", bound=DataStoreCollection)
