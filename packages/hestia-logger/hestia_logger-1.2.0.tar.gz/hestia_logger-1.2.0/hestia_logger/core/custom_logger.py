"""
HESTIA Logger - Custom Logger.

Defines a structured logger with thread-based asynchronous logging.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

# custom_logger.py
import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from ..internal_logger import hestia_internal_logger
from ..handlers import console_handler
from ..core.formatters import JSONFormatter
from ..core.config import (
    LOGS_DIR,
    LOG_LEVEL,
    LOG_ROTATION_TYPE,
    LOG_ROTATION_WHEN,
    LOG_ROTATION_INTERVAL,
    LOG_ROTATION_BACKUP_COUNT,
    LOG_ROTATION_MAX_BYTES,
    ENABLE_INTERNAL_LOGGER,
    LOG_FILE_PATH_APP,
)

# Global dictionary to track loggers
_LOGGERS = {}
_APP_LOG_HANDLER = None  # Ensure `app.log` is only attached once
_RESERVED_APP_NAME = "app"  # Reserved logger name


def get_logger(name: str, metadata: dict = None, log_level=None, internal=False):
    """
    Returns a structured logger for a specific service/module.
    - Ensures `app.log` is always available internally.
    - Prevents duplicate logger creation.
    """
    global _LOGGERS, _APP_LOG_HANDLER

    if name == _RESERVED_APP_NAME and not internal:
        raise ValueError(
            f'"{_RESERVED_APP_NAME}" is a reserved logger name and cannot be used directly.'
        )

    if name in _LOGGERS:
        return _LOGGERS[name]  # Prevent duplicate logger creation

    log_level = log_level or LOG_LEVEL
    service_log_file = os.path.join(LOGS_DIR, f"{name}.log")

    # Ensure `app.log` JSON handler is always initialized FIRST
    if _APP_LOG_HANDLER is None:
        json_formatter = JSONFormatter()
        _APP_LOG_HANDLER = RotatingFileHandler(
            LOG_FILE_PATH_APP,
            maxBytes=LOG_ROTATION_MAX_BYTES,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )
        _APP_LOG_HANDLER.setFormatter(json_formatter)
        _APP_LOG_HANDLER.setLevel(logging.DEBUG)
        _APP_LOG_HANDLER.flush = lambda: _APP_LOG_HANDLER.stream.flush()
        print("[DEBUG] Attached JSON handler to app.log and enabled flushing.")

        # Create the 'app' logger with the JSON handler attached
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.DEBUG)
        app_logger.addHandler(_APP_LOG_HANDLER)
        _LOGGERS["app"] = app_logger

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # Prevent log duplication

    if name != "app":
        # Human-friendly per-service log handler.
        service_handler = RotatingFileHandler(
            service_log_file,
            maxBytes=LOG_ROTATION_MAX_BYTES,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )
        service_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        service_handler.setLevel(log_level)
        logger.addHandler(service_handler)
        # Attach the centralized JSON handler.
        logger.addHandler(_APP_LOG_HANDLER)

    # Instead of setting metadata as an attribute, wrap the logger in a LoggerAdapter.
    from logging import LoggerAdapter
    from ..core.config import ENVIRONMENT, HOSTNAME, APP_VERSION

    # Set default metadata
    default_metadata = {
        "environment": ENVIRONMENT,
        "hostname": HOSTNAME,
        "app_version": APP_VERSION,
    }
    if metadata:
        default_metadata.update(metadata)

    adapter = LoggerAdapter(logger, {"metadata": default_metadata})
    _LOGGERS[name] = adapter
    return adapter


def apply_logging_settings():
    """
    Applies `LOG_LEVEL` settings to all handlers and ensures correct formatting.
    """
    logging.root.handlers = []
    logging.root.setLevel(LOG_LEVEL)
    console_handler.setLevel(LOG_LEVEL)

    color_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(color_formatter)

    logging.root.addHandler(console_handler)

    for handler in logging.root.handlers:
        handler.flush = lambda: handler.stream.flush()

    if hasattr(hestia_internal_logger, "setLevel"):
        hestia_internal_logger.setLevel(LOG_LEVEL)

    if hasattr(hestia_internal_logger, "disabled"):
        hestia_internal_logger.disabled = not ENABLE_INTERNAL_LOGGER

    if hasattr(hestia_internal_logger, "info") and LOG_LEVEL <= logging.INFO:
        hestia_internal_logger.info(f"Applied LOG_LEVEL: {LOG_LEVEL}")
        hestia_internal_logger.info(f"ENABLE_INTERNAL_LOGGER: {ENABLE_INTERNAL_LOGGER}")


apply_logging_settings()
