from pybotters import BitgetDataStore
from ..core import WrapperFactory


from .websocket_channels import BitgetWebSocketChannels
from .price_size_precision_fetcher import BitgetPriceSizePrecisionFetcher

class BitgetWrapperFactory(WrapperFactory):
    __BASE_URL = "https://api.bitget.com"
    _EXCHANGE_PROPERTIES = {
        "exchange": "bitget",
        "base_url": __BASE_URL,
    }
    _DATASTORE_MANAGER = BitgetDataStore
    _WEBSOCKET_CHANNELS = BitgetWebSocketChannels
    _PRICE_SIZE_PRECISION_FETCHER = BitgetPriceSizePrecisionFetcher
