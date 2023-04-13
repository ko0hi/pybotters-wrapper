import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.core import OrdersFetchAPI
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_fetch_orders_api,
)


class TestBinanceUSDSMFetchAPIOrders:
    SYMBOL = "ETHBUSD"
    DUMMY_RESPONSE = [
        {
            "orderId": 26799019660,
            "symbol": "ETHBUSD",
            "status": "NEW",
            "clientOrderId": "VKokEwY33pRhGbs4CnFEb9",
            "price": "1978.02",
            "avgPrice": "0",
            "origQty": "0.330",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "1980",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681382301047,
            "updateTime": 1681382301047,
        },
        {
            "orderId": 26807427868,
            "symbol": "ETHBUSD",
            "status": "NEW",
            "clientOrderId": "FBY2slHY1PPE04f40o6zmd",
            "price": "1988.01",
            "avgPrice": "0",
            "origQty": "0.330",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "1990",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681388511335,
            "updateTime": 1681388511335,
        },
    ]

    @pytest.mark.asyncio
    async def test_generate_endpoint(self):
        expected = "/fapi/v1/openOrders"
        async with create_client() as client:
            api = create_binanceusdsm_fetch_orders_api(client, verbose=True)
            actual = api._generate_endpoint({"symbol": self.SYMBOL, "extra_params": {}})
            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self):
        expected = {"symbol": "ETHBUSD"}

        async with create_client() as client:
            api = create_binanceusdsm_fetch_orders_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/openOrders",
                    "symbol": self.SYMBOL,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_itemize_response(self, async_response_mocker):
        url = f"https://fapi.binance.com/fapi/v1/openOrders?symbol={self.SYMBOL}"
        expected = [
            {
                "id": "26799019660",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1978.02,
                "size": 0.33,
                "type": "STOP",
                "info": self.DUMMY_RESPONSE[0],
            },
            {
                "id": "26807427868",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1988.01,
                "size": 0.33,
                "type": "STOP",
                "info": self.DUMMY_RESPONSE[1],
            },
        ]
        async with create_client() as client:
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                resp = await client.get(url)
                resp_data = await resp.json()
                api = create_binanceusdsm_fetch_orders_api(client, verbose=True)

                actual = api._itemize_response(resp, resp_data)

                assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(self, mocker: pytest_mock.MockerFixture):
        url = f"https://fapi.binance.com/fapi/v1/openOrders?symbol={self.SYMBOL}"
        spy_generate_endpoint = mocker.spy(OrdersFetchAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(OrdersFetchAPI, "_translate_parameters")
        spy_itemize_response = mocker.spy(OrdersFetchAPI, "_itemize_response")
        expected_generate_endpoint = "/fapi/v1/openOrders"
        expected_translate_parameters = {"symbol": "ETHBUSD"}
        expected_itemize_response = [
            {
                "id": "26799019660",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1978.02,
                "size": 0.33,
                "type": "STOP",
                "info": self.DUMMY_RESPONSE[0],
            },
            {
                "id": "26807427868",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1988.01,
                "size": 0.33,
                "type": "STOP",
                "info": self.DUMMY_RESPONSE[1],
            },
        ]
        async with create_client() as client:
            api = create_binanceusdsm_fetch_orders_api(client, verbose=True)
            with aioresponses() as m:
                m.get(url, payload=self.DUMMY_RESPONSE)
                await api.fetch_orders(self.SYMBOL)

                assert spy_generate_endpoint.spy_return == expected_generate_endpoint
                assert (
                    spy_translate_parameters.spy_return == expected_translate_parameters
                )
                assert spy_itemize_response.spy_return == expected_itemize_response
