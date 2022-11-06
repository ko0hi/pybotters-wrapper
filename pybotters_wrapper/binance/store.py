from pybotters.models.binance import BinanceDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.binance import BinanceWebsocketChannels


class BinanceDataStoreManagerWrapper(DataStoreManagerWrapper[BinanceDataStore]):
    _SOCKET_CHANNELS_CLS = BinanceWebsocketChannels

    def __init__(self, store: BinanceDataStore = None):
        super(BinanceDataStoreManagerWrapper, self).__init__(store or BinanceDataStore())
        raise NotImplementedError
