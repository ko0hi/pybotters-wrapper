from pybotters.models.bitget import BitgetDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.bitget import BitgetSocket


class BitgetDataStoreWrapper(DataStoreWrapper[BitgetDataStore]):
    _SOCKET = BitgetSocket
    def __init__(self, store: BitgetDataStore = None, *args, **kwargs):
        super(BitgetDataStoreWrapper, self).__init__(
            store or BitgetDataStore(), *args, **kwargs
        )
