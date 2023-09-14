from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable, cast

if TYPE_CHECKING:
    from pybotters.store import DataStore

from ...core import DataStoreWrapper, ExecutionItem
from ..base_plugin import Plugin
from ..mixins import WatchStoreMixin


class ExecutionWatcher(WatchStoreMixin, Plugin):
    def __init__(
        self,
        store: DataStoreWrapper,
        *,
        store_name: str | None = None,
        is_target: Callable[[DataStore, str, dict, dict], bool] | None = None,
    ):
        # ExecutionDataStoreを監視
        self._order_id: str | None = None
        self._item: ExecutionItem | None = None
        self._done: bool = False
        self._event: asyncio.Event = asyncio.Event()
        self._is_target_fn = is_target

        self.init_watch_store(getattr(store, store_name or "execution"))

    def set(self, order_id: str | None = None) -> ExecutionWatcher:
        """監視対象の注文IDをセット"""
        if self._order_id is not None:
            raise RuntimeError(
                "ExecutionWatcher must not be 'reused', create a new instance instead."
            )
        self._order_id = order_id
        self._event.set()
        return self

    async def _on_watch(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        """流れてきた約定情報が監視中の注文に関するものであるかをチェック

        ExecutionStoreを監視してるので、流れてくるdictはExecutionItem

        """
        if not self._event.is_set():
            # order_idがsetされるまで待機
            # 注文が即約定した時にsocket messageがresのresponseより早く到達するケースがあるので、
            # order_idがセットされるまでメッセージをここで待機させておく
            await self._event.wait()

        if self._is_target(store, operation, source, data):
            self._done = True
            self._item = cast(ExecutionItem, data)
            self.set_break()

    def _is_target(self, store: "DataStore", operation: str, source: dict, data: dict):
        if self._is_target_fn:
            return self._is_target_fn(store, operation, source, data)
        else:
            return data["id"] == self._order_id

    def done(self) -> bool:
        return self._done

    def result(self) -> ExecutionItem | None:
        return self._item

    async def wait(self):
        return await self.watch_task

    @property
    def order_id(self) -> str | None:
        return self._order_id
