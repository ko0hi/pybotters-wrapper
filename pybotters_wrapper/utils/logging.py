import os
import sys
from datetime import datetime

from loguru import logger

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level:<8}</level> | "
    "<level>{message}</level> ("
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>)"
)


def init_logdir(*subdirs: str) -> str:
    import __main__

    # /logs/<script_name>/<subdirs1>/<subdirs2>/.../<datetime>
    logdir = os.path.join(
        os.getcwd(),
        "logs",
        os.path.basename(__main__.__file__).replace(".py", ""),
        *subdirs,
        datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
    )
    os.makedirs(logdir, exist_ok=True)
    return logdir


def init_logger(
    logfile: str | None = None,
    retention: int = 3,
    rotation: str = "10MB",
    format: str | None = None,
    **kwargs
) -> None:
    """loguruのloggerを初期化する。"""
    format = format or LOG_FORMAT
    [logger.remove(h) for h in logger._core.handlers]  # type: ignore
    logger.add(sys.stderr, format=format, **kwargs)
    if logfile:
        logger.add(
            logfile, format=format, retention=retention, rotation=rotation, **kwargs
        )
