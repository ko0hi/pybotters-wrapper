from pybotters.models.binance import BinanceDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.binance import BinanceSocket


class BinanceDataStoreWrapper(DataStoreWrapper[BinanceDataStore]):
    _SOCKET = BinanceSocket

    def __init__(self, store: BinanceDataStore = None, *args, **kwargs):
        super(BinanceDataStoreWrapper, self).__init__(
            store or BinanceDataStore(), *args, **kwargs
        )
