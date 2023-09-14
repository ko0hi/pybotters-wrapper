from typing import NotRequired, TypedDict

from .typing import TOrderId, TPrice, TSide, TSize, TSymbol, TTimestamp


class TickerItem(TypedDict):
    symbol: TSymbol
    price: TPrice
    info: NotRequired[dict]


class TradesItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp
    info: NotRequired[dict]


class OrderbookItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    info: NotRequired[dict]


class ExecutionItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp
    info: NotRequired[dict]


class OrderItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    type: str
    trigger: NotRequired[TPrice]
    info: NotRequired[dict]


class PositionItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    info: NotRequired[dict]
