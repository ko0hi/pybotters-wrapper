from abc import ABCMeta, abstractmethod
from typing import Generic

from pybotters_wrapper.core.typedefs.typing import TDataStoreManager

from ...exceptions import UnsupportedStoreError
from .normalized_store_execution import ExecutionStore
from .normalized_store_order import OrderStore
from .normalized_store_orderbook import OrderbookStore
from .normalized_store_position import PositionStore
from .normalized_store_ticker import TickerStore
from .normalized_store_trades import TradesStore


class NormalizedStoreBuilder(Generic[TDataStoreManager], metaclass=ABCMeta):
    def __init__(self, store: TDataStoreManager):
        self._store: TDataStoreManager = store

    @abstractmethod
    def ticker(self) -> TickerStore:
        raise NotImplementedError

    @abstractmethod
    def trades(self) -> TradesStore:
        raise NotImplementedError

    @abstractmethod
    def orderbook(self) -> OrderbookStore:
        raise NotImplementedError

    @abstractmethod
    def order(self) -> OrderStore:
        raise NotImplementedError

    @abstractmethod
    def execution(self) -> ExecutionStore:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> PositionStore:
        raise NotImplementedError

    def get(
        self, *names: str
    ) -> (
        dict[
            str,
            TickerStore
            | TradesStore
            | OrderbookStore
            | OrderbookStore
            | ExecutionStore
            | PositionStore,
        ]
        | TickerStore
        | TradesStore
        | OrderbookStore
        | OrderStore
        | ExecutionStore
        | PositionStore
    ):
        if len(names) == 0:
            names = ("ticker", "trades", "orderbook", "order", "execution", "position")

        if len(names) == 1:
            return getattr(self, names[0])()
        else:
            rtn = {}
            for name in names:
                try:
                    rtn[name] = getattr(self, name)()
                except UnsupportedStoreError:
                    pass
            return rtn
