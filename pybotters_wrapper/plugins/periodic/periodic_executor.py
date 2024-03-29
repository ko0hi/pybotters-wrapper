from __future__ import annotations

import asyncio
from collections import deque
from typing import Any, Callable

from loguru import logger

from ..base_plugin import Plugin
from ..mixins import PublishQueueMixin


class PeriodicExecutor(PublishQueueMixin, Plugin):
    def __init__(
        self,
        fn: Callable,
        params: dict | Callable | None = None,
        interval: int | float = 10,
        handler: Callable | None = None,
        history: int = 999,
    ):
        super(PeriodicExecutor, self).__init__()
        self._fn = fn
        self._params = params
        self._interval = interval
        self._handler = handler
        self._is_coro_fn = asyncio.iscoroutinefunction(self._fn)
        self._is_coro_params = asyncio.iscoroutinefunction(self._params)
        self._is_coro_handler = asyncio.iscoroutinefunction(self._handler)
        self._task = asyncio.create_task(self._periodic_execute())
        self._history: deque = deque(maxlen=history)
        self.init_publish_queue()

    async def execute(self):
        params = await self._get_params()
        item = await self._call(params)
        item = await self._handle(item)
        self._history.append(item)
        self.put(item)

    async def _periodic_execute(self):
        while True:
            try:
                await self.execute()
            except Exception as e:
                logger.error(f"Polling error: {e}")
            await asyncio.sleep(self._interval)

    async def _get_params(self) -> dict:
        if self._params is None:
            return {}
        elif isinstance(self._params, dict):
            return self._params
        elif callable(self._params):
            if self._is_coro_params:
                return await self._params()
            else:
                return self._params()
        else:
            raise RuntimeError(
                "Unsupported params type: should be either of None, dict, or Callable."
            )

    async def _call(self, params: dict) -> Any:
        if self._is_coro_fn:
            return await self._fn(**params)
        else:
            return self._fn(**params)

    async def _handle(self, item: Any) -> Any:
        if self._handler is None:
            return item
        else:
            if self._is_coro_handler:
                return await self._handler(item)
            else:
                return self._handler(item)

    def stop(self):
        self._task.cancel()

    @property
    def task(self) -> asyncio.Task:
        return self._task

    @property
    def history(self) -> deque[Any]:
        return self._history

    @property
    def last(self) -> Any:
        try:
            return self._history[-1]
        except IndexError:
            return None
