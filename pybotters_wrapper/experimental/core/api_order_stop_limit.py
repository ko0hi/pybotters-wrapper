from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .._typedefs import (
    TEndpoint,
    TSymbol,
    TSide,
    TPrice,
    TSize,
    TTrigger,
)
from ..core import OrderAPI


class StopLimitOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class StopLimitOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopLimitOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    trigger: TPrice
    extra_params: dict


class StopLimitOrderAPIWrapResponseParameters(TypedDict):
    order_id: str
    resp: ClientResponse
    resp_data: dict


class StopLimitOrderAPI(
    OrderAPI[
        StopLimitOrderAPIResponse,
        StopLimitOrderAPIGenerateEndpointParameters,
        StopLimitOrderAPITranslateParametersParameters,
        StopLimitOrderAPIWrapResponseParameters,
    ]
):
    async def stop_limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> StopLimitOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            StopLimitOrderAPIGenerateEndpointParameters(
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                trigger=trigger,
                extra_params=extra_params,
            )
        )
        parameters = self._translate_parameters(
            StopLimitOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                trigger=trigger,
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
            StopLimitOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, resp_data=resp_data
            )
        )
