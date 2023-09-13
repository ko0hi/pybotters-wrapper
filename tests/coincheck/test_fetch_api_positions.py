import pandas as pd
import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(positions_fetch_api_tester):
    return positions_fetch_api_tester(
        symbol="btc_jpy",
        url="https://coincheck.com/api/accounts/balance",
        factory_method=pbw.create_factory("coincheck").create_positions_fetch_api,
        dummy_response={
            "success": True,
            "jpy": "0.8401",
            "btc": "7.75052654",
            "jpy_reserved": "3000.0",
            "btc_reserved": "3.5002",
            "jpy_lend_in_use": "0",
            "btc_lend_in_use": "0.3",
            "jpy_lent": "0",
            "btc_lent": "1.2",
            "jpy_debt": "0",
            "btc_debt": "0",
        },
        expected_generate_endpoint="/api/accounts/balance",
        expected_translate_parameters={},
        expected_itemize_response=[
            {"price": 0.0, "side": "BUY", "size": 0.8401, "symbol": "jpy"},
            {"price": 0.0, "side": "BUY", "size": 7.75052654, "symbol": "btc"},
        ],
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_fetch(tester):
    resp, data = await tester.test_fetch()
    print(data)


@pytest.mark.asyncio
@pytest.mark.skip
async def test_api(tester):
    resp = await tester.test_api()
    print(resp)


@pytest.mark.asyncio
async def test_generate_endpoint(tester):
    await tester.test_generate_endpoint()


@pytest.mark.asyncio
async def test_translate_parameters(tester):
    await tester.test_translate_parameters()


@pytest.mark.asyncio
async def test_itemize_response(tester):
    await tester.test_itemize_response()


@pytest.mark.asyncio
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
