from pybotters.models.binance import BinanceUSDSMDataStore

from .exchange_property import BinanceUSDSMExchangeProperty
from ...core.store_initializer import StoreInitializer


class BinanceUSDSMStoreInitializer(StoreInitializer[BinanceUSDSMDataStore]):
    base = BinanceUSDSMExchangeProperty().base_url
    _DEFAULT_INITIALIZE_CONFIG = {
        "token": ("POST", f"{base}/fapi/v1/listenKey"),
        "token_private": ("POST", f"{base}/fapi/v1/listenKey"),
        "orderbook": ("GET", f"{base}/fapi/v1/depth", {"symbol"}),
        "order": ("GET", f"{base}/fapi/v1/openOrders"),
        "position": ("GET", f"{base}/fapi/v2/positionRisk"),
    }
