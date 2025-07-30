"""
Hestia Logger - Request Logger.

Logs HTTP request and response details for API-based applications.
Supports FastAPI, Flask, and other web frameworks.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import os
from ..core.custom_logger import JSONFormatter
from ..handlers.console_handler import console_handler  # Use global handler

# Initialize request logger
requests_logger = logging.getLogger("hestia_requests")

# Load log level from environment variable
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL_STR = os.getenv("REQUESTS_LOG_LEVEL", "INFO").upper()
LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_STR, logging.INFO)
requests_logger.setLevel(LOG_LEVEL)

# Use global console handler instead of redefining one
requests_logger.addHandler(console_handler)

# Use JSON formatting for structured logging
json_formatter = JSONFormatter()
file_handler = logging.FileHandler("logs/requests.log")
file_handler.setFormatter(json_formatter)
requests_logger.addHandler(file_handler)

# Prevent log duplication
requests_logger.propagate = False
