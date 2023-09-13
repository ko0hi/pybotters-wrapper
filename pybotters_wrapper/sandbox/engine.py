from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, cast

import pandas as pd
from loguru import logger

if TYPE_CHECKING:
    from .api_wrapper import SandboxAPIWrapper
    from .store_wrapper import SandboxDataStoreWrapper

from ..core import (
    APIWrapper,
    DataStoreWrapper,
    ExecutionItem,
    OrderItem,
    PositionItem,
    TradesItem,
)
from .exceptions import OrderNotFoundError


class SandboxOrderItem(OrderItem):
    timestamp: str


class SandboxEngine:
    SUFFIX = ".sandbox"
    _REGISTRY: dict[str, SandboxEngine] = {}

    def __init__(self, store: SandboxDataStoreWrapper, api: SandboxAPIWrapper):
        self._store = store
        self._api = api

        self._task = asyncio.create_task(self._matching_task())

        # store/apiから当該エンジンにアクセスできるよう参照設定
        self._store._link_to_engine(self)
        self._api._link_to_engine(self)

    def insert_order(
        self,
        symbol: str,
        side: str,
        price: float | None,
        size: float,
        type: Literal["MARKET", "LIMIT", "STOP_LIMIT", "STOP_MARKET"],
        trigger: float | None = None,
        **kwargs,
    ) -> str:
        order_item = self._create_order_item(
            symbol, side, price, size, type, trigger=trigger, **kwargs
        )
        self._store.order._insert([order_item])
        logger.info(f"new order: {order_item}")

        if type == "MARKET":
            self._handle_execution(order_item)

        return order_item["id"]

    def delete_order(self, symbol: str, order_id: str) -> None:
        order_item = self._store.order.find({"symbol": symbol, "id": order_id})
        if len(order_item) == 0:
            raise OrderNotFoundError(
                f"No order found with {symbol} and {order_id}. "
                f"Your order list: {self._store.order.find()}"
            )
        assert len(order_item) == 1
        order_item = order_item[0]
        self._store.order._delete([order_item])

    async def _matching_task(self):
        with self._store.trades.watch() as stream:
            async for change in stream:
                if change.operation == "insert":
                    trade_item = change.data
                    orders = self._store.order.find({"symbol": trade_item["symbol"]})
                    for order_item in orders:
                        if self._is_executed(order_item, trade_item):
                            self._handle_execution(order_item)

                        if self._is_triggered(order_item, trade_item):
                            self._handle_trigger(order_item)

    def _is_executed(self, order_item: OrderItem, trade_item: TradesItem) -> bool:
        if order_item["symbol"] != trade_item["symbol"]:
            return False

        if "trigger" in order_item:
            return False

        if order_item["side"] == "BUY":
            return order_item["price"] >= trade_item["price"]
        else:
            return order_item["price"] <= trade_item["price"]

    def _is_triggered(self, order_item: OrderItem, trade_item: TradesItem) -> bool:
        if order_item["symbol"] != trade_item["symbol"]:
            return False

        if order_item["type"] in ["STOP_LIMIT", "STOP_MARKET"]:
            assert "trigger" in order_item
            return (
                order_item["side"] == "BUY"
                and trade_item["price"] >= order_item["trigger"]
            ) or (
                order_item["side"] == "SELL"
                and trade_item["price"] <= order_item["trigger"]
            )
        return False

    def _handle_execution(self, order_item: SandboxOrderItem) -> None:
        logger.info("handle execution")

        # 約定履歴の挿入
        execution_item = self._create_execution_item(order_item)
        self._store.execution._insert([execution_item])
        logger.info(f"insert execution: {execution_item}")

        # ポジション状態のアップデート
        # one-side only
        position_item = self._create_position_item(execution_item)
        position_old = self._store.position.find({"symbol": order_item["symbol"]})
        self._store.position._delete(position_old)
        if position_item is not None:
            self._store.position._insert([position_item])
        position_new = self._store.position.find({"symbol": order_item["symbol"]})
        logger.info(f"update position: {position_old} => {position_new}")

        # 注文の削除
        self._store.order._delete([order_item])
        logger.info(f"delete order: {order_item}")

    def _handle_trigger(self, order_item: OrderItem) -> None:
        self.insert_order(
            order_item["symbol"],
            order_item["side"],
            order_item["price"],
            order_item["size"],
            type=order_item["type"].replace("STOP_", ""),  # type: ignore
            order_id=order_item["id"],
        )

    def _create_order_item(
        self,
        symbol: str,
        side: str,
        price: float | None,  # marketの時はNone
        size: float,
        type: Literal["LIMIT", "MARKET", "STOP_LIMIT", "STOP_MARKET"],
        order_id: str | None = None,
        trigger: float | None = None,
        **kwargs,
    ) -> SandboxOrderItem:
        if type.startswith("STOP") and trigger is None:
            raise ValueError("trigger must be specified for STOP_MARKET order")

        kwargs = kwargs or {}
        kwargs["timestamp"] = pd.Timestamp.utcnow()
        if trigger:
            kwargs["trigger"] = trigger

        order_id = order_id or str(uuid.uuid4())
        order_item = self._store.order._itemize(
            id=order_id,
            symbol=symbol,
            side=side,
            price=price,
            size=size,
            type=type,
            **kwargs,
        )
        return cast(SandboxOrderItem, order_item)

    def _create_execution_item(self, order_item: SandboxOrderItem) -> ExecutionItem:
        order_type = order_item["type"]
        if order_type == "LIMIT":
            price = order_item["price"]
        elif order_type == "MARKET":
            price = self._get_execution_price_for_market_order(order_item)
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        return self._store.execution._itemize(
            id=order_item["id"],
            symbol=order_item["symbol"],
            side=order_item["side"],
            price=price,
            size=order_item["size"],
            timestamp=pd.Timestamp.utcnow(),
        )

    def _create_position_item(
        self, execution_item: ExecutionItem
    ) -> PositionItem | None:
        positions = self._store.position.find({"symbol": execution_item["symbol"]})

        symbol = execution_item["symbol"]
        side = execution_item["side"]
        size = execution_item["size"]
        price = execution_item["price"]

        if len(positions) == 0:
            return self._store.position._itemize(
                symbol=symbol, side=side, price=price, size=float(size)
            )
        else:
            assert len(positions) == 1
            position_item = positions[0]
            n_side, n_size, n_price = self._compute_position_side_size_price(
                position_item, execution_item
            )
            if n_size is not None:
                return self._store.position._itemize(
                    symbol=symbol, side=n_side, price=n_price, size=n_size
                )
            else:
                return None

    def _compute_position_side_size_price(
        self, position_item: PositionItem, execution_item: ExecutionItem
    ) -> tuple[str | None, float | None, float | None]:
        e_side = execution_item["side"]
        e_price = Decimal(str(execution_item["price"]))
        e_size = Decimal(str(execution_item["size"]))
        p_side = position_item["side"]
        p_price = Decimal(str(position_item["price"]))
        p_size = Decimal(str(position_item["size"]))
        if position_item["side"] == execution_item["side"]:
            total_size = e_size + p_size
            avg_price = (e_price * e_size + p_price * p_size) / total_size
            return e_side, float(total_size), float(avg_price)
        else:
            remaining_size = p_size - e_size
            if remaining_size == 0:
                return None, None, None
            elif remaining_size > 0:
                return p_side, float(remaining_size), float(p_price)
            else:
                return e_side, float(abs(remaining_size)), float(e_price)

    def _get_execution_price_for_market_order(
        self, order_item: SandboxOrderItem
    ) -> float:
        # todo: 注文サイズ・スリッページの考慮
        asks, bids = self._store.orderbook.sorted().values()
        if order_item["side"] == "BUY":
            return asks[0]["price"]
        else:
            return bids[0]["price"]

    @classmethod
    def register(
        cls, store: DataStoreWrapper, api: APIWrapper
    ) -> tuple[SandboxDataStoreWrapper, SandboxAPIWrapper]:
        from .api_wrapper import SandboxAPIWrapper
        from .store_wrapper import SandboxDataStoreWrapper

        sandbox_store: SandboxDataStoreWrapper = SandboxDataStoreWrapper(store)
        sandbox_api = SandboxAPIWrapper(api)

        cls._REGISTRY[str(uuid.uuid4())] = SandboxEngine(sandbox_store, sandbox_api)

        return sandbox_store, sandbox_api
