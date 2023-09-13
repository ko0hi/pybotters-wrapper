import pybotters
from pybotters import OKXDataStore

from ..core import CancelOrderAPI, LimitOrderAPI, MarketOrderAPI, WrapperFactory
from .normalized_store_builder import OKXNormalizedStoreBuilder
from .price_size_precision_fetcher import OKXPriceSizePrecisionFetcher
from .websocket_channels import OKXWebSocketChannels


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
