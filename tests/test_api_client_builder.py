import pytest

import pybotters_wrapper as pbw
from pybotters_wrapper.core.api_client_builder import APIClientBuilder
from pybotters_wrapper.core.exchange_property import ExchangeProperty


@pytest.mark.asyncio
async def test_api_client_builder():
    builder = APIClientBuilder()

    eprop = ExchangeProperty({"base_url": "https://sample.com", "exchange": "sample"})

    async with pbw.create_client() as client:
        api_client = (
            builder.set_client(client)
            .set_exchange_property(eprop)
            .set_verbose(True)
            .get()
        )

        assert "https://sample.com" == api_client._eprop.base_url
        assert "sample" == api_client._eprop.exchange


@pytest.mark.asyncio
async def test_api_client_builder_fail():
    builder = APIClientBuilder()

    async with pbw.create_client() as client:
        with pytest.raises(ValueError) as e:
            builder.set_client(client).set_verbose(True).get()

        assert "Missing required fields: exchange_property" == str(e.value)
