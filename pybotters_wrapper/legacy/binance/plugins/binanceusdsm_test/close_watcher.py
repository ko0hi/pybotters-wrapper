from __future__ import annotations

import asyncio

from ....core.store import DataStoreWrapper, OrderItem
from ....plugins import Plugin
from ....plugins.mixins import WatchStoreMixin


class CloseWatcher(WatchStoreMixin, Plugin):
    def __init__(self, store: "DataStoreWrapper"):
        # OrderStoreを監視
        self.init_watch_store(store.order)
        self._order_id = None
        self._item = None
        self._done = None
        self._status = None
        self._event = asyncio.Event()

    def set(self, order_id: str) -> CloseWatcher:
        """監視対象の注文IDをセット"""
        if self._order_id is not None:
            raise RuntimeError(
                "CancelWatcher must not be 'reused', create a new instance instead."
            )
        self._order_id = order_id
        self._status = 'OPEN'
        self._event.set()
        return self

    async def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        """open orderが約定したかチェック
        OPEN: idがopen
        FILLED: openなidが約定
        CANCEL: openなidがcancel
        CLOSE: idが最初からopenでない
        """
        if not self._event.is_set():
            # order_idがsetされるまで待機
            # 注文が即約定した時にsocket messageがresのresponseより早く到達するケースがあるので、
            # order_idがセットされるまでメッセージをここで待機させておく
            await self._event.wait()
        if len(self.watch_store.find({'id': self._order_id})) == 0 and operation != 'delete':
            self._done = True
            self._status = 'CLOSE'
            self.set_break()
        if data["id"] == self._order_id and operation == 'delete':  # なくなったらexecuted or cancelと判断
            if (source['info']['source']['X'] == 'FILLED'):
                self._done = True
                self._item = data
                self._status = 'FILLED'
                self.set_break()
            else:  # cancel
                self._done = True
                self._item = data
                self._status = 'CANCEL'
                self.set_break()

    @property
    def status(self):
        return self._status

    def _on_watch_is_stop(self, store: "DataStore", operation: str, source: dict, data: dict) -> bool:
        """監視終了判定"""
        return self._done

    def done(self) -> bool:
        return self._done

    def result(self) -> OrderItem:
        return self._item

    async def wait(self):
        return await self.watch_task

    @property
    def order_id(self) -> str:
        return self._order_id
