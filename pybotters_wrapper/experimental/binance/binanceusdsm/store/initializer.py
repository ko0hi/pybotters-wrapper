from typing import Awaitable

import aiohttp
import pybotters
from pybotters.models.binance import BinanceUSDSMDataStore

from ..exchange_property import BinanceUSDSMExchangeProperty
from ....core.store.initializer import StoreInitializer


class BinanceUSDSMStoreInitializer:
    def __init__(self, store: BinanceUSDSMDataStore):
        self._eprop = BinanceUSDSMExchangeProperty()
        self._initializer = StoreInitializer(store)
        self._initializer.register_token_config(
            "POST", f"{self._eprop.base_url}/fapi/v1/listenKey"
        )
        self._initializer.register_token_private_config(
            "POST", f"{self._eprop.base_url}/fapi/v1/listenKey"
        )
        self._initializer.register_orderbook_config(
            "GET", f"{self._eprop.base_url}/fapi/v1/depth", {"symbol"}
        )
        self._initializer.register_order_config(
            "GET", f"{self._eprop.base_url}/fapi/v1/openOrders"
        )
        self._initializer.register_position_config(
            "GET", f"{self._eprop.base_url}/fapi/v2/positionRisk"
        )

    async def initialize(
        self,
        aw_or_key_or_key_and_params_list: list[
            Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]
        ],
        client: pybotters.Client,
    ):
        return await self._initializer.initialize(
            aw_or_key_or_key_and_params_list, client
        )

    async def initialize_token(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("token", params)], client)

    async def initialize_token_public(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("token_public", params)], client)

    async def initialize_token_private(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("token_private", params)], client)

    async def initialize_ticker(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("ticker", params)], client)

    async def initialize_trades(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("trades", params)], client)

    async def initialize_orderbook(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("orderbook", params)], client)

    async def initialize_order(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("order", params)], client)

    async def initialize_execution(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("execution", params)], client)

    async def initialize_position(self, client: "pybotters.Client", **params):
        return await self._initializer.initialize([("position", params)], client)
