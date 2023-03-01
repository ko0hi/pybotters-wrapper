from __future__ import annotations

import asyncio
from typing import Callable

from loguru import logger
from pybotters.store import DataStore, StoreChange


def _is_aw(fn: Callable) -> bool:
    return asyncio.iscoroutinefunction(fn)


@logger.catch
async def _run_hook(is_aw: bool, fn: Callable, *args) -> any:
    if is_aw:
        return await fn(*args)
    else:
        return fn(*args)


class Plugin:
    ...
