from pybotters.models.okx import OKXDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.okx import OKXWebsocketChannels


class OKXDataStoreManagerWrapper(DataStoreManagerWrapper[OKXDataStore]):
    _SOCKET_CHANNELS_CLS = OKXWebsocketChannels

    def __init__(self, store: OKXDataStore = None, *args, **kwargs):
        super(OKXDataStoreManagerWrapper, self).__init__(
            store or OKXDataStore(), *args, **kwargs
        )
