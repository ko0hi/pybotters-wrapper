from typing import TypedDict

from .typing import TOrderId, TPrice, TSide, TSize, TSymbol, TTimestamp


class TickerItem(TypedDict):
    symbol: TSymbol
    price: TPrice


class TradesItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp


class OrderbookItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize


class ExecutionItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    timestamp: TTimestamp


class OrderItem(TypedDict):
    id: TOrderId
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
    type: str


class PositionItem(TypedDict):
    symbol: TSymbol
    side: TSide
    price: TPrice
    size: TSize
