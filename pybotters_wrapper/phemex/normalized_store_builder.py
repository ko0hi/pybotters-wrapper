from pybotters.models.phemex import PhemexDataStore

from ..core import (
    NormalizedStoreBuilder,
    PositionStore,
    ExecutionStore,
    OrderStore,
    OrderbookStore,
    TradesStore,
    TickerStore,
)


class PhemexNormalizedStoreBuilder(NormalizedStoreBuilder[PhemexDataStore]):
    def ticker(self) -> TickerStore:
        pass

    def trades(self) -> TradesStore:
        pass

    def orderbook(self) -> OrderbookStore:
        pass

    def order(self) -> OrderStore:
        pass

    def execution(self) -> ExecutionStore:
        pass

    def position(self) -> PositionStore:
        pass
