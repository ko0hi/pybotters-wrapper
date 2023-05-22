from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from pybotters_wrapper._typedefs import TEndpoint, TSide, TSize, TSymbol
from pybotters_wrapper.core.api_order import OrderAPI


class MarketOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    data: dict | None = None


class MarketOrderAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    side: TSide
    size: TSize
    extra_params: dict


class MarketOrderAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    side: TSide
    size: TSize
    extra_params: dict


class MarketOrderAPIWrapResponseParameters(TypedDict):
    order_id: str
    resp: ClientResponse
    data: dict


class MarketOrderAPI(
    OrderAPI[
        MarketOrderAPIResponse,
        MarketOrderAPIGenerateEndpointParameters,
        MarketOrderAPITranslateParametersParameters,
        MarketOrderAPIWrapResponseParameters,
    ]
):
    async def market_order(
            self,
            symbol: TSymbol,
            side: TSide,
            size: TSize,
            *,
            extra_params: dict = None,
            request_params: dict = None,
    ) -> MarketOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            MarketOrderAPIGenerateEndpointParameters(
                symbol=symbol, side=side, size=size, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            MarketOrderAPITranslateParametersParameters(
                endpoint=endpoint,
                symbol=symbol,
                side=side,
                size=size,
                extra_params=extra_params,
            )
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, data)
        return self._wrap_response(
            MarketOrderAPIWrapResponseParameters(
                order_id=order_id, resp=resp, data=data
            )
        )
