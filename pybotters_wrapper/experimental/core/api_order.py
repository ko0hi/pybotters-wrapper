from typing import NamedTuple, Callable

from aiohttp.client import ClientResponse
from requests import Response

from .api_client import APIClient
from .._typedefs import TRequsetMethod


class OrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    resp_data: dict | None = None

    @property
    def status(self) -> int:
        if self.resp is None:
            return -1
        else:
            return self.resp.status


class OrderAPI:
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        *,
        order_id_key: str,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
    ):
        self._api_client = api_client
        self._method = method
        self._order_id_key = order_id_key
        self._order_id_extractor = order_id_extractor

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

    def _extract_order_id(
        self,
        resp: ClientResponse,
        resp_data: dict,
    ) -> str | None:
        if self._order_id_extractor is not None:
            return self._order_id_extractor(resp, resp_data, self._order_id_key)
        else:
            return self._default_order_id_extractor(resp, resp_data, self._order_id_key)

    @classmethod
    def _default_order_id_extractor(
        cls, resp: ClientResponse, resp_data: dict, order_id_key: str
    ) -> str | None:
        if resp.status == 200:
            order_id = resp_data
            for k in order_id_key.split("."):
                order_id = order_id[k]
            return str(order_id)
        else:
            return None

    @classmethod
    def _wrap_response(
        cls, order_id: str, resp: ClientResponse, resp_data: dict
    ) -> OrderAPIResponse:
        return OrderAPIResponse(order_id, resp, resp_data)
