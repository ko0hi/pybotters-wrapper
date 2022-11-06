from pybotters.models.bitget import BitgetDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.bitget import BitgetWebsocketChannels


class BitgetDataStoreManagerWrapper(DataStoreManagerWrapper[BitgetDataStore]):
    _SOCKET_CHANNELS_CLS = BitgetWebsocketChannels
    def __init__(self, store: BitgetDataStore = None, *args, **kwargs):
        super(BitgetDataStoreManagerWrapper, self).__init__(
            store or BitgetDataStore(), *args, **kwargs
        )
