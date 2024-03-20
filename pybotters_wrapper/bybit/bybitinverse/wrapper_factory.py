from ..wrapper_factory import BybitWrapperFactoryMixin
from .websocket_channels import BybitInverseWebSocketChannels


class BybitInverseWrapperFactory(BybitWrapperFactoryMixin):
    __BASE_URL = "https://api.bybit.com"
    _CATEGORY = "inverse"
    _EXCHANGE_PROPERTIES = {
        "exchange": "bybitinverse",
        "base_url": __BASE_URL,
    }
    _WEBSOCKET_CHANNELS = BybitInverseWebSocketChannels
