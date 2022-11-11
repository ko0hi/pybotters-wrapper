from pybotters.models.binance import BinanceDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.binance import BinanceWebsocketChannels


class BinanceDataStoreWrapper(DataStoreWrapper[BinanceDataStore]):
    _SOCKET_CHANNELS_CLS = BinanceWebsocketChannels

    def __init__(self, store: BinanceDataStore = None):
        super(BinanceDataStoreWrapper, self).__init__(store or BinanceDataStore())
        raise NotImplementedError
