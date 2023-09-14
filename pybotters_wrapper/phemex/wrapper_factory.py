import pybotters
from pybotters import PhemexDataStore

from ..core import CancelOrderAPI, LimitOrderAPI, MarketOrderAPI, WrapperFactory
from .normalized_store_builder import PhemexNormalizedStoreBuilder
from .websocket_channels import PhemexWebsocketChannels


class PhemexWrapperFactory(WrapperFactory):
    _BASE_URL = "https://api.phemex.com"
    _EXCHANGE_PROPERTIES = {"exchange": "phemex", "base_url": _BASE_URL}
    _DATASTORE_MANAGER = PhemexDataStore
    _WEBSOCKET_CHANNELS = PhemexWebsocketChannels
    _NORMALIZED_STORE_BUILDER = PhemexNormalizedStoreBuilder

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
