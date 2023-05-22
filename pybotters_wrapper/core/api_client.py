from __future__ import annotations

from json import JSONDecodeError

import aiohttp
import pybotters
import requests
from aiohttp.client import ClientResponse
from loguru import logger
from requests import Response

from .exchange_property import ExchangeProperty
from .._typedefs import TRequestMethod


async def format_aiohttp_response(
        resp: ClientResponse, method: str, url: str, params: dict
) -> str:
    if resp.status == 200:
        return f"Request: [{resp.status}] {method} {url} with {params}"
    else:
        try:
            data = await resp.json()
        except JSONDecodeError:
            data = None
        return f"Request failed: [{resp.status}] {method} {url} with {params} -> {data}"


def format_requests_response(
        resp: Response, method: str, url: str, params: dict
) -> str:
    if resp.status_code == 200:
        return f"Request: [{resp.status_code}] {method} {url} with {params}"
    else:
        try:
            data = resp.json()
        except JSONDecodeError:
            data = None
        return f"Request failed: [{resp.status_code}] {method} {url} with {params} -> {data}"


class APIClient:
    def __init__(
            self,
            client: pybotters.Client,
            verbose: bool = False,
            *,
            exchange_property: ExchangeProperty,
    ):
        self._client = client
        self._verbose = verbose
        self._eprop = exchange_property
        self._validate()

    async def request(
            self,
            method: TRequestMethod,
            url: str,
            *,
            params_or_data: dict | None = None,
            **kwargs,
    ) -> ClientResponse:
        url = self._attach_base_url(url)
        if method == "GET":
            kwargs["params"] = params_or_data
        else:
            kwargs["data"] = params_or_data

        resp = await self._client.request(method, url, **kwargs)
        await self._log_aiohttp_response(resp, method, url, kwargs)
        return resp

    async def get(
            self, url: str, *, params: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("GET", url, params_or_data=params, **kwargs)

    async def post(
            self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("POST", url, params_or_data=data, **kwargs)

    async def put(
            self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("PUT", url, params_or_data=data, **kwargs)

    async def delete(
            self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self.request("DELETE", url, params_or_data=data, **kwargs)

    def srequest(
            self,
            method: TRequestMethod,
            url: str,
            *,
            params_or_data: dict | None = None,
            **kwargs,
    ) -> Response:
        # TODO: 網羅的なテスト
        # aiohttp.ClientSession._requestをpybotters.Clientから呼び出した時の処理を抜き出している
        sess: aiohttp.ClientSession = self._client._session

        if method == "GET":
            params = params_or_data
            data = None
        else:
            params = None
            data = params_or_data

        req = sess._request_class(
            method,
            sess._build_url(self._attach_base_url(url)),
            params=params,
            data=data,
            headers=sess._prepare_headers([]),
            session=sess,
            auth=pybotters.auth.Auth,
        )
        headers = {str(k): str(v) for (k, v) in dict(req.headers).items()}
        if isinstance(req.body, aiohttp.payload.BytesPayload):
            data = req.body._value
        else:
            data = req.body
        # paramsはurlに埋め込まれている
        resp = requests.request(
            method=req.method, url=str(req.url), data=data, headers=headers, **kwargs
        )

        self._log_request_response(resp, req.method, str(req.url), data)
        return resp

    def sget(self, url: str, *, params: dict | None = None, **kwargs) -> Response:
        return self.srequest("GET", url, params_or_data=params, **kwargs)

    def spost(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("POST", url, params_or_data=data, **kwargs)

    def sput(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("PUT", url, params_or_data=data, **kwargs)

    def sdelete(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self.srequest("DELETE", url, params_or_data=data, **kwargs)

    def _attach_base_url(self, url: str) -> str:
        return self._eprop.base_url + url

    def _validate(self):
        if self._client._base_url != "":
            raise ValueError("Client should not have base_url")

    def _log(self, msg: str, level: str = "DEBUG"):
        if self._verbose:
            logger.log(level, msg)

    async def _log_aiohttp_response(
            self, resp: ClientResponse, method: str, url: str, params: dict
    ):
        msg = await format_aiohttp_response(resp, method, url, params)
        self._log(msg) if resp.status == 200 else logger.error(msg)

    def _log_request_response(
            self, resp: Response, method: str, url: str, params: dict
    ):
        msg = format_requests_response(resp, method, url, params)
        self._log(msg) if resp.status_code == 200 else logger.error(msg)
