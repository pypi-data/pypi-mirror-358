"""
Utility functions.
"""

import logging
import time
import os
import sys
import threading
from typing import List
from datetime import datetime
from functools import wraps
from mw_python_sdk.core import DatasetFile


# Rate-limiting decorator
def rate_limited(rate_limit_seconds: float):
    def decorator(func):
        last_called = [0.0]  # We store this as a mutable to track the last call time

        @wraps(func)
        def wrapper(filename, seen_so_far, size, *args, **kwargs):
            current_time = time.time()
            time_since_last_call = current_time - last_called[0]

            # Always print if we've reached the end (seen_so_far == size)
            if seen_so_far == size or time_since_last_call >= rate_limit_seconds:
                last_called[0] = current_time
                return func(filename, seen_so_far, size, *args, **kwargs)
            # Skip if within the rate limit
            return None

        return wrapper

    return decorator


# Create a logger for your library
logger = logging.getLogger(__name__)


def parse_datetime(date_string: str) -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        date_string (str): The datetime string to parse.

    Returns:
        datetime: A datetime object.

    """
    if date_string is None:
        return datetime.now()
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")


def convert_to_dataset_file(files) -> List[DatasetFile]:
    """
    将给定的文件列表转换为 DatasetFile 对象的列表。

    Args:
        files (List[Dict]): 文件列表，每个元素为字典类型，包含 "_id"、"Token"、"Size" 和 "SubPath" 等字段。

    Returns:
        List[DatasetFile]: 转换后的 DatasetFile 对象列表。

    """
    if files is None:
        return []
    dataset_files = [
        DatasetFile(
            file.get("_id"),
            file.get("Token"),
            file.get("Size"),
            "" if file.get("SubPath") is None else file.get("SubPath"),
        )
        for file in files
    ]
    return dataset_files


def generate_timestamped_string(revision: int) -> str:
    """
    Generates a timestamped string based on the current time and a revision number.

    :param revision: The revision number.
    :return: A timestamped string.
    """
    timestamp = int(time.time() * 1000)
    result = f"{timestamp}_{revision}"
    return result


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


@rate_limited(0.1)  # 10 calls per second
def print_percent(filename: str, seen_so_far: float, size: float):
    percentage = (seen_so_far / size) * 100
    sys.stdout.write(
        "\r%s %s / %s  (%.2f%%)    "
        % (
            filename,
            sizeof_fmt(seen_so_far),
            sizeof_fmt(size),
            percentage,
        )
    )
    sys.stdout.flush()


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r %s %s / %s  (%.2f%%)    "
                % (
                    self._filename,
                    sizeof_fmt(self._seen_so_far),
                    sizeof_fmt(self._size),
                    percentage,
                )
            )
            sys.stdout.flush()
