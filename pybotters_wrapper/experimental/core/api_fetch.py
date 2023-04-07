import asyncio
from typing import Callable, Awaitable

from . import APIClient
from .._typedefs import TRequsetMethod

from aiohttp.client import ClientResponse


class FetchAPI:
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        self._api_client = api_client
        self._method = method
        self._response_decoder = response_decoder

    async def request(
        self, url: str, params_or_data: dict = None, **kwargs
    ) -> ClientResponse:
        if self._method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return await self._api_client.request(self._method, url, **kwargs)

    def srequest(self, url: str, params_or_data: dict = None, **kwargs) -> Response:
        if self._method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data
        return self._api_client.srequest(self._method, url, **kwargs)

    async def _decode_response(self, resp: ClientResponse) -> dict | list:
        if self._response_decoder is None:
            return await resp.json()
        else:
            if asyncio.iscoroutinefunction(self._response_decoder):
                return await self._response_decoder(resp)
            else:
                return self._response_decoder(resp)
