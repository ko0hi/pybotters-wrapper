import pytest
import pytest_mock

import pybotters_wrapper as pbw
from pybotters_wrapper.core import APIClientBuilder, ExchangeProperty


@pytest.mark.asyncio
async def test_api_client_request(mocker: pytest_mock.MockFixture):
    mock_request = mocker.patch("requests.request")
    async with pbw.create_client() as client:
        builder = APIClientBuilder()

        eprop = ExchangeProperty(
            {"base_url": "https://sample.com", "exchange": "sample"}
        )

        api_client = (
            builder.set_client(client)
            .set_exchange_property(eprop)
            .set_verbose(True)
            .get()
        )

        api_client.sget("/v1/ticker")
        assert "GET" == mock_request.call_args.kwargs["method"]
        assert "https://sample.com/v1/ticker" == mock_request.call_args.kwargs["url"]


@pytest.mark.asyncio
async def test_api_client_request_with_base_url():
    async with pbw.create_client(base_url="https://sample.com") as client:
        builder = APIClientBuilder()

        eprop = ExchangeProperty(
            {"base_url": "https://sample.com", "exchange": "sample"}
        )

        with pytest.raises(ValueError) as e:
            (
                builder.set_client(client)
                .set_exchange_property(eprop)
                .set_verbose(True)
                .get()
            )

        assert str(e.value) == "Client should not have base_url"
