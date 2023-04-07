from typing import Literal, TypeVar
from pybotters.store import DataStoreManager

TEndpoint = str
TOrderId = str
TSymbol = str
TSide = Literal["BUY", "SELL"]
TPrice = float
TSize = float
TTrigger = float
TRequsetMethod = Literal["GET", "POST", "PUT", "DELETE"]
TDataStoreManager = TypeVar("TDataStoreManager", bound=DataStoreManager)
