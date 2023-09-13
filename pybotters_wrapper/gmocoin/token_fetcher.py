import asyncio

import pybotters
from loguru import logger

from ..core import APIClient


class GMOCoinTokenFetcher:
    def __init__(self, client: pybotters.Client):
        self._client = client
        self._token: str | None = None
        self._update_task: asyncio.Task | None = None

    def fetch(self) -> str:
        if self._token is None:
            self._token = self._fetch_token()

        if self._update_task is None:
            self._update_task = asyncio.create_task(self._auto_update_token())

        return self._token

    def _fetch_token(self) -> str:
        client = self._init_client()
        resp = client.spost("/private/v1/ws-auth")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch token: {resp.text}")
        data = resp.json()
        return data["data"]

    async def _auto_update_token(self, interval: int = 1800) -> None:
        while True:
            client = self._init_client()
            resp = client.sput(
                "/private/v1/ws-auth",
                data={"token": self._token},
            )
            logger.info(f"Updated GMOCoin's token: {resp.json()}")
            await asyncio.sleep(interval)

    def _init_client(self) -> APIClient:

        from .wrapper_factory import GMOCoinWrapperFactory

        return GMOCoinWrapperFactory.create_api_client(self._client)
