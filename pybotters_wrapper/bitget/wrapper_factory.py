import pybotters
from pybotters import BitgetDataStore

from ..core import CancelOrderAPI, LimitOrderAPI, MarketOrderAPI, WrapperFactory
from .normalized_store_builder import BitgetNormalizedStoreBuilder
from .price_size_precision_fetcher import BitgetPriceSizePrecisionFetcher
from .websocket_channels import BitgetWebSocketChannels


class BitgetWrapperFactory(WrapperFactory):
    __BASE_URL = "https://api.bitget.com"
    _EXCHANGE_PROPERTIES = {
        "exchange": "bitget",
        "base_url": __BASE_URL,
    }
    _DATASTORE_MANAGER = BitgetDataStore
    _WEBSOCKET_CHANNELS = BitgetWebSocketChannels
    _PRICE_SIZE_PRECISION_FETCHER = BitgetPriceSizePrecisionFetcher
    _NORMALIZED_STORE_BUILDER = BitgetNormalizedStoreBuilder

    @classmethod
    def create_limit_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> LimitOrderAPI:
        raise NotImplementedError

    @classmethod
    def create_market_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> MarketOrderAPI:
        raise NotImplementedError

    @classmethod
    def create_cancel_order_api(
        cls, client: pybotters.Client, verbose: bool = False
    ) -> CancelOrderAPI:
        raise NotImplementedError
