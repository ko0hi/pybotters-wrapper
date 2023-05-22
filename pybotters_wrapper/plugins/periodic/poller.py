from typing import Callable

import aiohttp

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
            api: APIWrapper,
            url: str,
            interval: int,
            params: dict | Callable = None,
            handler: Callable = None,
            history: int = 999,
            method: str = "GET",
    ):
        super(Poller, self).__init__(
            api.request,
            params,
            interval,
            handler or _jsonify_handler,
            history,
        )
        self._api_or_client = api
        self._url = url
        self._method = method

    async def _get_params(self):
        # query / body
        params_or_data = await super()._get_params()

        params = {
            "url": self._url,
            "method": self._method,
            "params_or_data": params_or_data,
        }

        return params
