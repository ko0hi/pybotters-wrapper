from pybotters.models.bitflyer import bitFlyerDataStore, Board
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.bitflyer import BitflyerSocket


class BitflyerDataStoreWrapper(DataStoreWrapper[bitFlyerDataStore]):
    _SOCKET = BitflyerSocket

    def __init__(self, store: bitFlyerDataStore = None, *args, **kwargs):
        super(BitflyerDataStoreWrapper, self).__init__(
            store or bitFlyerDataStore(), *args, **kwargs
        )

    @property
    def board(self) -> Board:
        return self._store.board

    @property
    def executions(self):
        return self._store.executions

    @property
    def trades(self):
        return self.executions

    @property
    def childorderevents(self):
        return self._store.childorderevents

    @property
    def events(self):
        return self.childorderevents

    @property
    def childorders(self):
        return self._store.childorders

    @property
    def position(self):
        return self._store.positions

    @property
    def orders(self):
        return self.childorders
