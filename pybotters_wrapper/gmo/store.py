from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.common import DataStoreWrapper


class GMODataStoreWrapper(DataStoreWrapper[GMOCoinDataStore]):
    def __init__(self, store: GMOCoinDataStore = None, *args, **kwargs):
        super(GMODataStoreWrapper, self).__init__(
            store or GMOCoinDataStore(), *args, **kwargs
        )
