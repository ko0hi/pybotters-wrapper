from typing import Literal

from abc import ABCMeta, abstractmethod
import math


from ..typedefs import TSymbol


class PriceSizePrecisionFetcher(metaclass=ABCMeta):
    @abstractmethod
    def fetch_precisions(self) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        raise NotImplementedError

    @classmethod
    def value_to_precision(cls, value: float) -> int:
        if value >= 1:
            return 0
        else:
            return int(math.log10(value) * -1)
