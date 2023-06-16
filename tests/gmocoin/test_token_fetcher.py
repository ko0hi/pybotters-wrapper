import pytest

import pybotters_wrapper as pbw
from pybotters_wrapper.gmocoin.token_fetcher import GMOCoinTokenFetcher


@pytest.mark.asyncio
@pytest.mark.skip(reason="Access to the real API.")
async def test_fetch_token():
    async with pbw.create_client() as client:
        token_fetcher = GMOCoinTokenFetcher(client)
        token = token_fetcher.fetch()
        assert token is not None
        assert token_fetcher._update_task is not None
