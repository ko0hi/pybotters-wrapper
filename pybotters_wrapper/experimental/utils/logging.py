from __future__ import annotations

import json
import os
import sys
from datetime import datetime

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


def init_logdir(*subdirs: str):
    import __main__

    subdirs = list(map(str, subdirs))

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
    logfile=None, enable_icon=False, retention=3, rotation="10MB", **kwargs
):
    [logger.remove(h) for h in logger._core.handlers]

    fmt = LOG_FORMAT_WITH_ICON if enable_icon else LOG_FORMAT
    logger.add(sys.stderr, format=fmt, **kwargs)

    if logfile:
        logger.add(
            logfile, format=fmt, retention=retention, rotation=rotation, **kwargs
        )

    return logger


init_logger()


def log_command_args(
    logdir: str, args: "argparse.Namespace", filename: str = "args.json"
):
    with open(os.path.join(logdir, filename), "w") as f:
        json.dump(vars(args), f, indent=4)
