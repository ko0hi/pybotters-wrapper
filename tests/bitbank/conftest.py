import pytest_mock
import pytest


@pytest.fixture(autouse=True)
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.bitbank.price_size_precision_fetcher.bitbankPriceSizePrecisionFetcher.fetch_precisions",
        return_value={"price": {"btc_jpy": 0}, "size": {"btc_jpy": 3}},
    )
