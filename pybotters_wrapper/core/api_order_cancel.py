from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .api_order import OrderAPI
from .._typedefs import TEndpoint, TOrderId, TSymbol


class CancelOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    data: dict | None = None


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
    order_id: str
    resp: ClientResponse
    data: dict


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
            extra_params: dict = None,
            request_params: dict = None,
    ) -> CancelOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            CancelOrderAPIGenerateEndpointParameters(
                symbol=symbol, order_id=order_id, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            CancelOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                order_id=order_id,
                extra_params=extra_params,
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, data)
        return self._wrap_response(
            CancelOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, data=data
            )
        )
