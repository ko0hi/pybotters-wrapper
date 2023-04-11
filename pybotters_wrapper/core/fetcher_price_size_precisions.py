from abc import ABCMeta, abstractmethod


class PriceSizePrecisionFetcher(metaclass=ABCMeta):
    @abstractmethod
    def fetch_precisions(self, cache: bool = True) -> dict:
        raise NotImplementedError

