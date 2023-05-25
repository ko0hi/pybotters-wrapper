from typing import Literal

from abc import ABCMeta, abstractmethod

from ..typedefs import TSymbol


class PriceSizePrecisionFetcher(metaclass=ABCMeta):
    @abstractmethod
    def fetch_precisions(
        self, cache: bool = True
    ) -> dict[Literal["price", "size"], dict[TSymbol, int]]:
        raise NotImplementedError
