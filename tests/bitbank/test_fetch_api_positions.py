import pandas as pd
import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(positions_fetch_api_tester):
    return positions_fetch_api_tester(
        symbol="btc_jpy",
        url="https://api.bitbank.cc/v1/user/assets",
        factory_method=pbw.create_factory("bitbank").create_positions_fetch_api,
        dummy_response={
            "success": 1,
            "data": {
                "assets": [
                    {
                        "asset": "jpy",
                        "amount_precision": 4,
                        "onhand_amount": "1000000",
                        "locked_amount": "200000",
                        "free_amount": "800000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": {
                            "threshold": "30000.0000",
                            "under": "550.0000",
                            "over": "770.0000",
                        },
                    },
                    {
                        "asset": "btc",
                        "amount_precision": 8,
                        "onhand_amount": "1",
                        "locked_amount": "0.00000000",
                        "free_amount": "1",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.00060000",
                    },
                    {
                        "asset": "ltc",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.00100000",
                    },
                    {
                        "asset": "xrp",
                        "amount_precision": 6,
                        "onhand_amount": "0.000000",
                        "locked_amount": "0.000000",
                        "free_amount": "0.000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.150000",
                    },
                    {
                        "asset": "eth",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.00500000",
                    },
                    {
                        "asset": "mona",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.00100000",
                    },
                    {
                        "asset": "bcc",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.00100000",
                    },
                    {
                        "asset": "xlm",
                        "amount_precision": 7,
                        "onhand_amount": "0.0000000",
                        "locked_amount": "0.0000000",
                        "free_amount": "0.0000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.0100000",
                    },
                    {
                        "asset": "qtum",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.01000000",
                    },
                    {
                        "asset": "bat",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "45.00000000",
                    },
                    {
                        "asset": "omg",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "5.00000000",
                    },
                    {
                        "asset": "xym",
                        "amount_precision": 6,
                        "onhand_amount": "0.000000",
                        "locked_amount": "0.000000",
                        "free_amount": "0.000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "2.000000",
                    },
                    {
                        "asset": "link",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "1.10000000",
                    },
                    {
                        "asset": "mkr",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.02000000",
                    },
                    {
                        "asset": "boba",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "17.00000000",
                    },
                    {
                        "asset": "enj",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "14.00000000",
                    },
                    {
                        "asset": "matic",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "19.00000000",
                    },
                    {
                        "asset": "dot",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.05000000",
                    },
                    {
                        "asset": "doge",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "5.00000000",
                    },
                    {
                        "asset": "astr",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "2.50000000",
                    },
                    {
                        "asset": "ada",
                        "amount_precision": 6,
                        "onhand_amount": "0.000000",
                        "locked_amount": "0.000000",
                        "free_amount": "0.000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "1.000000",
                    },
                    {
                        "asset": "avax",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "0.01000000",
                    },
                    {
                        "asset": "axs",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "1.60000000",
                    },
                    {
                        "asset": "flr",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": True,
                        "stop_withdrawal": True,
                        "withdrawal_fee": "5.00000000",
                    },
                    {
                        "asset": "sand",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "21.00000000",
                    },
                    {
                        "asset": "gala",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "200.00000000",
                    },
                    {
                        "asset": "chz",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "58.00000000",
                    },
                    {
                        "asset": "ape",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "1.50000000",
                    },
                    {
                        "asset": "oas",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "30.00000000",
                    },
                    {
                        "asset": "mana",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "13.00000000",
                    },
                    {
                        "asset": "grt",
                        "amount_precision": 8,
                        "onhand_amount": "0.00000000",
                        "locked_amount": "0.00000000",
                        "free_amount": "0.00000000",
                        "stop_deposit": False,
                        "stop_withdrawal": False,
                        "withdrawal_fee": "92.00000000",
                    },
                ]
            },
        },
        expected_generate_endpoint="/user/assets",
        expected_translate_parameters={},
        expected_itemize_response=[
            {
                "symbol": "jpy",
                "price": 0,
                "side": "BUY",
                "size": 800000.0,
            },
            {"symbol": "btc", "price": 0, "side": "BUY", "size": 1.0},
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
