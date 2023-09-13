from pybotters import OKXDataStore
from ..core import WrapperFactory
from .websocket_channels import OKXWebSocketChannels
from .normalized_store_builder import OKXNormalizedStoreBuilder
from .price_size_precision_fetcher import OKXPriceSizePrecisionFetcher


class OKXWrapperFactory(WrapperFactory):
    __BASE_URL = "https://www.okx.com"
    _EXCHANGE_PROPERTIES = {
        "exchange": "okx",
        "base_url": __BASE_URL,
    }
    _DATASTORE_MANAGER = OKXDataStore
    _WEBSOCKET_CHANNELS = OKXWebSocketChannels
    _NORMALIZED_STORE_BUILDER = OKXNormalizedStoreBuilder
    _PRICE_SIZE_PRECISION_FETCHER = OKXPriceSizePrecisionFetcher
