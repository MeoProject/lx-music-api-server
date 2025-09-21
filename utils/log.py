import os
import logging
from rich.logging import RichHandler

from server.variable import output_logs, debug


def createLogger(name: str) -> logging.Logger:
    os.makedirs("./logs", exist_ok=True)

    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    logger = logging.getLogger(name)

    if output_logs:
        logfile = f"./logs/{name}.log"
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] | [%(name)s:%(levelname)s] | [%(module)s.%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
