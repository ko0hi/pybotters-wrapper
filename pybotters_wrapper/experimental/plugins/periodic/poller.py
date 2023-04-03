from typing import Callable

import aiohttp
import pybotters
from pybotters_wrapper.core import API

from ._base import PeriodicPlugin


async def _jsonify_handler(item: aiohttp.ClientResponse) -> any:
    try:
        return await item.json()
    except aiohttp.ContentTypeError:
        return item


class Poller(PeriodicPlugin):
    def __init__(
        self,
        api_or_client: pybotters.Client | API,
        url: str,
        interval: int,
        params: dict | Callable = None,
        handler: Callable = None,
        history: int = 999,
        method: str = "GET",
    ):
        super(Poller, self).__init__(
            api_or_client.request,
            params,
            interval,
            handler or _jsonify_handler,
            history,
        )
        self._api_or_client = api_or_client
        self._url = url
        self._method = method

    async def _get_params(self):
        # query / body
        params_or_data = await super()._get_params()

        params = {"url": self._url, "method": self._method}
        if self._method == "GET":
            params["params"] = params_or_data
        else:
            params["data"] = params_or_data

        return params
