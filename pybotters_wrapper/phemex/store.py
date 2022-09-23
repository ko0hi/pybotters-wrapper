from pybotters.models.phemex import PhemexDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.phemex import PhemexSocket


class PhemexDataStoreWrapper(DataStoreWrapper[PhemexDataStore]):
    _SOCKET = PhemexSocket

    def __init__(self, store: PhemexDataStore = None, *args, **kwargs):
        super(PhemexDataStoreWrapper, self).__init__(
            store or PhemexDataStore(), *args, **kwargs
        )