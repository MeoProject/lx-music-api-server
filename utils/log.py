import os
import logzero
import logging
from logging import Logger
from logzero import setup_logger, LogFormatter

from server.variable import output_logs, debug


def createLogger(name: str) -> Logger:
    os.makedirs("./logs", exist_ok=True)

    if debug:
        level = logzero.DEBUG
    else:
        level = logzero.INFO

    terminal_formatter = LogFormatter(
        color=True,
        fmt="%(color)s%(asctime)s %(message)s%(end_color)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = setup_logger(name, level=level, formatter=terminal_formatter)

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
