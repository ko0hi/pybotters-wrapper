import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_fetch_positions_api,
)
from pybotters_wrapper.core import PositionsFetchAPI


class TestBinanceUSDSMFetchAPIPositions:
    SYMBOL = "ETHBUSD"
    DUMMY_RESPONSE = [
        {
            "symbol": "ETHBUSD",
            "positionAmt": "-0.330",
            "entryPrice": "1995.0",
            "markPrice": "1997.57780226",
            "unRealizedProfit": "-0.85067474",
            "liquidationPrice": "45498.37431442",
            "leverage": "20",
            "maxNotionalValue": "5000000",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notional": "-659.20067474",
            "isolatedWallet": "0",
            "updateTime": 1681393911012,
        }
    ]

    @pytest.mark.asyncio
    async def test_generate_endpoint(self):
        expected = "/fapi/v2/positionRis˚k"
        async with create_client() as client:
            api = create_binanceusdsm_fetch_positions_api(client, verbose=True)
            actual = api._generate_endpoint({"symbol": self.SYMBOL, "extra_params": {}})
            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self):
        expected = {"symbol": "ETHBUSD"}

        async with create_client() as client:
            api = create_binanceusdsm_fetch_positions_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/positionRisk",
                    "symbol": self.SYMBOL,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_itemize_response(self, async_response_mocker):
        url = f"https://fapi.binance.com/fapi/v2/positionRisk?symbol={self.SYMBOL}"
        expected = [
            {
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1995.0,
                "size": -0.330,
                "info": self.DUMMY_RESPONSE[0],
            }
        ]
        async with create_client() as client:
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                resp = await client.get(url)
                resp_data = await resp.json()
                api = create_binanceusdsm_fetch_positions_api(client, verbose=True)

                actual = api._itemize_response(resp, resp_data)

                assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        url = f"https://fapi.binance.com/fapi/v2/positionRisk?symbol={self.SYMBOL}"
        spy_generate_endpoint = mocker.spy(PositionsFetchAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(
            PositionsFetchAPI, "_translate_parameters"
        )
        spy_itemize_response = mocker.spy(PositionsFetchAPI, "_itemize_response")
        expected_generate_endpoint = "/fapi/v2/positionRisk"
        expected_translate_parameters = {"symbol": "ETHBUSD"}
        expected_itemize_response = [
            {
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1995.0,
                "size": -0.330,
                "info": self.DUMMY_RESPONSE[0],
            }
        ]
        async with create_client() as client:
            api = create_binanceusdsm_fetch_positions_api(client, verbose=True)
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                await api.fetch_positions(self.SYMBOL)

                assert spy_generate_endpoint.spy_return == expected_generate_endpoint
                assert (
                    spy_translate_parameters.spy_return == expected_translate_parameters
                )
                assert spy_itemize_response.spy_return == expected_itemize_response
