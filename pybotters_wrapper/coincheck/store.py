from pybotters.models.coincheck import CoincheckDataStore
from pybotters_wrapper.common import DataStoreWrapper


class CoincheckDataStoreWrapper(DataStoreWrapper[CoincheckDataStore]):
    def __init__(self, store: CoincheckDataStore = None):
        super(CoincheckDataStoreWrapper, self).__init__(
            store or CoincheckDataStore()
        )
        raise NotImplementedError
