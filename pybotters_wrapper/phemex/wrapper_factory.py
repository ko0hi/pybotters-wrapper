from pybotters import PhemexDataStore

from .normalized_store_builder import PhemexNormalizedStoreBuilder
from .websocket_channels import PhemexWebsocketChannels
from ..core import (
    WrapperFactory,
)


class PhemexWrapperFactory(WrapperFactory):
    _BASE_URL = "https://api.phemex.com"
    _EXCHANGE_PROPERTIES = {"exchange": "phemex", "base_url": _BASE_URL}
    _DATASTORE_MANAGER = PhemexDataStore
    _WEBSOCKET_CHANNELS = PhemexWebsocketChannels
    _NORMALIZED_STORE_BUILDER = PhemexNormalizedStoreBuilder
