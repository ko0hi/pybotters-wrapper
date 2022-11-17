from pybotters.models.bitget import BitgetDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.bitget import BitgetWebsocketChannels


class BitgetDataStoreWrapper(DataStoreWrapper[BitgetDataStore]):
    _WEBSOCKET_CHANNELS = BitgetWebsocketChannels

    def __init__(self, store: BitgetDataStore = None):
        super(BitgetDataStoreWrapper, self).__init__(store or BitgetDataStore())
        raise NotImplementedError
