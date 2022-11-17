from pybotters.models.okx import OKXDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.okx import OKXWebsocketChannels



class OKXDataStoreWrapper(DataStoreWrapper[OKXDataStore]):
    _WEBSOCKET_CHANNELS = OKXWebsocketChannels

    def __init__(self, store: OKXDataStore = None):
        super(OKXDataStoreWrapper, self).__init__(store or OKXDataStore())
        raise NotImplementedError