from ..wrapper_factory import BybitWrapperFactoryMixin
from .websocket_channels import BybitUSDTWebSocketChannels


class BybitUSDTWrapperFactory(BybitWrapperFactoryMixin):
    __BASE_URL = "https://api.bybit.com"
    _CATEGORY = "linear"
    _EXCHANGE_PROPERTIES = {
        "exchange": "bybitusdt",
        "base_url": __BASE_URL,
    }
    _WEBSOCKET_CHANNELS = BybitUSDTWebSocketChannels
