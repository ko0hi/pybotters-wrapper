import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(positions_fetch_api_tester):
    return positions_fetch_api_tester(
        symbol="FX_BTC_JPY",
        url="https://api.bitflyer.com/v1/me/getpositions?product_code=FX_BTC_JPY",
        factory_method=pbw.create_factory("bitflyer").create_positions_fetch_api,
        dummy_response=[
            {
                "product_code": "FX_BTC_JPY",
                "side": "BUY",
                "price": 36000,
                "size": 10,
                "commission": 0,
                "swap_point_accumulate": -35,
                "require_collateral": 120000,
                "open_date": "2015-11-03T10:04:45.011",
                "leverage": 3,
                "pnl": 965,
                "sfd": -0.5,
            }
        ],
        expected_generate_endpoint="/v1/me/getpositions",
        expected_translate_parameters={
            "product_code": "FX_BTC_JPY",
        },
        expected_itemize_response=[
            {
                "symbol": "FX_BTC_JPY",
                "side": "BUY",
                "price": 36000.0,
                "size": 10.0,
            },
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
