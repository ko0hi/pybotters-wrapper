from typing import Literal, TypeVar
from pybotters.store import DataStoreManager

Side = Literal["BUY", "SELL"]
RequsetMethod = Literal["GET", "POST", "PUT", "DELETE"]
TDataStoreManager = TypeVar("TDataStoreManager", bound=DataStoreManager)
