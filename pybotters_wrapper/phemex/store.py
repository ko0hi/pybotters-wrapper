from pybotters.models.phemex import PhemexDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.phemex import PhemexWebsocketChannels


class PhemexDataStoreWrapper(DataStoreWrapper[PhemexDataStore]):
    _SOCKET_CHANNELS_CLS = PhemexWebsocketChannels

    def __init__(self, store: PhemexDataStore = None):
        super(PhemexDataStoreWrapper, self).__init__(store or PhemexDataStore())
        raise NotImplementedError
