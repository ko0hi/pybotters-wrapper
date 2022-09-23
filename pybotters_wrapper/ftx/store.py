from pybotters.models.ftx import FTXDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.ftx import FTXSocket


class FTXDataStoreWrapper(DataStoreWrapper[FTXDataStore]):
    _SOCKET = FTXSocket

    def __init__(self, store: FTXDataStore = None, *args, **kwargs):
        super(FTXDataStoreWrapper, self).__init__(
            store or FTXDataStore(), *args, **kwargs
        )
