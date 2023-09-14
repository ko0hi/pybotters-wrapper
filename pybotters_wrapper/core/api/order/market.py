from typing import Any, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from ...typedefs import TEndpoint, TSide, TSize, TSymbol
from .order_api import OrderAPI
from .order_api_builder import OrderAPIBuilder


class MarketOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse
    data: Any = None


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
    order_id: str | None
    resp: ClientResponse
    data: Any


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
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> MarketOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            {"symbol": symbol, "side": side, "size": size, "extra_params": extra_params}
        )
        parameters = self._translate_parameters(
            {
                "endpoint": endpoint,
                "symbol": symbol,
                "side": side,
                "size": size,
                "extra_params": extra_params,
            }
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, data)
        return self._wrap_response({"order_id": order_id, "resp": resp, "data": data})


class MarketOrderAPIBuilder(
    OrderAPIBuilder[
        MarketOrderAPI,
        MarketOrderAPIGenerateEndpointParameters,
        MarketOrderAPITranslateParametersParameters,
        MarketOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(MarketOrderAPIBuilder, self).__init__(
            MarketOrderAPI, MarketOrderAPIResponse
        )
