import sys
from loguru import logger

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level:<8}</level> | "
    "<level>{message}</level>"
)

LOG_FORMAT_WITH_ICON = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level.icon:<1}{level:<8}</level> | "
    "<level>{message}</level>"
)


def init_logger(
    logfile=None, enable_icon=False, retention=3, rotation="10MB", **kwargs
):
    logger.remove(0)
    fmt = LOG_FORMAT_WITH_ICON if enable_icon else LOG_FORMAT
    logger.add(sys.stderr, format=fmt, **kwargs)

    if logfile:
        logger.add(
            logfile, format=fmt, retention=retention, rotation=rotation, **kwargs
        )

    return logger


init_logger()


class LoggingMixin:
    def log(self, msg, level="debug"):
        getattr(logger, level)(f"[{self.__class__.__name__}] {msg}")

