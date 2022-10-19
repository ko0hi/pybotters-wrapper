from pybotters.models.ftx import FTXDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.ftx import FTXSocketChannels


class FTXDataStoreWrapper(DataStoreWrapper[FTXDataStore]):
    _SOCKET = FTXSocketChannels

    def __init__(self, store: FTXDataStore = None, *args, **kwargs):
        super(FTXDataStoreWrapper, self).__init__(
            store or FTXDataStore(), *args, **kwargs
        )
