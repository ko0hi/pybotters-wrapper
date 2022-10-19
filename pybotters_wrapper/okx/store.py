from pybotters.models.okx import OKXDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.okx import OKXSocketChannels


class OKXDataStoreWrapper(DataStoreWrapper[OKXDataStore]):
    _SOCKET = OKXSocketChannels

    def __init__(self, store: OKXDataStore = None, *args, **kwargs):
        super(OKXDataStoreWrapper, self).__init__(
            store or OKXDataStore(), *args, **kwargs
        )
