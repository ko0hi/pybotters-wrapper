from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from _typedefs import TEndpoint, TSymbol, TSide, TPrice, TSize
from ..core import OrderAPI


class LimitOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class LimitOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    extra_params: dict


class LimitOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    extra_params: dict


class LimitOrderAPIWrapResponseParameters(TypedDict):
    order_id: str
    resp: ClientResponse
    resp_data: dict


class LimitOrderAPI(
    OrderAPI[
        LimitOrderAPIResponse,
        LimitOrderAPIGenerateEndpointParameters,
        LimitOrderAPITranslateParametersParameters,
        LimitOrderAPIWrapResponseParameters,
    ]
):
    async def limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> LimitOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            LimitOrderAPIGenerateEndpointParameters(
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                extra_params=extra_params,
            )
        )
        parameters = self._translate_parameters(
            LimitOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                extra_params=extra_params,
            )
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_price(parameters, symbol)
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, resp_data)
        return self._wrap_response(
            LimitOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, resp_data=resp_data
            )
        )
