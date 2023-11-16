from typing import Callable

import pybotters
import pytest
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.coincheck import CoincheckWrapperFactory
from pybotters_wrapper.core import StoreInitializer


@pytest.fixture
def store() -> pybotters.CoincheckDataStore:
    return pybotters.CoincheckDataStore()


@pytest.fixture
def initializer_factory() -> Callable[[pybotters.CoincheckDataStore], StoreInitializer]:
    return CoincheckWrapperFactory.create_store_initializer


@pytest.mark.asyncio
async def test_initialize_orderbook(
    store: pybotters.CoincheckDataStore,
    initializer_factory: Callable[[pybotters.CoincheckDataStore], StoreInitializer],
) -> None:
    url = "https://coincheck.com/api/order_books?pair=btc_jpy"
    dummy_response = {
        "asks": [[27330, "2.25"], [27340, "0.45"]],
        "bids": [[27240, "1.1543"], [26800, "1.2226"]],
    }
    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_orderbook(client, pair="btc_jpy")
            assert (
                len(store.orderbook) == 4
                and len(store.orderbook.find({"side": "bids"})) == 2
                and len(store.orderbook.find({"side": "asks"})) == 2
            )
