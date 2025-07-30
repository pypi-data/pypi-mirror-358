import datetime
import json
import logging
import os
import sys
from typing import Any


def get_current_datetime_now(
    timezone: datetime.timezone = datetime.timezone.utc,
) -> datetime.datetime:
    return datetime.datetime.now(timezone)


def open_file(path: str):
    return open(file=path, mode="r", encoding="utf-8")


def open_file_as_json(path: str) -> dict[str, Any]:
    with open_file(path) as file:
        return json.load(file)


def open_file_as_text(path: str):
    with open_file(path) as file:
        return file.read().strip()


def get_directory_name(path: str):
    """
    Get the directory name from the given path.
    This is a wrapper function for `os.path.dirname` and
    will return the directory name of the given path. (e.g. /path/to/file.txt -> /path/to)

    **Note**: This function using `os.path.realpath` to get the real path of the given path.

    Args:
        path (str): The path to get the directory name.
    """
    return os.path.dirname(os.path.realpath(path))


def get_logger_with_stdout_handler(
    name: str,
    format: str,
    level: int = logging.INFO,
) -> logging.Logger:
    formatter = logging.Formatter(format)

    handler = logging.StreamHandler(sys.stdout)
    handler.name = "stdout_handler"
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if handler.name not in [h.name for h in logger.handlers]:
        logger.addHandler(handler)

    return logger
