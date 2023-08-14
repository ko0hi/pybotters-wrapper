from __future__ import annotations
from typing import Any, Callable

import aiohttp

import pybotters
from .periodic_executor import PeriodicExecutor
from ...core import APIWrapper


async def _jsonify_handler(item: aiohttp.ClientResponse) -> any:
    try:
        return await item.json()
    except aiohttp.ContentTypeError:
        return item


class Poller(PeriodicExecutor):
    def __init__(
        self,
        client_or_api: pybotters.Client | APIWrapper,
        url: str,
        interval: int | float,
        params: dict | Callable | None = None,
        handler: Callable | None = None,
        history: int = 999,
        method: str = "GET",
    ):
        super(Poller, self).__init__(
            client_or_api.request,
            params,
            interval,
            handler or _jsonify_handler,
            history,
        )
        self._client_or_api = client_or_api
        self._url = url
        self._method = method

    async def _call(self, params: dict) -> Any:
        return await self._fn(**params)

    async def _get_params(self):
        # query / body
        params_or_data = await super()._get_params()

        if isinstance(self._client_or_api, pybotters.Client):
            params: dict[str, str | dict] = {
                "method": self._method,
                "url": self._url,
            }
            if self._method == "GET":
                params["params"] = params_or_data
            else:
                params["body"] = params_or_data
        else:
            params = {
                "url": self._url,
                "method": self._method,
                "params_or_data": params_or_data,
            }

        return params
