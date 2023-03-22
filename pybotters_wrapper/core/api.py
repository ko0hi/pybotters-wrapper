from __future__ import annotations

from typing import NamedTuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import RequsetMethod, Side

import aiohttp
import pybotters
import requests
from loguru import logger
from pybotters_wrapper.utils.mixins import ExchangeMixin, LoggingMixin


class OrderResponse(NamedTuple):
    order_id: str
    resp: aiohttp.ClientResponse
    resp_data: Optional[dict] = None

    @property
    def status(self):
        return self.resp.status

    def is_success(self):
        return self.resp.status == 200


class API(ExchangeMixin, LoggingMixin):
    BASE_URL: str = None
    _ORDER_ENDPOINT: str = None
    _MARKET_ENDPOINT: str = None
    _LIMIT_ENDPOINT: str = None
    _STOP_MARKET_ENDPOINT: str = None
    _STOP_LIMIT_ENDPOINT: str = None
    _CANCEL_ENDPOINT: str = None
    _ORDER_ID_KEY: str = None
    _MARKET_REQUEST_METHOD: RequsetMethod = "POST"
    _LIMIT_REQUEST_METHOD: RequsetMethod = "POST"
    _CANCEL_REQUEST_METHOD: RequsetMethod = "DELETE"
    _STOP_MARKET_REQUEST_METHOD: RequsetMethod = "POST"
    _STOP_LIMIT_REQUEST_METHOD: RequsetMethod = "POST"

    def __init__(self, client: pybotters.Client, verbose: bool = False, **kwargs):
        self._client = client
        self._verbose = verbose

    async def request(
        self,
        method: RequsetMethod,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        url = self._attach_base_url(url, kwargs.pop("base_url", True))
        return await self._client.request(
            method, url, params=params, data=data, **kwargs
        )

    async def get(self, url: str, *, params: Optional[dict] = None, **kwargs):
        return await self.request("GET", url, params=params, data=None, **kwargs)

    async def post(self, url: str, *, data: Optional[dict] = None, **kwargs):
        return await self.request("POST", url, params=None, data=data, **kwargs)

    async def put(self, url: str, *, data: Optional[dict] = None, **kwargs):
        return await self.request("PUT", url, params=None, data=data, **kwargs)

    async def delete(self, url: str, *, data: Optional[dict] = None, **kwargs):
        return await self.request("DELETE", url, params=None, data=data, **kwargs)

    def srequest(
        self,
        method: RequsetMethod,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        # TODO: 網羅的なテスト
        # aiohttp.ClientSession._requestをpybotters.Clientから呼び出した時の処理を抜き出している
        sess: aiohttp.ClientSession = self._client._session
        req = sess._request_class(
            method,
            sess._build_url(self._attach_base_url(url, kwargs.pop("base_url", True))),
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
        return requests.request(
            method=req.method, url=str(req.url), data=data, headers=headers, **kwargs
        )

    def sget(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.srequest("GET", url, params=params, data=data, **kwargs)

    def spost(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.srequest("POST", url, params=params, data=data, **kwargs)

    def sput(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.srequest("PUT", url, params=params, data=data, **kwargs)

    def sdelete(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        return self.srequest("DELETE", url, params=params, data=data, **kwargs)

    @logger.catch
    async def market_order(
        self,
        symbol: str,
        side: Side,
        size: float,
        *,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_market_endpoint(symbol, side, size, **kwargs)
        p = self._make_market_order_parameter(endpoint, symbol, side, size)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"market order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_market_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"market order response: {resp} {resp_data}", verbose=self._verbose)
        order_id = self._make_market_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_market_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def limit_order(
        self,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        *,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_limit_endpoint(symbol, side, price, size, **kwargs)
        p = self._make_limit_order_parameter(endpoint, symbol, side, price, size)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"limit order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_limit_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"limit order response: {resp} {resp_data}", verbose=self._verbose)
        order_id = self._make_limit_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_limit_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
        *,
        request_params: dict = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_cancel_endpoint(symbol, order_id, **kwargs)
        p = self._make_cancel_order_parameter(endpoint, symbol, order_id)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"cancel order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_cancel_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"cancel order response: {resp} {resp_data}", verbose=self._verbose)
        wrapped_resp = self._make_cancel_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def stop_market_order(
        self,
        symbol: str,
        side: Side,
        size: float,
        trigger: float,
        *,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_stop_market_endpoint(symbol, side, size, trigger)
        p = self._make_stop_market_order_parameter(
            endpoint, symbol, side, size, trigger
        )
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"stop market order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_stop_market_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(
            f"stop market order response: {resp} {resp_data}", verbose=self._verbose
        )
        order_id = self._make_stop_market_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_stop_market_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def stop_limit_order(
        self,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        trigger: float,
        *,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_stop_limit_endpoint(symbol, side, price, size, trigger)
        p = self._make_stop_limit_order_parameter(
            endpoint, symbol, side, price, size, trigger
        )
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"stop limit order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_stop_limit_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(
            f"stop limit order response: {resp} {resp_data}", verbose=self._verbose
        )
        order_id = self._make_stop_limit_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_stop_limit_order_response(resp, resp_data, order_id)
        return wrapped_resp

    def _attach_base_url(self, url: str, base_url: str = False) -> str:
        if base_url:
            base_url = self._get_base_url(url)
            return url if self._client._base_url else base_url + url
        else:
            return url

    def _get_base_url(self, url: str):
        if self.BASE_URL is None:
            raise RuntimeError(f"BASE_URL is not defined: {self.exchange}")
        return self.BASE_URL

    def _make_market_endpoint(
        self, symbol: str, side: Side, size: float, **kwargs
    ) -> str:
        return self._MARKET_ENDPOINT or self._ORDER_ENDPOINT

    def _make_limit_endpoint(
        self, symbol: str, side: Side, price: float, size: float, **kwargs
    ) -> str:
        return self._LIMIT_ENDPOINT or self._ORDER_ENDPOINT

    def _make_cancel_endpoint(self, symbol: str, order_id: str, **kwargs) -> str:
        return self._CANCEL_ENDPOINT or self._ORDER_ENDPOINT

    def _make_stop_market_endpoint(
        self, symbol: str, side: Side, size: float, trigger: float, **kwargs
    ) -> str:
        return self._STOP_MARKET_ENDPOINT or self._ORDER_ENDPOINT

    def _make_stop_limit_endpoint(
        self,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        trigger: float,
        **kwargs,
    ) -> str:
        return self._STOP_LIMIT_ENDPOINT or self._ORDER_ENDPOINT

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> Optional[dict]:
        raise NotImplementedError

    def _make_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        price: float,
        size: float,
    ) -> Optional[dict]:
        raise NotImplementedError

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> Optional[dict]:
        raise NotImplementedError

    def _make_stop_market_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        size: float,
        trigger: float,
    ) -> Optional[dict]:
        raise NotImplementedError

    def _make_stop_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        trigger: float,
    ) -> Optional[dict]:
        raise NotImplementedError

    def _make_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        *,
        order_id_key: str,
    ) -> Optional[str]:
        if resp.status == 200:
            # 200が返って来た場合、レスポンスの中にorder_idが含まれるものとする。
            order_id = resp_data
            order_id_key = order_id_key or self._ORDER_ID_KEY
            assert order_id_key is not None
            for k in order_id_key.split("."):
                order_id = order_id[k]
            return str(order_id)
        else:
            self.log(f"order failed: {resp} {resp_data}", "error")
            return None

    def _make_market_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        *,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    def _make_limit_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        *,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    def _make_stop_market_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        *,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    def _make_stop_limit_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        *,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    async def _make_request(
        self,
        method: RequsetMethod,
        endpoint: str,
        params_or_data: Optional[dict],
        **kwargs,
    ) -> tuple[aiohttp.ClientResponse, any]:
        params = {"method": method, "url": endpoint}
        if method == "GET":
            params["params"] = params_or_data
        else:
            params["data"] = params_or_data

        params.update(kwargs)

        resp = await self.request(**params)
        resp_data = await resp.json()
        return resp, resp_data

    async def _make_market_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        return await self._make_request(
            self._MARKET_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_limit_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        return await self._make_request(
            self._LIMIT_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_cancel_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        return await self._make_request(
            self._CANCEL_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_stop_market_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        return await self._make_request(
            self._STOP_MARKET_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_stop_limit_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        return await self._make_request(
            self._STOP_LIMIT_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    def _make_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return OrderResponse(order_id, resp, resp_data)

    def _make_market_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_limit_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_cancel_order_response(
        self,
        resp: aiohttp.ClientResponse,
        resp_data: dict,
        order_id: str,
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_stop_market_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_stop_limit_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    @classmethod
    def _add_kwargs_to_data(cls, data: Optional[dict], **kwargs):
        data = data or {}
        return {**data, **kwargs}
