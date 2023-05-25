from typing import Literal, TypeVar

import pandas as pd
from pybotters.store import DataStoreManager

TEndpoint = str
TOrderId = str
TSymbol = str
TSide = Literal["BUY", "SELL"]
TPrice = float
TSize = float
TTrigger = float
TTimestamp = pd.Timestamp
TRequestMethod = Literal["GET", "POST", "PUT", "DELETE"]
TDataStoreManager = TypeVar("TDataStoreManager", bound=DataStoreManager)
