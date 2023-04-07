from typing import TypedDict

import pandas as pd

from .normalized_store import NormalizedDataStore
from .._typedefs import TSide


class TradesItem(TypedDict):
    id: str
    symbol: str
    side: TSide
    price: float
    size: float
    timestamp: pd.Timestamp


class TradesStore(NormalizedDataStore[TradesItem]):
    _NAME = "trades"
    _KEYS = ["id", "symbol"]

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: TSide,
        price: float,
        size: float,
        timestamp: pd.Timestamp,
        **extra
    ) -> TradesItem:
        return TradesItem(
            id=id,
            symbol=symbol,
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            **extra  # noqa
        )
