from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters_wrapper.core.store import (
        TradesItem,
        OrderItem,
        ExecutionItem,
        PositionItem,
    )
    from pybotters_wrapper.sandbox import SandboxAPI, SandboxDataStoreWrapper

from pybotters_wrapper.core import API, DataStoreWrapper
from pybotters_wrapper.utils.mixins import LoggingMixin


class SandboxEngine(LoggingMixin):
    SUFFIX = ".sandbox"
    _REGISTRY: dict[str, SandboxEngine] = {}

    def __init__(self, store: SandboxDataStoreWrapper, api: SandboxAPI):
        self._store = store
        self._api = api

        self._task = asyncio.create_task(self._matching_task())

        # store/apiから当該エンジンにアクセスできるよう参照設定
        self._store._link_to_engine(self)
        self._api._link_to_engine(self)

    def insert_order(
        self, symbol: str, side: str, price: float, size: float, type: str
    ) -> str:
        order_item = self._create_order_item(symbol, side, price, size, type)
        self._store.order._insert([order_item])
        self.log(f"new order: {order_item}")

        if type == "MARKET":
            self._handle_execution(order_item)

        return order_item["id"]

    def delete_order(self, symbol: str, order_id: str) -> None:
        order_item = self._store.order.find({"symbol": symbol, "id": order_id})
        if len(order_item) == 0:
            raise RuntimeError(
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

    def _is_executed(self, order_item: OrderItem, trade_item: TradesItem) -> bool:
        if order_item["symbol"] != trade_item["symbol"]:
            return False

        if order_item["side"] == "BUY":
            return order_item["price"] >= trade_item["price"]
        else:
            return order_item["price"] <= trade_item["price"]

    def _handle_execution(self, order_item: OrderItem) -> None:
        self.log(f"handle execution")

        # 約定履歴の挿入
        execution_item = self._create_execution_item(order_item)
        self._store.execution._insert([execution_item])
        self.log(f"insert execution: {execution_item}")

        # ポジション状態のアップデート
        # one-side only
        position_item = self._create_position_item(execution_item)
        if position_item is not None:
            position = self._store.position.find({"symbol": order_item["symbol"]})
            self._store.position._clear()
            self._store.position._insert([position_item])
            self.log(f"update position: {position} => [{position_item}]")

        # 注文の削除
        self._store.order._delete([order_item])
        self.log(f"delete order: {order_item}")

    def _create_order_item(
        self, symbol: str, side: str, price: float, size: float, type: str
    ) -> OrderItem:
        order_id = str(uuid.uuid4())
        order_item = self._store.order._itemize(
            order_id, symbol, side, price, size, type
        )
        return order_item

    def _create_execution_item(self, order_item: OrderItem) -> ExecutionItem:
        order_type = order_item["type"]
        if order_type == "LIMIT":
            price = order_item["price"]
        elif order_type == "MARKET":
            price = self._get_execution_price_for_market_order(order_item)
        else:
            raise RuntimeError(f"Unsupported order type: {order_type}")

        return self._store.execution._itemize(
            order_item["id"],
            order_item["symbol"],
            order_item["side"],
            price,
            order_item["size"],
            datetime.utcnow(),
        )

    def _create_position_item(self, execution_item: ExecutionItem) -> PositionItem:
        positions = self._store.position.find({"side": execution_item["side"]})

        symbol = execution_item["symbol"]
        side = execution_item["side"]
        price = execution_item["price"]
        size = execution_item["size"]

        if len(positions) == 0:
            position_item = self._store.position._itemize(
                symbol, side, price, float(size)
            )
        else:
            assert len(positions) == 1
            position = positions[0]
            if position["side"] == execution_item["side"]:
                total_size = size + position["size"]
                avg_price = (
                    price * size + position["price"] * position["size"]
                ) / total_size
                position_item = self._store.position._itemize(
                    symbol, side, avg_price, total_size
                )
            else:
                remaining_size = position["size"] - size
                if remaining_size == 0:
                    position_item = None
                elif remaining_size > 0:
                    position_item = self._store.position._itemize(
                        symbol, side, position["price"], remaining_size
                    )
                else:
                    rev_side = "SELL" if side == "BUY" else "BUY"
                    position_item = self._store.position._itemize(
                        symbol,
                        rev_side,
                        price,
                        abs(remaining_size),
                    )

        return position_item

    def _get_execution_price_for_market_order(self, order_item: OrderItem) -> float:
        # todo: 注文サイズ・スリッページの考慮
        asks, bids = self._store.orderbook.sorted().values()
        if order_item["side"] == "BUY":
            return asks[0]["price"]
        else:
            return bids[0]["price"]

    @classmethod
    def register(
        cls, store: DataStoreWrapper, api: API
    ) -> tuple[SandboxDataStoreWrapper, SandboxAPI]:

        if store.exchange in cls._REGISTRY:
            engine = cls._REGISTRY[store.exchange]
            return engine._store, engine._api

        from .api import SandboxAPI
        from .store import SandboxDataStoreWrapper

        sandbox_store = SandboxDataStoreWrapper(store)
        sandbox_api = SandboxAPI(api)

        cls._REGISTRY[store.exchange] = SandboxEngine(sandbox_store, sandbox_api)

        return sandbox_store, sandbox_api
