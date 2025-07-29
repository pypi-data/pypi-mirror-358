"""
logger.py

Creates a logger object that logs to a file.

Usage:
    from util.logger import setup_logger

    logger = setup_logger(name=__name__)
"""

from logging import DEBUG, FileHandler, Formatter, Logger, getLogger
from os import mkdir, path

LOG_DIR = "./logs"
LOG_FILE = "log.txt"

if not path.exists(path=LOG_DIR):
    mkdir(path=LOG_DIR)


def setup_logger(name: str, level: int = DEBUG) -> Logger:
    """
    Creates a logger object that logs to a file.

    Attributes:
        name (str): The name of the logger.
        level (int): The level of the logger.
    """
    logger: Logger = getLogger(name=name)
    logger.setLevel(level=level)

    # Create file handler which logs messages
    file_handler = FileHandler(filename=path.join(LOG_DIR, LOG_FILE))
    file_handler.setLevel(level=DEBUG)
    # Create formatter and add it to the handler
    formatter = Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(fmt=formatter)

    # Add the handlers to the logger
    if (
        not logger.handlers
    ):  # To avoid adding handlers multiple times in some environments
        logger.addHandler(hdlr=file_handler)
    return logger
