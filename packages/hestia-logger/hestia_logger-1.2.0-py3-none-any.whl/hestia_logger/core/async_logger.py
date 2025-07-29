"""
HESTIA Logger - Async Logger.

This module provides optional async logging for specific use cases where
thread-based logging might not be suitable.

Currently, HESTIA Logger defaults to thread-based logging. If async logging
is required, this module can be extended.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import asyncio
import aiofiles
import json
from ..internal_logger import hestia_internal_logger
from ..core.custom_logger import JSONFormatter

__all__ = ["AsyncFileLogger"]

import logging
import asyncio
import aiofiles
import json
from ..internal_logger import hestia_internal_logger
from ..core.custom_logger import JSONFormatter

__all__ = ["AsyncFileLogger"]


class AsyncFileLogger(logging.Handler):
    """
    Asynchronous file logger for specialized use cases.

    This class is experimental and can be used if high-throughput, non-blocking
    logging is required. It now includes an asyncio lock to ensure thread/async
    safety when multiple loggers write concurrently to the same file.

    Example Use:
        logger = AsyncFileLogger("async_app.log")
        logging.getLogger("async_test").addHandler(logger)
    """

    def __init__(self, log_file: str):
        super().__init__()
        self.log_file = log_file
        self.formatter = JSONFormatter()  # Use the same JSON formatter
        self._lock = asyncio.Lock()  # Lock to ensure safe concurrent writes

    async def _write_log(self, message):
        """
        Writes log messages asynchronously to the file.
        The asyncio lock ensures that concurrent writes are serialized.
        """
        try:
            async with self._lock:
                async with aiofiles.open(
                    self.log_file, mode="a", encoding="utf-8"
                ) as f:
                    await f.write(message + "\n")
                    await f.flush()
            hestia_internal_logger.debug(
                f"✅ Successfully wrote log to {self.log_file}."
            )
        except Exception as e:
            hestia_internal_logger.error(
                f"❌ ERROR WRITING TO FILE {self.log_file}: {e}"
            )

    def emit(self, record):
        """
        Formats log records and ensures `_write_log()` runs asynchronously.
        If there is no running loop, falls back to asyncio.run.
        """
        try:
            log_entry = self.format(record)

            # Ensure valid JSON before writing
            if isinstance(log_entry, str):
                log_entry = json.loads(log_entry)

            loop = asyncio.get_running_loop()
            loop.create_task(self._write_log(json.dumps(log_entry, ensure_ascii=False)))
        except RuntimeError:
            # Fallback if no running loop exists
            asyncio.run(self._write_log(json.dumps(log_entry, ensure_ascii=False)))
        except Exception as e:
            hestia_internal_logger.error(f"❌ ERROR IN `emit()`: {e}")
