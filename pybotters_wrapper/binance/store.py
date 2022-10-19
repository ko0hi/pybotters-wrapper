from pybotters.models.binance import BinanceDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.binance import BinanceSocketChannels


class BinanceDataStoreWrapper(DataStoreWrapper[BinanceDataStore]):
    _SOCKET = BinanceSocketChannels

    def __init__(self, store: BinanceDataStore = None, *args, **kwargs):
        super(BinanceDataStoreWrapper, self).__init__(
            store or BinanceDataStore(), *args, **kwargs
        )
