import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.core import OrderbookFetchAPI
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_fetch_orderbook_api,
)


class TestBinanceUSDSMFetchAPIOrderbook:
    SYMBOL = "BTCUSDT"
    DUMMY_RESPONSE = {
        "lastUpdateId": 1027024,
        "E": 1589436922972,
        "T": 1589436922959,
        "bids": [["4.00000000", "431.00000000"]],
        "asks": [["4.00000200", "12.00000000"]],
    }

    @pytest.mark.asyncio
    async def test_generate_endpoint(self):
        expected = "/fapi/v1/depth"
        async with create_client() as client:
            api = create_binanceusdsm_fetch_orderbook_api(client, verbose=True)
            actual = api._generate_endpoint({"symbol": self.SYMBOL, "extra_params": {}})
            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self):
        expected = {"symbol": "BTCUSDT"}

        async with create_client() as client:
            api = create_binanceusdsm_fetch_orderbook_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/depth",
                    "symbol": self.SYMBOL,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_itemize_response(self, async_response_mocker):
        url = f"https://fapi.binance.com/fapi/v1/depth?symbol={self.SYMBOL}"
        expected = {
            "BUY": [{"price": 4.0, "side": "BUY", "size": 431.0, "symbol": "BTCUSDT"}],
            "SELL": [
                {"price": 4.000002, "side": "SELL", "size": 12.0, "symbol": "BTCUSDT"}
            ],
        }
        async with create_client() as client:
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                resp = await client.get(url)
                resp_data = await resp.json()
                api = create_binanceusdsm_fetch_orderbook_api(client, verbose=True)

                actual = api._itemize_response(resp, resp_data)

                assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        url = f"https://fapi.binance.com/fapi/v1/depth?symbol={self.SYMBOL}"
        spy_generate_endpoint = mocker.spy(OrderbookFetchAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(
            OrderbookFetchAPI, "_translate_parameters"
        )
        spy_itemize_response = mocker.spy(OrderbookFetchAPI, "_itemize_response")
        expected_generate_endpoint = "/fapi/v1/depth"
        expected_translate_parameters = {"symbol": "BTCUSDT"}
        expected_itemize_response = {
            "BUY": [{"price": 4.0, "side": "BUY", "size": 431.0, "symbol": "BTCUSDT"}],
            "SELL": [
                {"price": 4.000002, "side": "SELL", "size": 12.0, "symbol": "BTCUSDT"}
            ],
        }

        async with create_client() as client:
            api = create_binanceusdsm_fetch_orderbook_api(client, verbose=True)
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                await api.fetch_orderbook(self.SYMBOL)

                assert spy_generate_endpoint.spy_return == expected_generate_endpoint
                assert (
                    spy_translate_parameters.spy_return == expected_translate_parameters
                )
                assert spy_itemize_response.spy_return == expected_itemize_response
