from pybotters.models.bitflyer import bitFlyerDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.bitflyer import BitflyerSocket


class BitflyerDataStoreWrapper(DataStoreWrapper[bitFlyerDataStore]):
    _SOCKET = BitflyerSocket

    def __init__(self, store: bitFlyerDataStore = None, *args, **kwargs):
        super(BitflyerDataStoreWrapper, self).__init__(
            store or bitFlyerDataStore(), *args, **kwargs
        )

    @property
    def board(self):
        return self._store.board

    @property
    def executions(self):
        return self._store.executions
