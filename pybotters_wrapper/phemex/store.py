from pybotters.models.phemex import PhemexDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.phemex import PhemexWebsocketChannels


class PhemexDataStoreManagerWrapper(DataStoreManagerWrapper[PhemexDataStore]):
    _SOCKET_CHANNELS_CLS = PhemexWebsocketChannels

    def __init__(self, store: PhemexDataStore = None, *args, **kwargs):
        super(PhemexDataStoreManagerWrapper, self).__init__(
            store or PhemexDataStore(), *args, **kwargs
        )