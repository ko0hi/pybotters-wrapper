import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.core import TickerFetchAPI
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_fetch_ticker_api,
)


class TestBinanceUSDSMFetchAPIOrderbook:
    SYMBOL = "BTCUSDT"
    DUMMY_RESPONSE = {"symbol": "BTCUSDT", "price": "6000.01", "time": 1589437530011}

    @pytest.mark.asyncio
    async def test_generate_endpoint(self):
        expected = "/fapi/v1/ticker/price"
        async with create_client() as client:
            api = create_binanceusdsm_fetch_ticker_api(client, verbose=True)
            actual = api._generate_endpoint({"symbol": self.SYMBOL, "extra_params": {}})
            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self):
        expected = {"symbol": "BTCUSDT"}
        async with create_client() as client:
            api = create_binanceusdsm_fetch_ticker_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/ticker/price",
                    "symbol": self.SYMBOL,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_itemize_response(self, async_response_mocker):
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.SYMBOL}"
        expected = {"symbol": "BTCUSDT", "price": 6000.01}
        async with create_client() as client:
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                resp = await client.get(url)
                resp_data = await resp.json()
                api = create_binanceusdsm_fetch_ticker_api(client, verbose=True)

                actual = api._itemize_response(resp, resp_data)

                assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={self.SYMBOL}"
        spy_generate_endpoint = mocker.spy(TickerFetchAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(TickerFetchAPI, "_translate_parameters")
        spy_itemize_response = mocker.spy(TickerFetchAPI, "_itemize_response")
        expected_generate_endpoint = "/fapi/v1/ticker/price"
        expected_translate_parameters = {"symbol": "BTCUSDT"}
        expected_itemize_response = {"symbol": "BTCUSDT", "price": 6000.01}
        async with create_client() as client:
            api = create_binanceusdsm_fetch_ticker_api(client, verbose=True)
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)

                await api.fetch_ticker(self.SYMBOL)

                assert spy_generate_endpoint.spy_return == expected_generate_endpoint
                assert (
                    spy_translate_parameters.spy_return == expected_translate_parameters
                )
                assert spy_itemize_response.spy_return == expected_itemize_response
