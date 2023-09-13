import pytest
import pytest_mock


@pytest.fixture(autouse=True)
def patch_fetch_precisions(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.gmocoin.price_size_precision_fetcher.GMOCoinPriceSizePrecisionFetcher.fetch_precisions",
        return_value={
            "price": {"BTC_JPY": 1},
            "size": {"BTC_JPY": 2},
        },
    )
