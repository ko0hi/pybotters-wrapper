import asyncio
from collections import deque
from typing import Callable
from loguru import logger

from .._base import Plugin


class PeriodicPlugin(Plugin):
    def __init__(
        self,
        fn: Callable,
        params: dict | Callable = None,
        interval: int = 10,
        handler: Callable = None,
        history: int = 999,
    ):
        super(PeriodicPlugin, self).__init__()
        self._fn = fn
        self._params = params
        self._interval = interval
        self._handle = handler
        self._is_coro_fn = asyncio.iscoroutinefunction(self._fn)
        self._is_coro_params = asyncio.iscoroutinefunction(self._params)
        self._is_coro_handler = asyncio.iscoroutinefunction(self._handle)
        self._task = asyncio.create_task(self._periodic_execute())
        self._history = deque(maxlen=history)

    async def execute(self):
        params = await self._get_params()
        item = await self._call(params)
        item = await self._handle(item)
        self._history.append(item)
        self.put(item)

    @logger.catch
    async def _execute(self):
        """_periodic_executeでexceptionをcatchするためのwrapper"""
        await self.execute()

    async def _periodic_execute(self):
        while True:
            await self._execute()
            await asyncio.sleep(self._interval)

    async def _get_params(self) -> dict:
        if self._params is None:
            return {}
        elif isinstance(self._params, dict):
            return self._params
        elif callable(self._fn):
            if self._is_coro_params:
                return await self._params()
            else:
                return self._params()
        else:
            raise RuntimeError(
                "Unsupported params type: should be either of None, dict, or Callable."
            )

    async def _call(self, params: dict) -> any:
        if self._is_coro_fn:
            return await self._fn(**params)
        else:
            return self._fn(**params)

    async def _handle(self, item: any) -> any:
        if self._handle is None:
            return item
        else:
            if self._is_coro_handler:
                return await self._handle(item)
            else:
                return self._handle(item)

    def stop(self):
        self._task.cancel()

    @property
    def task(self) -> asyncio.Task:
        return self._task

    @property
    def history(self) -> list[any]:
        return self._history

    @property
    def last(self) -> any:
        try:
            return self._history[-1]
        except IndexError:
            return None
