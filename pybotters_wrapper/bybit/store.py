from pybotters.models.bybit import BybitUSDTDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.bybit import BybitSocket


class BybitUSDTDataStoreWrapper(DataStoreWrapper[BybitUSDTDataStore]):
    _SOCKET = BybitSocket

    def __init__(self, store: BybitUSDTDataStore = None, *args, **kwargs):
        super(BybitUSDTDataStoreWrapper, self).__init__(
            store or BybitUSDTDataStore(),
            *args, **kwargs
        )
