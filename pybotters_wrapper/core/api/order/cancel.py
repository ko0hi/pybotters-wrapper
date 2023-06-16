from typing import Any, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .order_api import OrderAPI
from .order_api_builder import OrderAPIBuilder
from ...typedefs import TEndpoint, TOrderId, TSymbol


class CancelOrderAPIResponse(NamedTuple):
    order_id: str | None
    resp: ClientResponse | None = None
    data: Any = None


class CancelOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    order_id: str
    extra_params: dict


class CancelOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    order_id: str
    extra_params: dict


class CancelOrderAPIWrapResponseParameters(TypedDict):
    order_id: str | None
    resp: ClientResponse
    data: Any


class CancelOrderAPI(
    OrderAPI[
        CancelOrderAPIResponse,
        CancelOrderAPIGenerateEndpointParameters,
        CancelOrderAPITranslateParametersParameters,
        CancelOrderAPIWrapResponseParameters,
    ]
):
    async def cancel_order(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> CancelOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            {"symbol": symbol, "order_id": order_id, "extra_params": extra_params}
        )
        parameters = self._translate_parameters(
            {
                "endpoint": endpoint,
                "symbol": symbol,
                "order_id": order_id,
                "extra_params": extra_params,
            }
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        return self._wrap_response({"order_id": order_id, "resp": resp, "data": data})


class CancelOrderAPIBuilder(
    OrderAPIBuilder[
        CancelOrderAPI,
        CancelOrderAPIGenerateEndpointParameters,
        CancelOrderAPITranslateParametersParameters,
        CancelOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(CancelOrderAPIBuilder, self).__init__(
            CancelOrderAPI, CancelOrderAPIResponse
        )
