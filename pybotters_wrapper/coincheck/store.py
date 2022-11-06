from pybotters.models.coincheck import CoincheckDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper


class CoincheckDataStoreManagerWrapper(DataStoreManagerWrapper[CoincheckDataStore]):
    def __init__(self, store: CoincheckDataStore = None):
        super(CoincheckDataStoreManagerWrapper, self).__init__(
            store or CoincheckDataStore()
        )
        raise NotImplementedError
